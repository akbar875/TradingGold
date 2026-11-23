#ifndef AURUM_SETUP_CLAIMS_MQH
#define AURUM_SETUP_CLAIMS_MQH

enum AurumSetupClaim
  {
   SETUP_CLAIMED,
   DUPLICATE_SIGNAL,
   SETUP_STATE_UNAVAILABLE
  };

string AurumSetupClaimPath(const string symbol)
  {
   string path="Aurum_setup_m15_";
   for(int index=0;index<StringLen(symbol);++index)
      path+=StringFormat("%04X",(uint)StringGetCharacter(symbol,index));
   return path+".bin";
  }

AurumSetupClaim AurumClaimSetupBar(const string path,const datetime bar_time,const bool tester,
                                   datetime &last_claim)
  {
   if(bar_time<=0 || path=="")
      return SETUP_STATE_UNAVAILABLE;
   if(bar_time<=last_claim)
      return DUPLICATE_SIGNAL;
   if(tester)
     {
      last_claim=bar_time;
      return SETUP_CLAIMED;
     }

   // Exclusive handle serializes charts. The file contains only the newest claimed M15 open time.
   const int handle=FileOpen(path,FILE_READ|FILE_WRITE|FILE_BIN);
   if(handle==INVALID_HANDLE)
      return SETUP_STATE_UNAVAILABLE;

   ResetLastError();
   const ulong size=FileSize(handle);
   bool readable=GetLastError()==0 && (size==0 || size==sizeof(long));
   datetime stored=0;
   if(readable && size!=0)
     {
      stored=(datetime)FileReadLong(handle);
      readable=GetLastError()==0 && stored>0;
     }
   AurumSetupClaim claim=SETUP_STATE_UNAVAILABLE;
   if(readable && bar_time<=stored)
     {
      last_claim=stored;
      claim=DUPLICATE_SIGNAL;
     }
   else if(readable && FileSeek(handle,0,SEEK_SET) && FileWriteLong(handle,(long)bar_time)==sizeof(long))
     {
      FileFlush(handle);
      if(GetLastError()==0)
        {
         last_claim=bar_time;
         claim=SETUP_CLAIMED;
        }
     }
   FileClose(handle);
   return claim;
  }

#endif
