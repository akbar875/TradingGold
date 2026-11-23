#ifndef AURUM_SETUPS_MQH
#define AURUM_SETUPS_MQH

#include <Aurum/Regime.mqh>

enum AurumSetupKind
  {
   NO_SETUP,
   TREND_PULLBACK,
   BREAKOUT_RETEST
  };

enum AurumSetupAction
  {
   SETUP_WAIT,
   SETUP_BUY,
   SETUP_SELL
  };

enum AurumSetupReason
  {
   SETUP_DATA_INVALID,
   SETUP_REGIME_BLOCKED,
   NO_VALID_SETUP,
   SETUP_QUOTE_INVALID,
   SETUP_INVALIDATED,
   PRICE_CHASED,
   SETUP_STOP_DISTANCE,
   SETUP_CONFIRMED
  };

struct AurumSetupSettings
  {
   int key_lookback;
   int max_retest_bars;
   double zone_atr;
   double min_breakout_body_ratio;
   double max_chase_atr;
   double max_stop_atr;
  };

struct AurumSetupResult
  {
   AurumSetupAction action;
   AurumSetupKind kind;
   AurumSetupReason reason;
   datetime bar_time;
   double key_level;
   double invalidation;
  };

bool AurumValidSetupSettings(const AurumSetupSettings &settings)
  {
   return settings.key_lookback>=2 && settings.key_lookback<=AURUM_SETUP_MAX_LOOKBACK &&
          settings.max_retest_bars>=1 && settings.max_retest_bars<=AURUM_SETUP_MAX_RETEST_BARS &&
          AurumPositiveNumber(settings.zone_atr) &&
          AurumPositiveNumber(settings.min_breakout_body_ratio) && settings.min_breakout_body_ratio<=1 &&
          AurumPositiveNumber(settings.max_chase_atr) && settings.max_chase_atr>=settings.zone_atr &&
          AurumPositiveNumber(settings.max_stop_atr);
  }

// In directional coordinates, continuation is always toward higher prices.
double AurumForwardExtreme(const MqlRates &bar,const int side)
  {
   return side>0 ? bar.high : -bar.low;
  }

double AurumAdverseExtreme(const MqlRates &bar,const int side)
  {
   return side>0 ? bar.low : -bar.high;
  }

bool AurumClosedContinuation(const MqlRates &touch,const MqlRates &confirmation,const int side)
  {
   return side*confirmation.close>side*confirmation.open &&
          side*confirmation.close>AurumForwardExtreme(touch,side) &&
          AurumAdverseExtreme(confirmation,side)>AurumAdverseExtreme(touch,side);
  }

bool AurumPullback(const MqlRates &touch,const double ema,const double zone,const int side)
  {
   const double level=side*ema;
   const double extreme=AurumAdverseExtreme(touch,side);
   return extreme>=level-zone && extreme<=level+zone && side*touch.close>=level;
  }

double AurumPriorKeyLevel(const AurumSetupHistory &history,const int breakout,const int lookback,const int side)
  {
   const int first=breakout-lookback;
   double level=AurumForwardExtreme(history.bars[first],side);
   for(int index=first+1;index<breakout;++index)
      level=MathMax(level,AurumForwardExtreme(history.bars[index],side));
   return level;
  }

bool AurumRetestedBreakout(const AurumSetupHistory &history,const AurumSetupSettings &settings,
                          const double zone,const int side,double &level)
  {
   const int retest=history.count-2;
   const MqlRates touch=history.bars[retest];
   for(int index=retest-1;index>=retest-settings.max_retest_bars;--index)
     {
      const MqlRates bar=history.bars[index];
      const double key=AurumPriorKeyLevel(history,index,settings.key_lookback,side);
      const double body=side*bar.close-side*bar.open;
      if(side*bar.open>key || side*bar.close<=key || body<=0 ||
         body<(bar.high-bar.low)*settings.min_breakout_body_ratio)
         continue;
      const double extreme=AurumAdverseExtreme(touch,side);
      if(extreme<key-zone || extreme>key+zone || side*touch.close<=key)
         continue;

      // A close back at or through the broken level cancels this breakout.
      bool held=true;
      for(int follow=index+1;follow<retest;++follow)
         if(side*history.bars[follow].close<=key)
           {
            held=false;
            break;
           }
      if(held)
        {
         level=key;
         return true;
        }
     }
   return false;
  }

void AurumEvaluateSetup(const AurumIndicatorSnapshot &snapshot,const AurumRegimeResult &regime,
                        const AurumSetupHistory &history,const AurumSetupSettings &settings,
                        const MqlTick &quote,AurumSetupResult &result)
  {
   ZeroMemory(result);
   result.reason=SETUP_DATA_INVALID;
   const int seconds=PeriodSeconds(PERIOD_M15);
   if(!AurumValidSetupSettings(settings) || !AurumPositiveNumber(snapshot.prior_atr_mean) ||
      !AurumPositiveNumber(history.pullback_ema) || snapshot.m15_open<=0 ||
      snapshot.decision_time!=snapshot.m15_open+seconds ||
      history.count!=settings.key_lookback+settings.max_retest_bars+2)
      return;
   for(int index=0;index<history.count;++index)
      if(history.bars[index].time!=snapshot.decision_time-(history.count-index)*seconds ||
         !AurumValidOhlc(history.bars[index]))
         return;

   int side=0;
   if(regime.regime==TREND_UP && regime.direction==REGIME_BUY_ALLOWED)
      side=1;
   if(regime.regime==TREND_DOWN && regime.direction==REGIME_SELL_ALLOWED)
      side=-1;
   if(side==0)
     {
      result.reason=SETUP_REGIME_BLOCKED;
      return;
     }

   const double zone=settings.zone_atr*snapshot.prior_atr_mean;
   const double chase_limit=settings.max_chase_atr*snapshot.prior_atr_mean;
   const double stop_limit=settings.max_stop_atr*snapshot.prior_atr_mean;
   if(!AurumPositiveNumber(zone) || !AurumPositiveNumber(chase_limit) || !AurumPositiveNumber(stop_limit))
      return;

   const MqlRates touch=history.bars[history.count-2];
   const MqlRates confirmation=history.bars[history.count-1];
   result.reason=NO_VALID_SETUP;
   if(!AurumClosedContinuation(touch,confirmation,side))
      return;

   AurumSetupKind kind=BREAKOUT_RETEST;
   double level=0;
   if(!AurumRetestedBreakout(history,settings,zone,side,level))
     {
      if(!AurumPullback(touch,history.pullback_ema,zone,side))
         return;
      level=side*history.pullback_ema;
      kind=TREND_PULLBACK;
     }

   result.reason=SETUP_QUOTE_INVALID;
   if(!AurumPositiveNumber(quote.bid) || !AurumPositiveNumber(quote.ask) || quote.ask<quote.bid ||
      quote.time<snapshot.decision_time || quote.time>=snapshot.decision_time+seconds)
      return;
   const double live_structure_price=side*quote.bid; // XAUUSD chart OHLC is based on Bid.
   const double entry=side>0 ? quote.ask : -quote.bid;
   const double invalidation=AurumAdverseExtreme(touch,side);
   if(live_structure_price<=invalidation || entry<=invalidation || live_structure_price<level-zone)
      result.reason=SETUP_INVALIDATED;
   else if(entry>level+chase_limit || side*confirmation.close>level+chase_limit)
      result.reason=PRICE_CHASED;
   else if(entry-invalidation>stop_limit)
      result.reason=SETUP_STOP_DISTANCE;
   else
     {
      result.action=side>0 ? SETUP_BUY : SETUP_SELL;
      result.kind=kind;
      result.reason=SETUP_CONFIRMED;
      result.bar_time=snapshot.m15_open;
      result.key_level=side*level;
      result.invalidation=side*invalidation;
     }
  }

#endif
