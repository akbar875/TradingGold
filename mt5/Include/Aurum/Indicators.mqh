#ifndef AURUM_INDICATORS_MQH
#define AURUM_INDICATORS_MQH

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
  };

bool AurumValidIndicatorPeriods(const AurumIndicatorPeriods &periods)
  {
   return periods.ema_m15_fast>0 && periods.ema_m15_slow>periods.ema_m15_fast &&
          periods.ema_h1_fast>0 && periods.ema_h1_slow>periods.ema_h1_fast &&
          periods.rsi>0 && periods.macd_fast>0 && periods.macd_slow>periods.macd_fast &&
          periods.macd_signal>0 && periods.adx>0 && periods.atr>0;
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
   AURUM_HANDLE_COUNT
  };

class AurumIndicators
  {
private:
   string                m_symbol;
   AurumIndicatorPeriods m_periods;
   int                   m_handles[AURUM_HANDLE_COUNT];

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
      const int h1_seconds=PeriodSeconds(PERIOD_H1);
      const datetime m15_open=iTime(m_symbol,PERIOD_M15,m15_shift);
      const datetime m15_current=iTime(m_symbol,PERIOD_M15,0);
      if(m15_open<=0 || m15_current<=0)
         return INDICATOR_WARMUP;
      const datetime decision_time=m15_open+m15_seconds;
      if(m15_current!=decision_time)
         return INDICATOR_DATA_STALE;

      // A bar is eligible only if its nominal close is at or before the M15 cutoff.
      const int h1_shift=iBarShift(m_symbol,PERIOD_H1,decision_time-h1_seconds,false);
      if(h1_shift<1)
         return INDICATOR_WARMUP;
      const datetime h1_open=iTime(m_symbol,PERIOD_H1,h1_shift);
      const int m15_bars=Bars(m_symbol,PERIOD_M15);
      const int h1_bars=Bars(m_symbol,PERIOD_H1);
      if(h1_open<=0 || m15_bars<=m15_shift || h1_bars<=h1_shift ||
         !SeriesInfoInteger(m_symbol,PERIOD_M15,SERIES_SYNCHRONIZED) ||
         !SeriesInfoInteger(m_symbol,PERIOD_H1,SERIES_SYNCHRONIZED))
         return INDICATOR_WARMUP;
      const datetime h1_close=h1_open+h1_seconds;
      if(h1_close>decision_time || decision_time-h1_close>=h1_seconds)
         return INDICATOR_DATA_STALE;

      AurumIndicatorSnapshot pending;
      AurumIndicatorStatus status=INDICATORS_READY;
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
         !ReadValue(HANDLE_ATR,0,m15_shift,m15_bars,(long)m_periods.atr+1,pending.atr,status))
         return status;

      if(pending.ema_m15_fast<=0 || pending.ema_m15_slow<=0 ||
         pending.ema_h1_fast<=0 || pending.ema_h1_slow<=0 || pending.atr<0 ||
         pending.rsi<0 || pending.rsi>100 || pending.adx<0 || pending.adx>100 ||
         pending.plus_di<0 || pending.plus_di>100 || pending.minus_di<0 || pending.minus_di>100)
         return INDICATOR_VALUE_INVALID;

      // Reject a mixed snapshot if bar positions changed while reading the buffers.
      if(iTime(m_symbol,PERIOD_M15,m15_shift)!=m15_open ||
         iTime(m_symbol,PERIOD_M15,0)!=m15_current || iTime(m_symbol,PERIOD_H1,h1_shift)!=h1_open ||
         Bars(m_symbol,PERIOD_M15)!=m15_bars || Bars(m_symbol,PERIOD_H1)!=h1_bars ||
         !SeriesInfoInteger(m_symbol,PERIOD_M15,SERIES_SYNCHRONIZED) ||
         !SeriesInfoInteger(m_symbol,PERIOD_H1,SERIES_SYNCHRONIZED))
         return INDICATOR_BAR_CHANGED;

      pending.m15_open=m15_open;
      pending.h1_open=h1_open;
      pending.decision_time=decision_time;
      snapshot=pending;
      return INDICATORS_READY;
     }
  };

#endif
