#property strict
#property version "3.00"
#property description "Scaffold diagnostik saja. Tidak memiliki jalur eksekusi order."

#include <Aurum/Status.mqh>

input bool InpSignalOnly = true;
input bool InpEnableAutoTrade = false;
input bool InpDemoOnly = true;
input bool InpRequireLeverage2000 = true;
input bool InpRequireAI = false;
input bool InpRequireNewsFilter = true;
input bool InpEmergencyKillSwitch = false;
input double InpRiskPercentPerTrade = 0.25;
input double InpMaxLot = 0.05;

int OnInit()
  {
   if(!InpSignalOnly || InpEnableAutoTrade || !InpDemoOnly)
     {
      Print("EXECUTION_NOT_IMPLEMENTED: gunakan preset Signal_Only.");
      return INIT_PARAMETERS_INCORRECT;
     }
   if(InpRiskPercentPerTrade<=0 || InpRiskPercentPerTrade>100 || InpMaxLot<=0)
      return INIT_PARAMETERS_INCORRECT;
   Comment("Aurum v3 foundation\n",AurumFoundationStatus());
   return INIT_SUCCEEDED;
  }

void OnTick()
  {
   string status=InpEmergencyKillSwitch ? "WAIT | KILL_SWITCH" : AurumFoundationStatus();
   Comment("Aurum v3 foundation\n",status,"\nSymbol: ",_Symbol,
           "\nLeverage aktual: 1:",AccountInfoInteger(ACCOUNT_LEVERAGE),
           "\nAnalisis, ML, risk engine dan pengelolaan posisi belum tersedia.");
  }

void OnDeinit(const int reason)
  {
   Comment("");
  }
