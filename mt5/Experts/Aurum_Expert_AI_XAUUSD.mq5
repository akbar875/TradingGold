#property strict
#property version "3.00"
#property description "Diagnostik dan indikator closed-bar. Tidak memiliki jalur eksekusi order."

#include <Aurum/Status.mqh>
#include <Aurum/Indicators.mqh>

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

AurumIndicators Indicators;

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
   Comment("Aurum v3 foundation\n",AurumFoundationStatus());
   return INIT_SUCCEEDED;
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
   if(status!=INDICATORS_READY)
     {
      Comment(header,"WAIT | ",EnumToString(status));
      return;
     }

   Comment(header,"WAIT | ENGINE_NOT_IMPLEMENTED | SIGNAL ONLY | ",EnumToString(status),
           "\nBar open (waktu server) M15 ",TimeToString(snapshot.m15_open,TIME_DATE|TIME_MINUTES),
           " | H1 ",TimeToString(snapshot.h1_open,TIME_DATE|TIME_MINUTES),
           "\nEMA M15 fast / slow: ",DoubleToString(snapshot.ema_m15_fast,8)," / ",DoubleToString(snapshot.ema_m15_slow,8),
           "\nEMA H1 fast / slow: ",DoubleToString(snapshot.ema_h1_fast,8)," / ",DoubleToString(snapshot.ema_h1_slow,8),
           "\nRSI: ",DoubleToString(snapshot.rsi,8),
           " | MACD main / signal: ",DoubleToString(snapshot.macd_main,8)," / ",DoubleToString(snapshot.macd_signal,8),
           "\nADX / +DI / -DI: ",DoubleToString(snapshot.adx,8)," / ",DoubleToString(snapshot.plus_di,8),
           " / ",DoubleToString(snapshot.minus_di,8)," | ATR: ",DoubleToString(snapshot.atr,8));
  }

void OnDeinit(const int reason)
  {
   Indicators.Release();
   Comment("");
  }
