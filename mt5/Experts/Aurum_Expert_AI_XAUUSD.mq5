#property strict
#property version "3.00"
#property description "Diagnostik indikator, market regime dan setup closed-bar. Tidak memiliki jalur eksekusi order."

#include <Aurum/Status.mqh>
#include <Aurum/Setups.mqh>
#include <Aurum/SetupClaims.mqh>

input bool InpSignalOnly = true;
input bool InpEnableAutoTrade = false;
input bool InpDemoOnly = true;
input bool InpRequireLeverage2000 = true;
input bool InpRequireAI = false;
input bool InpRequireNewsFilter = true;
input bool InpEmergencyKillSwitch = false;
input double InpRiskPercentPerTrade = 0.25;
input double InpMaxLot = 0.05;
input int InpEmaM15Fast = 20;
input int InpEmaM15Slow = 50;
input int InpEmaH1Fast = 50;
input int InpEmaH1Slow = 200;
input int InpRsiPeriod = 14;
input int InpMacdFast = 12;
input int InpMacdSlow = 26;
input int InpMacdSignal = 9;
input int InpAdxPeriod = 14;
input int InpAtrPeriod = 14;
input int InpEmaH4Fast = 50;
input int InpEmaH4Slow = 200;
input double InpRegimeMinTrendAdx = 25.0;
input double InpRegimeAtrSpikeRatio = 2.0;
input double InpRegimeMaxSpreadAtrRatio = 0.25;
input double InpRegimeMaxRangeAtrRatio = 4.0;
input int InpSetupKeyLookback = 12;
input int InpSetupMaxRetestBars = 3;
input double InpSetupZoneAtr = 0.30;
input double InpSetupMinBreakoutBodyRatio = 0.60;
input double InpSetupMaxChaseAtr = 1.50;
input double InpSetupMaxStopAtr = 3.00;

AurumIndicators Indicators;
AurumRegimeSettings RegimeSettings;
AurumSetupSettings SetupSettings;
string SetupClaimPath;
datetime LastSetupClaim;

int OnInit()
  {
   if(!InpSignalOnly || InpEnableAutoTrade || !InpDemoOnly)
     {
      Print("EXECUTION_NOT_IMPLEMENTED: gunakan preset Signal_Only.");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(InpRiskPercentPerTrade<=0 || InpRiskPercentPerTrade>100 || InpMaxLot<=0)
      return INIT_PARAMETERS_INCORRECT;

   AurumIndicatorPeriods periods;
   periods.ema_m15_fast=InpEmaM15Fast;
   periods.ema_m15_slow=InpEmaM15Slow;
   periods.ema_h1_fast=InpEmaH1Fast;
   periods.ema_h1_slow=InpEmaH1Slow;
   periods.rsi=InpRsiPeriod;
   periods.macd_fast=InpMacdFast;
   periods.macd_slow=InpMacdSlow;
   periods.macd_signal=InpMacdSignal;
   periods.adx=InpAdxPeriod;
   periods.atr=InpAtrPeriod;
   periods.ema_h4_fast=InpEmaH4Fast;
   periods.ema_h4_slow=InpEmaH4Slow;
   RegimeSettings.min_trend_adx=InpRegimeMinTrendAdx;
   RegimeSettings.atr_spike_ratio=InpRegimeAtrSpikeRatio;
   RegimeSettings.max_spread_atr_ratio=InpRegimeMaxSpreadAtrRatio;
   RegimeSettings.max_range_atr_ratio=InpRegimeMaxRangeAtrRatio;
   if(!AurumValidRegimeSettings(RegimeSettings))
     {
      Print("REGIME_SETTINGS_INVALID: periksa ambang ADX, ATR, spread dan range.");
      return INIT_PARAMETERS_INCORRECT;
     }
   SetupSettings.key_lookback=InpSetupKeyLookback;
   SetupSettings.max_retest_bars=InpSetupMaxRetestBars;
   SetupSettings.zone_atr=InpSetupZoneAtr;
   SetupSettings.min_breakout_body_ratio=InpSetupMinBreakoutBodyRatio;
   SetupSettings.max_chase_atr=InpSetupMaxChaseAtr;
   SetupSettings.max_stop_atr=InpSetupMaxStopAtr;
   if(!AurumValidSetupSettings(SetupSettings))
     {
      Print("SETUP_SETTINGS_INVALID");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(!AurumValidIndicatorPeriods(periods))
     {
      Print("INDICATOR_PERIOD_INVALID: gunakan periode positif dan fast < slow.");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(!Indicators.Create(_Symbol,periods))
     {
      Print("INDICATOR_HANDLE_FAILED: inisialisasi indikator gagal untuk ",_Symbol);
      return INIT_FAILED;
     }
   SetupClaimPath=AurumSetupClaimPath(_Symbol);
   LastSetupClaim=0;
   Comment("Aurum v3 foundation\n",AurumFoundationStatus());
   return INIT_SUCCEEDED;
  }

string SetupDiagnostic(const AurumIndicatorSnapshot &snapshot,const AurumRegimeResult &regime)
  {
   if(regime.direction==REGIME_DIRECTION_BLOCKED)
      return "SETUP_REGIME_BLOCKED";
   AurumSetupHistory history;
   const int count=SetupSettings.key_lookback+SetupSettings.max_retest_bars+2;
   const AurumIndicatorStatus status=Indicators.ReadSetupHistory(snapshot,count,history);
   if(status!=INDICATORS_READY)
      return EnumToString(status);

   MqlTick quote;
   long chart_mode;
   if(!SymbolInfoInteger(_Symbol,SYMBOL_CHART_MODE,chart_mode) || chart_mode!=SYMBOL_CHART_MODE_BID ||
      !SymbolInfoTick(_Symbol,quote))
      return "SETUP_QUOTE_INVALID";

   AurumSetupResult result;
   AurumEvaluateSetup(snapshot,regime,history,SetupSettings,quote,result);
   if(result.action==SETUP_WAIT)
      return EnumToString(result.reason);

   const AurumSetupClaim claim=AurumClaimSetupBar(SetupClaimPath,result.bar_time,
                                                 (bool)MQLInfoInteger(MQL_TESTER),LastSetupClaim);
   if(claim==SETUP_STATE_UNAVAILABLE)
      return EnumToString(claim);

   const string candidate=StringFormat("%s | %s | Level %s | Invalidation %s",
                                       EnumToString(result.action),EnumToString(result.kind),
                                       DoubleToString(result.key_level,_Digits),
                                       DoubleToString(result.invalidation,_Digits));
   if(claim==SETUP_CLAIMED)
      Print("SETUP_CONFIRMED | ",_Symbol," | ",TimeToString(result.bar_time,TIME_DATE|TIME_MINUTES)," | ",candidate);
   return candidate+(claim==DUPLICATE_SIGNAL ? " | DUPLICATE_SIGNAL" : "");
  }

void OnTick()
  {
   string header=StringFormat("Aurum v3 foundation\nSymbol: %s | Leverage aktual: 1:%I64d\n",
                             _Symbol,AccountInfoInteger(ACCOUNT_LEVERAGE));
   if(InpEmergencyKillSwitch || (!MQLInfoInteger(MQL_TESTER) && !TerminalInfoInteger(TERMINAL_CONNECTED)))
     {
      Comment(header,InpEmergencyKillSwitch ? "WAIT | KILL_SWITCH" : AurumFoundationStatus());
      return;
     }

   AurumIndicatorSnapshot snapshot;
   const AurumIndicatorStatus status=Indicators.ReadLatest(snapshot);
   AurumRegimeResult regime;
   AurumClassifyRegime(status,snapshot,RegimeSettings,regime);
   const string regime_line=StringFormat("\nRegime: %s | %s | %s",EnumToString(regime.regime),
                                         EnumToString(regime.direction),EnumToString(regime.reason));
   if(status!=INDICATORS_READY)
     {
      Comment(header,"WAIT | ",EnumToString(status),regime_line);
      return;
     }

   const string setup_line=SetupDiagnostic(snapshot,regime);
   const string entry_reason=InpRequireNewsFilter ? "NEWS_UNKNOWN" :
                             (InpRequireAI ? "AI_UNAVAILABLE" : "ENGINE_NOT_IMPLEMENTED");
   Comment(header,"WAIT | ",entry_reason," | SIGNAL ONLY",regime_line,"\nSetup diagnostic: ",setup_line,
           "\nBar open (waktu server) M15 ",TimeToString(snapshot.m15_open,TIME_DATE|TIME_MINUTES),
           " | H1 ",TimeToString(snapshot.h1_open,TIME_DATE|TIME_MINUTES),
           " | H4 ",TimeToString(snapshot.h4_open,TIME_DATE|TIME_MINUTES),
           "\nEMA M15 fast / slow: ",DoubleToString(snapshot.ema_m15_fast,8)," / ",DoubleToString(snapshot.ema_m15_slow,8),
           "\nEMA H1 fast / slow: ",DoubleToString(snapshot.ema_h1_fast,8)," / ",DoubleToString(snapshot.ema_h1_slow,8),
           "\nEMA H4 fast / slow: ",DoubleToString(snapshot.ema_h4_fast,8)," / ",DoubleToString(snapshot.ema_h4_slow,8),
           "\nRSI: ",DoubleToString(snapshot.rsi,8),
           " | MACD main / signal: ",DoubleToString(snapshot.macd_main,8)," / ",DoubleToString(snapshot.macd_signal,8),
           "\nADX / +DI / -DI: ",DoubleToString(snapshot.adx,8)," / ",DoubleToString(snapshot.plus_di,8),
           " / ",DoubleToString(snapshot.minus_di,8)," | ATR: ",DoubleToString(snapshot.atr,8),
           "\nATR baseline: ",DoubleToString(snapshot.prior_atr_mean,8),
           " | Spread: ",DoubleToString(snapshot.spread_price,8),
           " | Range: ",DoubleToString(snapshot.range_price,8));
  }

void OnDeinit(const int reason)
  {
   Indicators.Release();
   Comment("");
  }
