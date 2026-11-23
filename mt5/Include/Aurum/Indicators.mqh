#ifndef AURUM_INDICATORS_MQH
#define AURUM_INDICATORS_MQH

#define AURUM_REGIME_LOOKBACK 8
#define AURUM_SETUP_MAX_LOOKBACK 64
#define AURUM_SETUP_MAX_RETEST_BARS 16
#define AURUM_SETUP_MAX_BARS (AURUM_SETUP_MAX_LOOKBACK+AURUM_SETUP_MAX_RETEST_BARS+2)

bool AurumPositiveNumber(const double value)
  {
   return value>0 && value!=EMPTY_VALUE && MathIsValidNumber(value);
  }

bool AurumValidOhlc(const MqlRates &bar)
  {
   return AurumPositiveNumber(bar.open) && AurumPositiveNumber(bar.high) &&
          AurumPositiveNumber(bar.low) && AurumPositiveNumber(bar.close) &&
          bar.low<=MathMin(bar.open,bar.close) && bar.high>=MathMax(bar.open,bar.close);
  }

enum AurumIndicatorStatus
  {
   INDICATORS_READY,
   INDICATOR_HANDLE_FAILED,
   INDICATOR_WARMUP,
   INDICATOR_DATA_STALE,
   INDICATOR_COPY_FAILED,
   INDICATOR_VALUE_INVALID,
   INDICATOR_BAR_CHANGED
  };

struct AurumIndicatorPeriods
  {
   int ema_m15_fast;
   int ema_m15_slow;
   int ema_h1_fast;
   int ema_h1_slow;
   int rsi;
   int macd_fast;
   int macd_slow;
   int macd_signal;
   int adx;
   int atr;
   int ema_h4_fast;
   int ema_h4_slow;
  };

bool AurumValidIndicatorPeriods(const AurumIndicatorPeriods &periods)
  {
   return periods.ema_m15_fast>0 && periods.ema_m15_slow>periods.ema_m15_fast &&
          periods.ema_h1_fast>0 && periods.ema_h1_slow>periods.ema_h1_fast &&
          periods.rsi>0 && periods.macd_fast>0 && periods.macd_slow>periods.macd_fast &&
          periods.macd_signal>0 && periods.adx>0 && periods.atr>0 &&
          periods.ema_h4_fast>0 && periods.ema_h4_slow>periods.ema_h4_fast;
  }

struct AurumIndicatorSnapshot
  {
   datetime m15_open;
   datetime h1_open;
   datetime decision_time;
   double ema_m15_fast;
   double ema_m15_slow;
   double ema_h1_fast;
   double ema_h1_slow;
   double rsi;
   double macd_main;
   double macd_signal;
   double adx;
   double plus_di;
   double minus_di;
   double atr;
   datetime h4_open;
   double ema_h4_fast;
   double ema_h4_slow;
   double prior_atr_mean;
   double range_price;
   double spread_price;
  };

struct AurumSetupHistory
  {
   int count;
   double pullback_ema;
   MqlRates bars[AURUM_SETUP_MAX_BARS];
  };

enum AurumIndicatorHandle
  {
   HANDLE_EMA_M15_FAST,
   HANDLE_EMA_M15_SLOW,
   HANDLE_EMA_H1_FAST,
   HANDLE_EMA_H1_SLOW,
   HANDLE_RSI,
   HANDLE_MACD,
   HANDLE_ADX,
   HANDLE_ATR,
   HANDLE_EMA_H4_FAST,
   HANDLE_EMA_H4_SLOW,
   AURUM_HANDLE_COUNT
  };

class AurumIndicators
  {
private:
   string                m_symbol;
   AurumIndicatorPeriods m_periods;
   int                   m_handles[AURUM_HANDLE_COUNT];

   AurumIndicatorStatus ReadClosedBar(const ENUM_TIMEFRAMES timeframe,const datetime decision_time,
                                     int &shift,datetime &open,int &bars)
     {
      const int seconds=PeriodSeconds(timeframe);
      shift=iBarShift(m_symbol,timeframe,decision_time-seconds,false);
      if(shift<1)
         return INDICATOR_WARMUP;
      open=iTime(m_symbol,timeframe,shift);
      bars=Bars(m_symbol,timeframe);
      if(open<=0 || bars<=shift || !SeriesInfoInteger(m_symbol,timeframe,SERIES_SYNCHRONIZED))
         return INDICATOR_WARMUP;
      const datetime close=open+seconds;
      if(close>decision_time || decision_time-close>=seconds)
         return INDICATOR_DATA_STALE;
      return INDICATORS_READY;
     }

   bool SameSeriesBar(const ENUM_TIMEFRAMES timeframe,const int shift,const datetime open,const int bars)
     {
      return iTime(m_symbol,timeframe,shift)==open && Bars(m_symbol,timeframe)==bars &&
             SeriesInfoInteger(m_symbol,timeframe,SERIES_SYNCHRONIZED);
     }

   bool ReadValue(const AurumIndicatorHandle slot,const int buffer_number,const int shift,
                  const int series_bars,const long warmup,double &value,AurumIndicatorStatus &status)
     {
      const int handle=m_handles[slot];
      if(handle==INVALID_HANDLE)
        {
         status=INDICATOR_HANDLE_FAILED;
         return false;
        }

      if(series_bars<warmup+shift)
        {
         status=INDICATOR_WARMUP;
         return false;
        }

      double values[1];
      // Request the buffer before checking readiness to trigger lazy tester calculations.
      const int copied=CopyBuffer(handle,buffer_number,shift,1,values);
      if(BarsCalculated(handle)<series_bars)
        {
         status=INDICATOR_WARMUP;
         return false;
        }
      if(copied!=1)
        {
         status=INDICATOR_COPY_FAILED;
         return false;
        }
      if(values[0]==EMPTY_VALUE || !MathIsValidNumber(values[0]))
        {
         status=INDICATOR_VALUE_INVALID;
         return false;
        }
      value=values[0];
      return true;
     }

   AurumIndicatorStatus ReadRegimeContext(const datetime decision_time,const int m15_bars,
                                          AurumIndicatorSnapshot &pending)
     {
      // ATR baseline excludes the decision bar. The price window includes it.
      if(m15_bars<(long)m_periods.atr+1+AURUM_REGIME_LOOKBACK+1)
         return INDICATOR_WARMUP;
      double atr_values[AURUM_REGIME_LOOKBACK];
      MqlRates rates[AURUM_REGIME_LOOKBACK+1];
      if(CopyBuffer(m_handles[HANDLE_ATR],0,2,AURUM_REGIME_LOOKBACK,atr_values)!=AURUM_REGIME_LOOKBACK ||
         CopyRates(m_symbol,PERIOD_M15,1,AURUM_REGIME_LOOKBACK+1,rates)!=AURUM_REGIME_LOOKBACK+1)
         return INDICATOR_COPY_FAILED;
      double mean=0;
      double low=rates[0].low;
      double high=rates[0].high;
      for(int index=0;index<=AURUM_REGIME_LOOKBACK;++index)
        {
         // CopyRates stores oldest first in physical memory.
         const datetime expected=decision_time-(AURUM_REGIME_LOOKBACK+1-index)*PeriodSeconds(PERIOD_M15);
         if(rates[index].time!=expected)
            return INDICATOR_DATA_STALE;
         if(!AurumValidOhlc(rates[index]))
            return INDICATOR_VALUE_INVALID;
         low=MathMin(low,rates[index].low);
         high=MathMax(high,rates[index].high);
         if(index<AURUM_REGIME_LOOKBACK)
           {
            if(!AurumPositiveNumber(atr_values[index]))
               return INDICATOR_VALUE_INVALID;
            mean+=atr_values[index]/AURUM_REGIME_LOOKBACK;
           }
        }
      const double point=SymbolInfoDouble(m_symbol,SYMBOL_POINT);
      const double spread=rates[AURUM_REGIME_LOOKBACK].spread*point;
      if(!AurumPositiveNumber(point) || !AurumPositiveNumber(spread) || !AurumPositiveNumber(mean))
         return INDICATOR_VALUE_INVALID;
      pending.prior_atr_mean=mean;
      pending.range_price=high-low;
      pending.spread_price=spread;
      return INDICATORS_READY;
     }

public:
   AurumIndicators()
     {
      for(int slot=0;slot<AURUM_HANDLE_COUNT;++slot)
         m_handles[slot]=INVALID_HANDLE;
     }

   bool Create(const string symbol,const AurumIndicatorPeriods &periods)
     {
      Release();
      if(!AurumValidIndicatorPeriods(periods))
         return false;
      m_symbol=symbol;
      m_periods=periods;
      m_handles[HANDLE_EMA_M15_FAST]=iMA(symbol,PERIOD_M15,periods.ema_m15_fast,0,MODE_EMA,PRICE_CLOSE);
      m_handles[HANDLE_EMA_M15_SLOW]=iMA(symbol,PERIOD_M15,periods.ema_m15_slow,0,MODE_EMA,PRICE_CLOSE);
      m_handles[HANDLE_EMA_H1_FAST]=iMA(symbol,PERIOD_H1,periods.ema_h1_fast,0,MODE_EMA,PRICE_CLOSE);
      m_handles[HANDLE_EMA_H1_SLOW]=iMA(symbol,PERIOD_H1,periods.ema_h1_slow,0,MODE_EMA,PRICE_CLOSE);
      m_handles[HANDLE_RSI]=iRSI(symbol,PERIOD_M15,periods.rsi,PRICE_CLOSE);
      m_handles[HANDLE_MACD]=iMACD(symbol,PERIOD_M15,periods.macd_fast,periods.macd_slow,periods.macd_signal,PRICE_CLOSE);
      m_handles[HANDLE_ADX]=iADXWilder(symbol,PERIOD_M15,periods.adx);
      m_handles[HANDLE_ATR]=iATR(symbol,PERIOD_M15,periods.atr);
      m_handles[HANDLE_EMA_H4_FAST]=iMA(symbol,PERIOD_H4,periods.ema_h4_fast,0,MODE_EMA,PRICE_CLOSE);
      m_handles[HANDLE_EMA_H4_SLOW]=iMA(symbol,PERIOD_H4,periods.ema_h4_slow,0,MODE_EMA,PRICE_CLOSE);
      for(int slot=0;slot<AURUM_HANDLE_COUNT;++slot)
         if(m_handles[slot]==INVALID_HANDLE)
           {
            Release();
            return false;
           }
      return true;
     }

   void Release()
     {
      for(int slot=0;slot<AURUM_HANDLE_COUNT;++slot)
        {
         if(m_handles[slot]!=INVALID_HANDLE)
            IndicatorRelease(m_handles[slot]);
         m_handles[slot]=INVALID_HANDLE;
        }
     }

   AurumIndicatorStatus ReadLatest(AurumIndicatorSnapshot &snapshot)
     {
      ZeroMemory(snapshot);
      if(m_handles[HANDLE_EMA_M15_FAST]==INVALID_HANDLE)
         return INDICATOR_HANDLE_FAILED;

      const int m15_shift=1;
      const int m15_seconds=PeriodSeconds(PERIOD_M15);
      const datetime m15_open=iTime(m_symbol,PERIOD_M15,m15_shift);
      const datetime m15_current=iTime(m_symbol,PERIOD_M15,0);
      if(m15_open<=0 || m15_current<=0)
         return INDICATOR_WARMUP;
      const datetime decision_time=m15_open+m15_seconds;
      if(m15_current!=decision_time)
         return INDICATOR_DATA_STALE;

      const int m15_bars=Bars(m_symbol,PERIOD_M15);
      if(m15_bars<=m15_shift || !SeriesInfoInteger(m_symbol,PERIOD_M15,SERIES_SYNCHRONIZED))
         return INDICATOR_WARMUP;

      AurumIndicatorSnapshot pending;
      int h1_shift,h4_shift,h1_bars,h4_bars;
      AurumIndicatorStatus status=ReadClosedBar(PERIOD_H1,decision_time,h1_shift,pending.h1_open,h1_bars);
      if(status!=INDICATORS_READY)
         return status;
      status=ReadClosedBar(PERIOD_H4,decision_time,h4_shift,pending.h4_open,h4_bars);
      if(status!=INDICATORS_READY)
         return status;
      const long macd_warmup=(long)m_periods.macd_slow+m_periods.macd_signal-1;
      const long adx_warmup=2*(long)m_periods.adx;
      if(!ReadValue(HANDLE_EMA_M15_FAST,0,m15_shift,m15_bars,m_periods.ema_m15_fast,pending.ema_m15_fast,status) ||
         !ReadValue(HANDLE_EMA_M15_SLOW,0,m15_shift,m15_bars,m_periods.ema_m15_slow,pending.ema_m15_slow,status) ||
         !ReadValue(HANDLE_EMA_H1_FAST,0,h1_shift,h1_bars,m_periods.ema_h1_fast,pending.ema_h1_fast,status) ||
         !ReadValue(HANDLE_EMA_H1_SLOW,0,h1_shift,h1_bars,m_periods.ema_h1_slow,pending.ema_h1_slow,status) ||
         !ReadValue(HANDLE_RSI,0,m15_shift,m15_bars,(long)m_periods.rsi+1,pending.rsi,status) ||
         !ReadValue(HANDLE_MACD,0,m15_shift,m15_bars,macd_warmup,pending.macd_main,status) ||
         !ReadValue(HANDLE_MACD,1,m15_shift,m15_bars,macd_warmup,pending.macd_signal,status) ||
         !ReadValue(HANDLE_ADX,0,m15_shift,m15_bars,adx_warmup,pending.adx,status) ||
         !ReadValue(HANDLE_ADX,1,m15_shift,m15_bars,adx_warmup,pending.plus_di,status) ||
         !ReadValue(HANDLE_ADX,2,m15_shift,m15_bars,adx_warmup,pending.minus_di,status) ||
         !ReadValue(HANDLE_ATR,0,m15_shift,m15_bars,(long)m_periods.atr+1,pending.atr,status) ||
         !ReadValue(HANDLE_EMA_H4_FAST,0,h4_shift,h4_bars,m_periods.ema_h4_fast,pending.ema_h4_fast,status) ||
         !ReadValue(HANDLE_EMA_H4_SLOW,0,h4_shift,h4_bars,m_periods.ema_h4_slow,pending.ema_h4_slow,status))
         return status;

      if(pending.ema_m15_fast<=0 || pending.ema_m15_slow<=0 ||
         pending.ema_h1_fast<=0 || pending.ema_h1_slow<=0 || pending.atr<0 ||
         pending.ema_h4_fast<=0 || pending.ema_h4_slow<=0 ||
         pending.rsi<0 || pending.rsi>100 || pending.adx<0 || pending.adx>100 ||
         pending.plus_di<0 || pending.plus_di>100 || pending.minus_di<0 || pending.minus_di>100)
         return INDICATOR_VALUE_INVALID;

      status=ReadRegimeContext(decision_time,m15_bars,pending);

      // Reject a mixed snapshot if bar positions changed while reading the buffers.
      if(!SameSeriesBar(PERIOD_M15,m15_shift,m15_open,m15_bars) ||
         iTime(m_symbol,PERIOD_M15,0)!=m15_current ||
         !SameSeriesBar(PERIOD_H1,h1_shift,pending.h1_open,h1_bars) ||
         !SameSeriesBar(PERIOD_H4,h4_shift,pending.h4_open,h4_bars))
         return INDICATOR_BAR_CHANGED;
      if(status!=INDICATORS_READY)
         return status;

      pending.m15_open=m15_open;
      pending.decision_time=decision_time;
      snapshot=pending;
      return INDICATORS_READY;
     }

   AurumIndicatorStatus ReadSetupHistory(const AurumIndicatorSnapshot &snapshot,const int count,
                                         AurumSetupHistory &history)
     {
      history.count=0;
      const int seconds=PeriodSeconds(PERIOD_M15);
      if(count<3 || count>AURUM_SETUP_MAX_BARS || snapshot.m15_open<=0 ||
         snapshot.m15_open+seconds!=snapshot.decision_time)
         return INDICATOR_VALUE_INVALID;

      const int bars=Bars(m_symbol,PERIOD_M15);
      if(bars<=count || !SeriesInfoInteger(m_symbol,PERIOD_M15,SERIES_SYNCHRONIZED))
         return INDICATOR_WARMUP;
      AurumIndicatorStatus status=INDICATORS_READY;
      if(!ReadValue(HANDLE_EMA_M15_FAST,0,2,bars,m_periods.ema_m15_fast,history.pullback_ema,status))
         return status;
      if(CopyRates(m_symbol,PERIOD_M15,1,count,history.bars)!=count)
         return INDICATOR_COPY_FAILED;
      if(!SameSeriesBar(PERIOD_M15,1,snapshot.m15_open,bars) ||
         iTime(m_symbol,PERIOD_M15,0)!=snapshot.decision_time)
         return INDICATOR_BAR_CHANGED;
      history.count=count;
      return INDICATORS_READY;
     }
  };

#endif
