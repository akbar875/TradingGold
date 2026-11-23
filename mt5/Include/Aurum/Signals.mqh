#ifndef AURUM_SIGNALS_MQH
#define AURUM_SIGNALS_MQH

#include <Aurum/Setups.mqh>
#include <Aurum/SetupClaims.mqh>

#define AURUM_SCORE_PARTS 6
#define AURUM_SIGNAL_REASONS 12

struct AurumScorePart
  {
   string rule;
   bool passed;
   int weight;
   double observed;
   double reference;
  };

struct AurumSignalResult
  {
   AurumSetupResult candidate;
   string signal_id;
   int technical_score; // -1 indicates no eligible score.
   AurumScorePart parts[AURUM_SCORE_PARTS];
   int reason_count;
   string reasons[AURUM_SIGNAL_REASONS]; // In priority order.
  };

void AurumAddSignalReason(AurumSignalResult &result,const string reason)
  {
   for(int index=0;index<result.reason_count;++index)
      if(result.reasons[index]==reason)
         return;
   if(result.reason_count<AURUM_SIGNAL_REASONS)
      result.reasons[result.reason_count++]=reason;
  }

void AurumClearCandidate(AurumSignalResult &result)
  {
   ZeroMemory(result.candidate);
   result.signal_id="";
   result.technical_score=-1;
   for(int index=0;index<AURUM_SCORE_PARTS;++index)
      ZeroMemory(result.parts[index]);
  }

// Length-prefix text fields to keep broker names and symbol suffixes unambiguous.
string AurumSignalField(const string value)
  {
   return IntegerToString(StringLen(value))+":"+value;
  }

string AurumSignalDigest(const string value)
  {
   // FNV-1a 64-bit over UTF-16 code units, low byte first.
   ulong hash=(ulong)0xCBF29CE484222325;
   for(int index=0;index<StringLen(value);++index)
     {
      const uint code=StringGetCharacter(value,index);
      hash=(hash^(code&255))*0x100000001B3;
      hash=(hash^(code>>8))*0x100000001B3;
     }
   return StringFormat("%016I64X",hash);
  }

string AurumSignalScope(const long login,const string server,const string symbol)
  {
   if(login<=0 || server=="" || symbol=="")
      return "";
   return "v1|"+IntegerToString(login)+"|"+AurumSignalField(server)+AurumSignalField(symbol);
  }

string AurumSignalId(const string scope,const ENUM_TIMEFRAMES timeframe,const datetime bar_open,
                    const AurumSetupKind setup,const AurumSetupAction side)
  {
   if(scope=="" || (int)timeframe<=0 || PeriodSeconds(timeframe)<=0 || bar_open<=0 ||
      (setup!=TREND_PULLBACK && setup!=BREAKOUT_RETEST) || (side!=SETUP_BUY && side!=SETUP_SELL))
      return "";
   const string setup_name=setup==TREND_PULLBACK ? "TREND_PULLBACK" : "BREAKOUT_RETEST";
   const string side_name=side==SETUP_BUY ? "BUY" : "SELL";
   return "AUR1-"+AurumSignalDigest(scope+"|"+IntegerToString(timeframe)+"|"+
                                   IntegerToString(bar_open)+"|"+setup_name+"|"+side_name);
  }

void AurumSetScorePart(AurumSignalResult &result,const int index,const string rule,const bool passed,
                       const int weight,const double observed,const double reference)
  {
   result.parts[index].rule=rule;
   result.parts[index].passed=passed;
   result.parts[index].weight=weight;
   result.parts[index].observed=observed;
   result.parts[index].reference=reference;
   if(passed)
      result.technical_score+=weight;
  }

bool AurumValidScoreSnapshot(const AurumIndicatorSnapshot &snapshot,const AurumRegimeSettings &settings)
  {
   return AurumValidRegimeSettings(settings) && snapshot.m15_open>0 &&
          snapshot.decision_time-snapshot.m15_open==PeriodSeconds(PERIOD_M15) &&
          AurumPositiveNumber(snapshot.ema_h1_fast) && AurumPositiveNumber(snapshot.ema_h1_slow) &&
          AurumPositiveNumber(snapshot.ema_h4_fast) && AurumPositiveNumber(snapshot.ema_h4_slow) &&
          MathIsValidNumber(snapshot.adx) && snapshot.adx>=0 && snapshot.adx<=100 &&
          MathIsValidNumber(snapshot.rsi) && snapshot.rsi>=0 && snapshot.rsi<=100 &&
          MathIsValidNumber(snapshot.macd_main) && snapshot.macd_main!=EMPTY_VALUE &&
          MathIsValidNumber(snapshot.macd_signal) && snapshot.macd_signal!=EMPTY_VALUE &&
          AurumPositiveNumber(snapshot.atr) && AurumPositiveNumber(snapshot.prior_atr_mean) &&
          AurumPositiveNumber(snapshot.spread_price) &&
          AurumPositiveNumber(snapshot.atr/snapshot.prior_atr_mean) &&
          AurumPositiveNumber(snapshot.spread_price/snapshot.prior_atr_mean);
  }

bool AurumScoreCandidate(const AurumIndicatorSnapshot &snapshot,const AurumRegimeSettings &settings,
                         const AurumRegimeResult &regime,const AurumSetupResult &setup,
                         const string scope,AurumSignalResult &result)
  {
   const int side=setup.action==SETUP_BUY ? 1 : -1;
   const bool trend_matches=side>0 ? regime.regime==TREND_UP && regime.direction==REGIME_BUY_ALLOWED :
                                     regime.regime==TREND_DOWN && regime.direction==REGIME_SELL_ALLOWED;
   const int h1=AurumCompareDirection(snapshot.ema_h1_fast,snapshot.ema_h1_slow);
   const int h4=AurumCompareDirection(snapshot.ema_h4_fast,snapshot.ema_h4_slow);
   if(!trend_matches || regime.reason!=REGIME_TREND_CONFIRMED || h1!=side || h4!=side ||
      snapshot.adx<settings.min_trend_adx || setup.reason!=SETUP_CONFIRMED ||
      setup.bar_time!=snapshot.m15_open || !AurumPositiveNumber(setup.key_level) ||
      !AurumPositiveNumber(setup.invalidation))
      return false;
   const string id=AurumSignalId(scope,PERIOD_M15,setup.bar_time,setup.kind,setup.action);
   if(id=="")
      return false;

   result.candidate=setup;
   result.signal_id=id;
   result.technical_score=0;
   AurumSetScorePart(result,0,"SETUP_LEVEL/INVALIDATION",true,30,setup.key_level,setup.invalidation);
   AurumSetScorePart(result,1,"H1_EMA_FAST/SLOW",h1==side,15,snapshot.ema_h1_fast,snapshot.ema_h1_slow);
   AurumSetScorePart(result,2,"H4_EMA_FAST/SLOW",h4==side,15,snapshot.ema_h4_fast,snapshot.ema_h4_slow);
   AurumSetScorePart(result,3,"ADX/MIN",snapshot.adx>=settings.min_trend_adx,15,
                     snapshot.adx,settings.min_trend_adx);
   AurumSetScorePart(result,4,"MACD_MAIN/SIGNAL",
                     AurumCompareDirection(snapshot.macd_main,snapshot.macd_signal)==side,15,
                     snapshot.macd_main,snapshot.macd_signal);
   AurumSetScorePart(result,5,"RSI/MIDPOINT",AurumCompareDirection(snapshot.rsi,50)==side,10,
                     snapshot.rsi,50);
   return true;
  }

void AurumEvaluateSignal(const AurumIndicatorStatus indicator_status,const AurumIndicatorSnapshot &snapshot,
                         const AurumRegimeSettings &settings,const AurumRegimeResult &regime,
                         const AurumIndicatorStatus setup_status,const AurumSetupResult &setup,
                         const string scope,const bool require_news,const bool require_ai,
                         AurumSignalResult &result)
  {
   ZeroMemory(result);
   result.technical_score=-1;
   const bool snapshot_ready=indicator_status==INDICATORS_READY && AurumValidScoreSnapshot(snapshot,settings);
   const bool setup_input_ready=setup_status==INDICATORS_READY &&
                                setup.reason!=SETUP_DATA_INVALID && setup.reason!=SETUP_QUOTE_INVALID;
   if(scope=="")
      AurumAddSignalReason(result,"SIGNAL_ACCOUNT_INVALID");
   if(indicator_status!=INDICATORS_READY)
      AurumAddSignalReason(result,EnumToString(indicator_status));
   else if(!snapshot_ready)
      AurumAddSignalReason(result,"SIGNAL_DATA_INVALID");
   else if(setup_status!=INDICATORS_READY)
      AurumAddSignalReason(result,EnumToString(setup_status));
   else if(!setup_input_ready)
      AurumAddSignalReason(result,EnumToString(setup.reason));

   bool atr_block=false;
   bool spread_block=false;
   if(snapshot_ready)
     {
      atr_block=snapshot.atr/snapshot.prior_atr_mean>=settings.atr_spike_ratio;
      spread_block=snapshot.spread_price/snapshot.prior_atr_mean>=settings.max_spread_atr_ratio;
      if(atr_block)
         AurumAddSignalReason(result,"REGIME_ATR_SPIKE");
      if(spread_block)
         AurumAddSignalReason(result,"REGIME_SPREAD_TOO_WIDE");
      if(regime.reason==REGIME_DATA_UNSAFE)
         AurumAddSignalReason(result,EnumToString(regime.reason));
     }
   if(require_news)
      AurumAddSignalReason(result,"NEWS_UNKNOWN");
   if(snapshot_ready)
     {
      const int h1=AurumCompareDirection(snapshot.ema_h1_fast,snapshot.ema_h1_slow);
      const int h4=AurumCompareDirection(snapshot.ema_h4_fast,snapshot.ema_h4_slow);
      if(h1*h4<0)
         AurumAddSignalReason(result,"REGIME_HTF_CONFLICT");
      if(regime.direction==REGIME_DIRECTION_BLOCKED)
         AurumAddSignalReason(result,regime.reason==REGIME_TREND_CONFIRMED ?
                              "SIGNAL_DATA_INVALID" : EnumToString(regime.reason));
      else if(setup_input_ready)
        {
         if(setup.action==SETUP_WAIT)
            AurumAddSignalReason(result,setup.reason==SETUP_CONFIRMED ?
                                 "SIGNAL_CANDIDATE_INVALID" : EnumToString(setup.reason));
         else if(scope!="" && !atr_block && !spread_block && !AurumScoreCandidate(snapshot,settings,regime,setup,scope,result))
            AurumAddSignalReason(result,"SIGNAL_CANDIDATE_INVALID");
        }
     }
   if(require_ai)
      AurumAddSignalReason(result,"AI_UNAVAILABLE");
   if(result.reason_count==0)
      AurumAddSignalReason(result,"ENGINE_NOT_IMPLEMENTED");
  }

bool AurumClaimSignalDiagnostic(const string scope,const bool tester,string &current_path,
                                datetime &last_claim,AurumSignalResult &result)
  {
   if(result.technical_score<0)
      return false;
   const string path="Aurum_signal_v1_"+AurumSignalDigest(scope)+".bin";
   if(path!=current_path)
     {
      current_path=path;
      last_claim=0;
     }
   const AurumSetupClaim claim=AurumClaimSetupBar(path,result.candidate.bar_time,tester,last_claim);
   if(claim==SETUP_CLAIMED)
      return true;
   if(claim==SETUP_STATE_UNAVAILABLE)
      AurumClearCandidate(result);
   if(result.reason_count==1 && result.reasons[0]=="ENGINE_NOT_IMPLEMENTED")
      result.reasons[0]=EnumToString(claim);
   else
      AurumAddSignalReason(result,EnumToString(claim));
   return false;
  }

#endif
