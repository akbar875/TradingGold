#ifndef AURUM_STATUS_MQH
#define AURUM_STATUS_MQH

string AurumFoundationStatus()
  {
   if(!TerminalInfoInteger(TERMINAL_CONNECTED))
      return "WAIT | MT5_DISCONNECTED";
   return "WAIT | ENGINE_NOT_IMPLEMENTED | SIGNAL ONLY";
  }

#endif
