# Backtest — belum tersedia

`python -m aurum.cli backtest --config config/default.yaml` saat ini exit 2,
NOT_IMPLEMENTED (AU-023). `export-signals` menunggu replay OOS AU-024.
Belum ada hasil P/L, equity curve, Monte Carlo atau bukti broker.

Data nantinya berasal dari CSV pengguna atau history broker berizin, dengan metadata
source/broker/symbol/timeframe/UTC/range/hash. Spread, slippage, commission dan swap
dicatat eksplisit; entry setelah sinyal tersedia; ambigu SL/TP dinilai stop-first.
Jangan mengisi entry pada candle sebelum keputusan. Per-trade journal dan metrik
net P/L, DD, expectancy R, PF, jumlah trade dan exposure wajib dapat direproduksi.

Bandingkan rules-only, ML-only diagnostik, combined dan WAIT baseline.
Pisahkan training klasifikasi, backtest, tester replay dan demo forward.
Strategy Tester tidak boleh diasumsikan memiliki proses Python/live kalender.
