#ifndef AURUM_REGIME_MQH
#define AURUM_REGIME_MQH

#include <Aurum/Indicators.mqh>

enum AurumMarketRegime
  {
   HIGH_VOLATILITY_UNSAFE,
   TREND_UP,
   TREND_DOWN,
   RANGE,
   REGIME_UNCLASSIFIED
  };

enum AurumRegimeDirection
  {
   REGIME_DIRECTION_BLOCKED,
   REGIME_BUY_ALLOWED,
   REGIME_SELL_ALLOWED
  };

enum AurumRegimeReason
  {
   REGIME_DATA_UNSAFE,
   REGIME_ATR_SPIKE,
   REGIME_SPREAD_TOO_WIDE,
   REGIME_HTF_CONFLICT,
   REGIME_TREND_CONFIRMED,
   REGIME_CONSOLIDATION,
   REGIME_INCONCLUSIVE
  };

struct AurumRegimeSettings
  {
   double min_trend_adx;
   double atr_spike_ratio;
   double max_spread_atr_ratio;
   double max_range_atr_ratio;
  };

struct AurumRegimeResult
  {
   AurumMarketRegime regime;
   AurumRegimeDirection direction;
   AurumRegimeReason reason;
  };

bool AurumValidRegimeSettings(const AurumRegimeSettings &settings)
  {
   return AurumPositiveNumber(settings.min_trend_adx) && settings.min_trend_adx<=100 &&
          AurumPositiveNumber(settings.atr_spike_ratio) && settings.atr_spike_ratio>1 &&
          AurumPositiveNumber(settings.max_spread_atr_ratio) &&
          AurumPositiveNumber(settings.max_range_atr_ratio);
  }

int AurumCompareDirection(const double first,const double second)
  {
   if(first>second)
      return 1;
   if(first<second)
      return -1;
   return 0;
  }

// Each evaluation replaces the entire result. A failed read cannot preserve a prior bias.
void AurumClassifyRegime(const AurumIndicatorStatus status,const AurumIndicatorSnapshot &snapshot,
                         const AurumRegimeSettings &settings,AurumRegimeResult &result)
  {
   result.regime=HIGH_VOLATILITY_UNSAFE;
   result.direction=REGIME_DIRECTION_BLOCKED;
   result.reason=REGIME_DATA_UNSAFE;
   if(status!=INDICATORS_READY || !AurumValidRegimeSettings(settings) ||
      !AurumPositiveNumber(snapshot.atr) || !AurumPositiveNumber(snapshot.prior_atr_mean) ||
      !AurumPositiveNumber(snapshot.spread_price))
      return;

   const double atr_ratio=snapshot.atr/snapshot.prior_atr_mean;
   const double spread_ratio=snapshot.spread_price/snapshot.prior_atr_mean;
   const double range_ratio=snapshot.range_price/snapshot.prior_atr_mean;
   if(!AurumPositiveNumber(atr_ratio) || !AurumPositiveNumber(spread_ratio) ||
      !MathIsValidNumber(range_ratio) || range_ratio==EMPTY_VALUE || range_ratio<0)
      return;
   if(atr_ratio>=settings.atr_spike_ratio)
     {
      result.reason=REGIME_ATR_SPIKE;
      return;
     }
   if(spread_ratio>=settings.max_spread_atr_ratio)
     {
      result.reason=REGIME_SPREAD_TOO_WIDE;
      return;
     }

   const int h1=AurumCompareDirection(snapshot.ema_h1_fast,snapshot.ema_h1_slow);
   const int h4=AurumCompareDirection(snapshot.ema_h4_fast,snapshot.ema_h4_slow);
   result.regime=REGIME_UNCLASSIFIED;
   result.reason=REGIME_INCONCLUSIVE;
   if(h1*h4<0)
     {
      result.reason=REGIME_HTF_CONFLICT;
      return;
     }
   if(snapshot.adx<settings.min_trend_adx)
     {
      if(range_ratio<=settings.max_range_atr_ratio)
        {
         result.regime=RANGE;
         result.reason=REGIME_CONSOLIDATION;
        }
      return;
     }

   const int m15=AurumCompareDirection(snapshot.ema_m15_fast,snapshot.ema_m15_slow);
   const int di=AurumCompareDirection(snapshot.plus_di,snapshot.minus_di);
   if(h1==0 || h1!=h4 || h1!=m15 || h1!=di)
      return;
   result.regime=h1>0 ? TREND_UP : TREND_DOWN;
   result.direction=h1>0 ? REGIME_BUY_ALLOWED : REGIME_SELL_ALLOWED;
   result.reason=REGIME_TREND_CONFIRMED;
  }

#endif
