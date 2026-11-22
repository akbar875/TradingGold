"""Local XAUUSD M15 machine-learning confirmation for Aurum MT5 EA.

The Python process NEVER sends orders. It only writes a timestamped prediction.
Orders, hard stops, and risk limits live in the MQL5 EA.
Install on Windows with MetaTrader 5 desktop running and logged in.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score

MODEL_VERSION = 2
HORIZON = 8           # Future M15 candles for training label only
BARRIER_ATR = 1.50    # Symmetric threshold; a model class does not imply RR=1:1
MIN_TRAIN_BARS = 2200
MIN_AI_PROBABILITY = 0.62
MIN_AI_EDGE = 0.15
RETRAIN_EVERY_DAYS = 7
FEATURE_COLUMNS = [
    "ret1", "ret3", "ret6", "ret12", "ema20_gap_atr", "ema50_gap_atr",
    "ema_slope_atr", "rsi", "macd_hist_atr", "atr_pct", "body_atr",
    "upper_wick_atr", "lower_wick_atr", "range_atr", "adx_proxy",
    "volume_rel", "spread_to_atr", "position_12", "hour_sin", "hour_cos",
]


def build_features(rates: pd.DataFrame) -> pd.DataFrame:
    """Causal features: each row uses only itself and older bars."""
    frame = rates.copy().sort_values("time").reset_index(drop=True)
    c = frame["close"].astype(float)
    o = frame["open"].astype(float)
    h = frame["high"].astype(float)
    lo = frame["low"].astype(float)
    t = pd.to_datetime(frame["time"], unit="s", utc=True)
    prev = c.shift(1)
    true_range = pd.concat([(h-lo), (h-prev).abs(), (lo-prev).abs()], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1/14, adjust=False, min_periods=14).mean().clip(lower=1e-10)
    ema20 = c.ewm(span=20, adjust=False, min_periods=20).mean()
    ema50 = c.ewm(span=50, adjust=False, min_periods=50).mean()
    ema12 = c.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = c.ewm(span=26, adjust=False, min_periods=26).mean()
    macd = ema12-ema26
    macd_signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    delta = c.diff()
    up = delta.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rsi = (100.0-100.0/(1+up/down.replace(0, np.nan))).fillna(50.0)
    vol = frame["tick_volume"].astype(float)
    high12 = h.rolling(12, min_periods=12).max()
    low12 = lo.rolling(12, min_periods=12).min()
    diff = (high12-low12).replace(0, np.nan)
    output = pd.DataFrame({
        "time": frame["time"].astype("int64"),
        "atr": atr,
        "ret1": c.pct_change(1),
        "ret3": c.pct_change(3),
        "ret6": c.pct_change(6),
        "ret12": c.pct_change(12),
        "ema20_gap_atr": (c-ema20)/atr,
        "ema50_gap_atr": (c-ema50)/atr,
        "ema_slope_atr": (ema20-ema20.shift(3))/atr,
        "rsi": rsi/100,
        "macd_hist_atr": (macd-macd_signal)/atr,
        "atr_pct": atr/c,
        "body_atr": (c-o)/atr,
        "upper_wick_atr": (h-np.maximum(o,c))/atr,
        "lower_wick_atr": (np.minimum(o,c)-lo)/atr,
        "range_atr": (h-lo)/atr,
        # Trend-strength proxy; NOT the Wilder ADX indicator.
        "adx_proxy": (ema20-ema50).abs()/atr,
        "volume_rel": vol/vol.rolling(20, min_periods=20).mean().replace(0,np.nan),
        "spread_to_atr": frame.get("spread_price", frame["spread"].astype(float)*0.01)/atr,
        "position_12": (c-low12)/diff,
        "hour_sin": np.sin(2*np.pi*t.dt.hour/24),
        "hour_cos": np.cos(2*np.pi*t.dt.hour/24),
    })
    return output.replace([np.inf,-np.inf], np.nan)


def triple_barrier_labels(rates: pd.DataFrame, feats: pd.DataFrame) -> pd.Series:
    """Training labels only. Unknown intrabar hit order => WAIT class 0."""
    frame = rates.sort_values("time").reset_index(drop=True)
    close = frame["close"].to_numpy(dtype=float)
    hi = frame["high"].to_numpy(dtype=float)
    low = frame["low"].to_numpy(dtype=float)
    atr = feats["atr"].to_numpy(dtype=float)
    result = np.full(len(frame), np.nan)
    for idx in range(len(frame)-HORIZON):
        if not np.isfinite(atr[idx]) or atr[idx] <= 0:
            continue
        upper = close[idx] + BARRIER_ATR*atr[idx]
        lower = close[idx] - BARRIER_ATR*atr[idx]
        target = 0
        for future in range(idx+1,idx+HORIZON+1):
            hit_buy = hi[future]>=upper
            hit_sell = low[future]<=lower
            if hit_buy and hit_sell:
                target=0
                break
            if hit_buy:
                target=1
                break
            if hit_sell:
                target=-1
                break
        result[idx]=target
    return pd.Series(result, dtype=float)


def training_table(rates: pd.DataFrame) -> pd.DataFrame:
    f = build_features(rates)
    f["target"] = triple_barrier_labels(rates, f)
    return f.dropna(subset=FEATURE_COLUMNS+["target"]).reset_index(drop=True)


def class_prob(model: RandomForestClassifier, features: pd.DataFrame) -> dict[int, np.ndarray]:
    raw=model.predict_proba(features[FEATURE_COLUMNS])
    return {int(c):raw[:, idx] for idx,c in enumerate(model.classes_)}


def choose_signal(model: RandomForestClassifier, row: pd.DataFrame) -> tuple[str,float,float,float]:
    p=class_prob(model,row)
    buy=float(p.get(1,np.array([0.0]))[0])
    sell=float(p.get(-1,np.array([0.0]))[0])
    wait=float(p.get(0,np.array([0.0]))[0])
    action="WAIT"
    if buy>=MIN_AI_PROBABILITY and buy-sell>=MIN_AI_EDGE:
        action="BUY"
    elif sell>=MIN_AI_PROBABILITY and sell-buy>=MIN_AI_EDGE:
        action="SELL"
    return action,buy,sell,wait


def fit_and_evaluate(rates: pd.DataFrame) -> tuple[RandomForestClassifier, dict]:
    df=training_table(rates)
    if len(df)<MIN_TRAIN_BARS:
        raise RuntimeError(f"History berlabel hanya {len(df)}; perlu minimal {MIN_TRAIN_BARS}")
    cut=int(len(df)*0.8)
    train=df.iloc[:cut-HORIZON]
    test=df.iloc[cut:]
    if train["target"].nunique()<3:
        raise RuntimeError("Tiga kelas sinyal belum tersedia pada data training")
    kwargs=dict(n_estimators=240,max_depth=9,min_samples_leaf=15,
                class_weight="balanced_subsample",random_state=42,n_jobs=-1)
    checker=RandomForestClassifier(**kwargs)
    checker.fit(train[FEATURE_COLUMNS],train["target"].astype(int))
    y=test["target"].astype(int)
    yhat=checker.predict(test[FEATURE_COLUMNS])
    probs=class_prob(checker,test)
    pb=probs.get(1,np.zeros(len(test)))
    ps=probs.get(-1,np.zeros(len(test)))
    long_mask=(pb>=MIN_AI_PROBABILITY)&((pb-ps)>=MIN_AI_EDGE)
    short_mask=(ps>=MIN_AI_PROBABILITY)&((ps-pb)>=MIN_AI_EDGE)
    signaled=(long_mask|short_mask)
    signal_correct=(long_mask&(y.to_numpy()==1)) | (short_mask&(y.to_numpy()==-1))
    report={
        "model":"RandomForestClassifier (three-class: BUY / SELL / WAIT)",
        "data_bars":len(df),
        "train_bars":len(train),
        "holdout_bars":len(test),
        "holdout_accuracy":round(float(accuracy_score(y,yhat)),4),
        "holdout_balanced_accuracy":round(float(balanced_accuracy_score(y,yhat)),4),
        "holdout_signal_count":int(signaled.sum()),
        "holdout_signal_coverage":round(float(signaled.mean()),4),
        "holdout_signal_directional_precision":(
            round(float(signal_correct.sum()/signaled.sum()),4) if signaled.any() else None
        ),
        "label_definition":f"First symmetric +/-{BARRIER_ATR} ATR hit within {HORIZON} candles; both hit -> WAIT",
        "warning":"Historical classification only. NOT realized trading P/L, NOT a win rate or calibrated probability.",
        "evaluated_at_utc":datetime.now(timezone.utc).isoformat(),
    }
    # Fit final model on all historical LABELLED candles, after out-of-sample evaluation.
    model=RandomForestClassifier(**kwargs)
    model.fit(df[FEATURE_COLUMNS],df["target"].astype(int))
    return model,report


def model_path(symbol: str,account: int) -> Path:
    root=Path(__file__).resolve().parent/"models"
    root.mkdir(exist_ok=True)
    clean="".join(c if c.isalnum() else "_" for c in symbol)
    return root/f"AurumAI_{account}_{clean}_M15.joblib"


def get_model(rates:pd.DataFrame, symbol:str,account:int):
    path=model_path(symbol,account)
    need_train=True
    if path.exists():
        bundle=joblib.load(path)  # Load ONLY local file created by this script.
        if (bundle.get("version")==MODEL_VERSION and
            bundle.get("last_train_time",0)+RETRAIN_EVERY_DAYS*86400>time.time()):
            need_train=False
    if need_train:
        print("[AI] Melatih model dari riwayat MT5 dan mengevaluasi holdout kronologis...")
        model,report=fit_and_evaluate(rates)
        bundle={"version":MODEL_VERSION,"model":model,"report":report,
                "last_train_time":time.time(),"symbol":symbol,"account":account}
        joblib.dump(bundle,path)
        metrics_file=path.with_suffix(".metrics.json")
        metrics_file.write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps(report,indent=2))
        print("[AI] Laporan historis:",metrics_file)
    return bundle["model"]


def atomic_csv_write(path:Path,fields:list[str]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+".tmp")
    with temp.open("w",newline="",encoding="ascii") as f:
        writer=csv.writer(f,lineterminator="\r\n")
        writer.writerow(fields)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp,path)


def run_terminal(args:argparse.Namespace) -> None:
    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        raise RuntimeError("Jalankan di Windows: pip install MetaTrader5") from exc
    if not mt5.initialize():
        raise RuntimeError(f"Tidak bisa connect MT5: {mt5.last_error()}")
    try:
        account=mt5.account_info()
        terminal=mt5.terminal_info()
        if account is None or terminal is None:
            raise RuntimeError("MT5 belum login atau terminal_info tidak tersedia")
        symbol=args.symbol
        if not mt5.symbol_select(symbol,True):
            raise RuntimeError(f"Simbol {symbol} tidak tersedia: {mt5.last_error()}")
        common_dir=Path(terminal.commondata_path)/"Files"
        account_id=int(account.login)
        target=common_dir/f"AurumAI_{account_id}_{symbol}_M15.csv"
        print("[MT5] Akun",account_id,"|",symbol,"| common files",common_dir)
        last_time=0
        while True:
            rates_array=mt5.copy_rates_from_pos(symbol,mt5.TIMEFRAME_M15,0,args.bars)
            if rates_array is None or len(rates_array)<MIN_TRAIN_BARS+150:
                raise RuntimeError("History MT5 kurang. Tambahkan Max bars in chart dan muat history M15.")
            frame=pd.DataFrame(rates_array).sort_values("time").reset_index(drop=True)
            frame=frame.iloc[:-1].copy()  # EXCLUDE still-forming bar
            symbol_info=mt5.symbol_info(symbol)
            if symbol_info is None or symbol_info.point<=0:
                raise RuntimeError("Tidak dapat membaca ukuran point broker")
            frame["spread_price"] = frame["spread"].astype(float)*float(symbol_info.point)
            latest=int(frame.iloc[-1]["time"])
            if latest!=last_time:
                last_time=latest
                model=get_model(frame,symbol,account_id)
                feature=build_features(frame).iloc[[-1]]
                if feature[FEATURE_COLUMNS].isna().any(axis=None):
                    raise RuntimeError("Indikator belum memiliki data valid")
                action,p_buy,p_sell,p_wait=choose_signal(model,feature)
                atomic_csv_write(target,[str(account_id),symbol,str(latest),action,
                                         f"{p_buy:.6f}",f"{p_sell:.6f}"])
                when=datetime.fromtimestamp(latest,tz=timezone.utc).isoformat()
                print(f"[AI] {when} {action} P(BUY)={p_buy:.3f} P(SELL)={p_sell:.3f} P(WAIT)={p_wait:.3f}")
            if args.once:
                break
            time.sleep(args.poll_seconds)
    finally:
        mt5.shutdown()


def main():
    parser=argparse.ArgumentParser(description="MT5 local ML confirmation; never sends orders")
    parser.add_argument("--symbol",default="XAUUSD",help="Exact broker symbol, incl suffix")
    parser.add_argument("--bars",type=int,default=8500,help="M15 history to train")
    parser.add_argument("--poll-seconds",type=int,default=12,help="Refresh check seconds")
    parser.add_argument("--once",action="store_true",help="Train/predict once")
    args=parser.parse_args()
    if args.bars<3000 or args.poll_seconds<2:
        parser.error("--bars minimal 3000 dan --poll-seconds minimal 2")
    run_terminal(args)

if __name__=="__main__":
    main()
