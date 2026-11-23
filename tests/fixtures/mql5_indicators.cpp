#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <limits>
#include <string>
#include <tuple>
#include <vector>

using string = std::string;
using datetime = long long;

enum ENUM_TIMEFRAMES { PERIOD_M15 = 15, PERIOD_H1 = 60, PERIOD_H4 = 240 };
constexpr int INVALID_HANDLE = -1;
constexpr int MODE_EMA = 1;
constexpr int PRICE_CLOSE = 0;
constexpr int SERIES_SYNCHRONIZED = 1;
constexpr int SYMBOL_POINT = 2;
constexpr double EMPTY_VALUE = std::numeric_limits<double>::max();

struct MqlRates {
    datetime time;
    double open;
    double high;
    double low;
    double close;
    int spread;
};

struct Fixture {
    // Latest first. The normal M15 cutoff is 10:45. The eligible H1 opened at 09:00.
    std::array<datetime, 2> m15{38700, 37800};
    std::array<datetime, 4> h1{36000, 32400, 28800, 25200};
    std::array<datetime, 4> h4{28800, 14400, 3600, 1};
    int m15_bars = 250;
    int h1_bars = 250;
    int h4_bars = 250;
    bool synchronized = true;
    bool h4_synchronized = true;
    int next_handle = 0;
    int create_failure = INVALID_HANDLE;
    int copy_failure = INVALID_HANDLE;
    int calculated = -1;
    bool calculate_on_copy = false;
    bool move_m15_during_copy = false;
    bool move_h4_during_rates = false;
    bool rates_partial = false;
    bool atr_window_partial = false;
    bool rates_gap = false;
    bool rates_bad_ohlc = false;
    double newer_h1_ema = 2040.0;
    double newer_h4_ema = 2050.0;
    double prior_atr = 2.0;
    double point = 0.01;
    int historical_spread = 10;
    std::vector<int> releases;
    std::vector<std::tuple<int, int, int>> copies;
    std::vector<std::pair<ENUM_TIMEFRAMES, int>> periods;
    std::array<std::array<double, 3>, 10> values{{
        {2020.25}, {2019.5}, {2010.0}, {2000.0}, {63.5},
        {-1.25, -0.75}, {20.0, 30.0, 10.0}, {3.25}, {2015.0}, {1995.0}
    }};
} fixture;

int NewHandle(const string &symbol, ENUM_TIMEFRAMES timeframe, int period) {
    assert(symbol == "XAUUSDm");
    fixture.periods.emplace_back(timeframe, period);
    const int slot = fixture.next_handle++;
    return slot == fixture.create_failure ? INVALID_HANDLE : slot;
}

int iMA(const string &symbol, ENUM_TIMEFRAMES timeframe, int period, int offset, int method, int price) {
    assert(offset == 0 && method == MODE_EMA && price == PRICE_CLOSE);
    return NewHandle(symbol, timeframe, period);
}

int iRSI(const string &symbol, ENUM_TIMEFRAMES timeframe, int period, int price) {
    assert(price == PRICE_CLOSE);
    return NewHandle(symbol, timeframe, period);
}

int iMACD(const string &symbol, ENUM_TIMEFRAMES timeframe, int fast, int slow, int signal, int price) {
    assert(fast == 12 && slow == 26 && signal == 9 && price == PRICE_CLOSE);
    return NewHandle(symbol, timeframe, slow);
}

int iADXWilder(const string &symbol, ENUM_TIMEFRAMES timeframe, int period) {
    return NewHandle(symbol, timeframe, period);
}

int iATR(const string &symbol, ENUM_TIMEFRAMES timeframe, int period) {
    return NewHandle(symbol, timeframe, period);
}

bool IndicatorRelease(int handle) {
    fixture.releases.push_back(handle);
    return true;
}

int PeriodSeconds(ENUM_TIMEFRAMES timeframe) { return 60 * timeframe; }

datetime iTime(const string &, ENUM_TIMEFRAMES timeframe, int shift) {
    if (timeframe == PERIOD_M15)
        return fixture.m15.at(shift);
    return timeframe == PERIOD_H1 ? fixture.h1.at(shift) : fixture.h4.at(shift);
}

int iBarShift(const string &, ENUM_TIMEFRAMES timeframe, datetime timestamp, bool exact) {
    assert((timeframe == PERIOD_H1 || timeframe == PERIOD_H4) && !exact);
    const auto &bars = timeframe == PERIOD_H1 ? fixture.h1 : fixture.h4;
    for (std::size_t shift = 0; shift < bars.size(); ++shift) {
        if (bars[shift] <= timestamp)
            return static_cast<int>(shift);
    }
    return -1;
}

int Bars(const string &, ENUM_TIMEFRAMES timeframe) {
    if (timeframe == PERIOD_M15)
        return fixture.m15_bars;
    return timeframe == PERIOD_H1 ? fixture.h1_bars : fixture.h4_bars;
}

bool SeriesInfoInteger(const string &, ENUM_TIMEFRAMES timeframe, int property) {
    assert(property == SERIES_SYNCHRONIZED);
    return fixture.synchronized && (timeframe != PERIOD_H4 || fixture.h4_synchronized);
}

int BarsCalculated(int handle) {
    if (fixture.calculated >= 0)
        return fixture.calculated;
    return Bars("", fixture.periods.at(handle).first);
}

int CopyBuffer(int handle, int buffer, int shift, int count, double (&values)[1]) {
    assert(shift >= 1 && count == 1);
    fixture.copies.emplace_back(handle, buffer, shift);
    if (fixture.calculate_on_copy)
        fixture.calculated = -1;
    if (handle == fixture.copy_failure)
        return 0;
    values[0] = fixture.values.at(handle).at(buffer);
    if (fixture.periods.at(handle).first == PERIOD_H1 && fixture.h1.at(shift) >= 36000)
        values[0] = fixture.newer_h1_ema;
    if (fixture.periods.at(handle).first == PERIOD_H4 && fixture.h4.at(shift) >= 28800)
        values[0] = fixture.newer_h4_ema;
    if (fixture.move_m15_during_copy) {
        fixture.m15 = {39600, 38700};
        fixture.move_m15_during_copy = false;
    }
    return 1;
}

bool MathIsValidNumber(double value) { return std::isfinite(value); }
double MathMin(double left, double right) { return std::min(left, right); }
double MathMax(double left, double right) { return std::max(left, right); }

template <typename T> void ZeroMemory(T &value) { value = {}; }

template <std::size_t Size>
int CopyBuffer(int handle, int buffer, int shift, int count, double (&values)[Size]);

template <std::size_t Size>
int CopyRates(const string &, ENUM_TIMEFRAMES timeframe, int shift, int count, MqlRates (&rates)[Size]) {
    assert(timeframe == PERIOD_M15 && shift == 1 && count == static_cast<int>(Size));
    if (fixture.rates_partial)
        return count - 1;
    for (int index = 0; index < count; ++index) {
        const datetime time = fixture.m15[1] - (count - 1 - index) * 900;
        rates[index] = {time, 2020.0, 2022.0, 2018.0, 2021.0, 0};
    }
    rates[count - 1].spread = fixture.historical_spread;
    if (fixture.rates_gap)
        rates[0].time -= 900;
    if (fixture.rates_bad_ohlc)
        rates[0].high = 2019.0;
    if (fixture.move_h4_during_rates)
        fixture.h4 = {43200, 28800, 14400, 3600};
    return count;
}

double SymbolInfoDouble(const string &symbol, int property) {
    assert(symbol == "XAUUSDm" && property == SYMBOL_POINT);
    return fixture.point;
}

#include "Aurum/Regime.mqh"

template <std::size_t Size>
int CopyBuffer(int handle, int buffer, int shift, int count, double (&values)[Size]) {
    assert(handle == HANDLE_ATR && buffer == 0 && shift == 2 &&
           count == AURUM_REGIME_LOOKBACK && count == static_cast<int>(Size));
    fixture.copies.emplace_back(handle, buffer, shift);
    if (fixture.atr_window_partial)
        return count - 1;
    std::fill_n(values, count, fixture.prior_atr);
    return count;
}

const AurumIndicatorPeriods defaults{20, 50, 50, 200, 14, 12, 26, 9, 14, 14, 50, 200};
const AurumRegimeSettings regime_defaults{25.0, 2.0, 0.25, 4.0};

void CheckSnapshot() {
    fixture = {};
    AurumIndicators indicators;
    AurumIndicatorSnapshot snapshot;
    assert(indicators.Create("XAUUSDm", defaults));
    assert((fixture.periods == std::vector<std::pair<ENUM_TIMEFRAMES, int>>{
        {PERIOD_M15, 20}, {PERIOD_M15, 50}, {PERIOD_H1, 50}, {PERIOD_H1, 200},
        {PERIOD_M15, 14}, {PERIOD_M15, 26}, {PERIOD_M15, 14}, {PERIOD_M15, 14},
        {PERIOD_H4, 50}, {PERIOD_H4, 200}
    }));
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(snapshot.m15_open == 37800 && snapshot.h1_open == 32400 && snapshot.decision_time == 38700);
    assert(snapshot.ema_m15_fast == 2020.25 && snapshot.ema_m15_slow == 2019.5);
    assert(snapshot.ema_h1_fast == 2010.0 && snapshot.ema_h1_slow == 2000.0);
    assert(snapshot.h4_open == 14400 && snapshot.ema_h4_fast == 2015.0 && snapshot.ema_h4_slow == 1995.0);
    assert(snapshot.prior_atr_mean == 2.0 && snapshot.range_price == 4.0 && snapshot.spread_price == 0.1);
    assert(snapshot.rsi == 63.5 && snapshot.macd_main == -1.25 && snapshot.macd_signal == -0.75);
    assert(snapshot.adx == 20.0 && snapshot.plus_di == 30.0 && snapshot.minus_di == 10.0 && snapshot.atr == 3.25);
    assert((fixture.copies == std::vector<std::tuple<int, int, int>>{
        {0, 0, 1}, {1, 0, 1}, {2, 0, 1}, {3, 0, 1}, {4, 0, 1},
        {5, 0, 1}, {5, 1, 1}, {6, 0, 1}, {6, 1, 1}, {6, 2, 1}, {7, 0, 1},
        {8, 0, 1}, {9, 0, 1}, {7, 0, 2}
    }));

    // The H1 series has advanced since the 10:45 decision. The 10:00 H1 (now
    // closed) remains ineligible because its close falls after that cutoff.
    fixture.h1 = {39600, 36000, 32400, 28800};
    fixture.newer_h1_ema = 2063.5;
    fixture.copies.clear();
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(snapshot.h1_open == 32400 && std::get<2>(fixture.copies.at(2)) == 2);
    assert(snapshot.ema_h1_fast == 2010.0 && snapshot.ema_h1_slow == 2000.0);

    // At exactly 11:00 the 10:00 H1 becomes eligible.
    fixture.m15 = {39600, 38700};
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(snapshot.h1_open == 36000 && snapshot.decision_time == 39600);
    assert(snapshot.ema_h1_fast == fixture.newer_h1_ema);

    fixture.m15 = {42300, 41400};
    fixture.h1 = {43200, 39600, 36000, 32400};
    fixture.h4 = {43200, 28800, 14400, 3600};
    fixture.newer_h4_ema = 2100.0;
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(snapshot.h4_open == 14400 && snapshot.ema_h4_fast == 2015.0);
    fixture.m15 = {43200, 42300};
    fixture.h4 = {28800, 14400, 3600, 1};
    assert(indicators.ReadLatest(snapshot) == INDICATOR_WARMUP);
    fixture.h4 = {43200, 28800, 14400, 3600};
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(snapshot.h4_open == 28800 && snapshot.ema_h4_fast == 2100.0);
    indicators.Release();
}

void CheckFailuresAndRetry() {
    fixture = {};
    AurumIndicators indicators;
    AurumIndicatorSnapshot snapshot;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_HANDLE_FAILED);
    AurumIndicatorPeriods invalid = defaults;
    invalid.ema_h1_slow = invalid.ema_h1_fast;
    assert(!indicators.Create("XAUUSDm", invalid) && fixture.next_handle == 0);
    invalid = defaults;
    invalid.ema_h4_slow = invalid.ema_h4_fast;
    assert(!indicators.Create("XAUUSDm", invalid) && fixture.next_handle == 0);
    assert(indicators.Create("XAUUSDm", defaults));

    fixture.synchronized = false;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_WARMUP && fixture.copies.empty());
    fixture.synchronized = true;
    fixture.h1 = {36000, 28800, 25200, 21600};
    assert(indicators.ReadLatest(snapshot) == INDICATOR_DATA_STALE && fixture.copies.empty());
    fixture.h1 = {36000, 32400, 28800, 25200};
    fixture.h1_bars = 200;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_WARMUP);
    fixture.h1_bars = 201;
    fixture.calculated = 200;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_WARMUP);
    fixture.calculate_on_copy = true;
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    fixture.calculate_on_copy = false;

    fixture.copy_failure = HANDLE_ATR;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_COPY_FAILED);
    assert(snapshot.decision_time == 0 && snapshot.ema_m15_fast == 0 && snapshot.atr == 0);
    fixture.copy_failure = INVALID_HANDLE;
    for (double value : {EMPTY_VALUE, std::numeric_limits<double>::quiet_NaN(), -1.0}) {
        fixture.values[HANDLE_ATR][0] = value;
        assert(indicators.ReadLatest(snapshot) == INDICATOR_VALUE_INVALID && snapshot.m15_open == 0);
    }
    fixture.values[HANDLE_ATR][0] = 0;
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY && snapshot.atr == 0);

    fixture.move_m15_during_copy = true;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_BAR_CHANGED && snapshot.h1_open == 0);
    assert(indicators.ReadLatest(snapshot) == INDICATOR_WARMUP);
    fixture.h1 = {39600, 36000, 32400, 28800};
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    fixture.m15[0] += 900;
    assert(indicators.ReadLatest(snapshot) == INDICATOR_DATA_STALE);
    indicators.Release();
}

void CheckLifecycle() {
    fixture = {};
    AurumIndicators indicators;
    fixture.create_failure = HANDLE_EMA_H4_FAST;
    assert(!indicators.Create("XAUUSDm", defaults));
    assert((fixture.releases == std::vector<int>{0, 1, 2, 3, 4, 5, 6, 7, 9}));
    indicators.Release();
    assert(fixture.releases.size() == 9);
    fixture = {};
    assert(indicators.Create("XAUUSDm", defaults));
    indicators.Release();
    indicators.Release();
    assert(fixture.releases.size() == 10);
    fixture = {};
    assert(indicators.Create("XAUUSDm", defaults));
    AurumIndicatorSnapshot snapshot;
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    indicators.Release();
}

void ExpectRegime(AurumMarketRegime regime, AurumRegimeDirection direction, AurumRegimeReason reason,
                  const AurumRegimeResult &result) {
    assert(result.regime == regime && result.direction == direction && result.reason == reason);
}

void CheckRegimeBoundariesAndInvalidation() {
    fixture = {};
    AurumIndicators indicators;
    AurumIndicatorSnapshot snapshot;
    AurumRegimeResult result;
    assert(indicators.Create("XAUUSDm", defaults));
    auto evaluate = [&](AurumIndicatorStatus expected = INDICATORS_READY) {
        const auto status = indicators.ReadLatest(snapshot);
        assert(status == expected);
        AurumClassifyRegime(status, snapshot, regime_defaults, result);
    };
    auto expect_unsafe_data = [&](AurumIndicatorStatus status) {
        evaluate(status);
        ExpectRegime(HIGH_VOLATILITY_UNSAFE, REGIME_DIRECTION_BLOCKED, REGIME_DATA_UNSAFE, result);
    };

    evaluate();
    ExpectRegime(RANGE, REGIME_DIRECTION_BLOCKED, REGIME_CONSOLIDATION, result);
    fixture.prior_atr = 1.0;
    fixture.values[HANDLE_ATR][0] = 1.5;
    evaluate(); // Range width is exactly four times the baseline.
    ExpectRegime(RANGE, REGIME_DIRECTION_BLOCKED, REGIME_CONSOLIDATION, result);
    fixture.prior_atr = 0.99;
    evaluate();
    ExpectRegime(REGIME_UNCLASSIFIED, REGIME_DIRECTION_BLOCKED, REGIME_INCONCLUSIVE, result);
    fixture.prior_atr = 2.0;
    fixture.values[HANDLE_ADX][0] = 25.0;
    evaluate(); // ADX equal to the threshold can confirm a trend.
    ExpectRegime(TREND_UP, REGIME_BUY_ALLOWED, REGIME_TREND_CONFIRMED, result);

    std::swap(fixture.values[HANDLE_EMA_H4_FAST], fixture.values[HANDLE_EMA_H4_SLOW]);
    evaluate();
    ExpectRegime(REGIME_UNCLASSIFIED, REGIME_DIRECTION_BLOCKED, REGIME_HTF_CONFLICT, result);
    std::swap(fixture.values[HANDLE_EMA_H1_FAST], fixture.values[HANDLE_EMA_H1_SLOW]);
    std::swap(fixture.values[HANDLE_EMA_M15_FAST], fixture.values[HANDLE_EMA_M15_SLOW]);
    evaluate(); // Higher timeframes and EMA M15 agree, but DI still points up.
    ExpectRegime(REGIME_UNCLASSIFIED, REGIME_DIRECTION_BLOCKED, REGIME_INCONCLUSIVE, result);
    std::swap(fixture.values[HANDLE_ADX][1], fixture.values[HANDLE_ADX][2]);
    evaluate();
    ExpectRegime(TREND_DOWN, REGIME_SELL_ALLOWED, REGIME_TREND_CONFIRMED, result);

    fixture.values[HANDLE_ATR][0] = 4.0;
    fixture.historical_spread = 50;
    evaluate(); // A spike at the exact limit takes priority when both guards fail.
    ExpectRegime(HIGH_VOLATILITY_UNSAFE, REGIME_DIRECTION_BLOCKED, REGIME_ATR_SPIKE, result);
    fixture.values[HANDLE_ATR][0] = 3.99;
    evaluate();
    ExpectRegime(HIGH_VOLATILITY_UNSAFE, REGIME_DIRECTION_BLOCKED, REGIME_SPREAD_TOO_WIDE, result);
    fixture.historical_spread = 49;
    evaluate();
    ExpectRegime(TREND_DOWN, REGIME_SELL_ALLOWED, REGIME_TREND_CONFIRMED, result);

    fixture.h4_bars = 200;
    expect_unsafe_data(INDICATOR_WARMUP);
    assert(snapshot.decision_time == 0);
    fixture.h4_bars = 250;
    fixture.h4_synchronized = false;
    expect_unsafe_data(INDICATOR_WARMUP);
    fixture.h4_synchronized = true;
    fixture.h4 = {28800, 3600, 1, 0};
    expect_unsafe_data(INDICATOR_DATA_STALE);
    fixture.h4 = {28800, 14400, 3600, 1};
    fixture.move_h4_during_rates = true;
    expect_unsafe_data(INDICATOR_BAR_CHANGED);
    fixture.move_h4_during_rates = false;
    fixture.atr_window_partial = true;
    expect_unsafe_data(INDICATOR_COPY_FAILED);
    fixture.atr_window_partial = false;
    fixture.rates_partial = true;
    expect_unsafe_data(INDICATOR_COPY_FAILED);
    fixture.rates_partial = false;
    fixture.rates_gap = true;
    expect_unsafe_data(INDICATOR_DATA_STALE);
    fixture.rates_gap = false;
    fixture.rates_bad_ohlc = true;
    expect_unsafe_data(INDICATOR_VALUE_INVALID);
    fixture.rates_bad_ohlc = false;
    fixture.prior_atr = EMPTY_VALUE;
    expect_unsafe_data(INDICATOR_VALUE_INVALID);
    fixture.prior_atr = 0.0;
    expect_unsafe_data(INDICATOR_VALUE_INVALID);
    fixture.prior_atr = 2.0;
    fixture.historical_spread = 0;
    expect_unsafe_data(INDICATOR_VALUE_INVALID);
    fixture.historical_spread = 10;
    fixture.point = -1.0;
    expect_unsafe_data(INDICATOR_VALUE_INVALID);
    fixture.point = 0.01;
    fixture.values[HANDLE_ATR][0] = 0.0;
    expect_unsafe_data(INDICATORS_READY);
    fixture.values[HANDLE_ATR][0] = 3.25;
    evaluate();
    ExpectRegime(TREND_DOWN, REGIME_SELL_ALLOWED, REGIME_TREND_CONFIRMED, result);

    AurumRegimeSettings invalid = regime_defaults;
    invalid.min_trend_adx = 101.0;
    assert(!AurumValidRegimeSettings(invalid));
    invalid = regime_defaults;
    invalid.atr_spike_ratio = 1.0;
    assert(!AurumValidRegimeSettings(invalid));
    invalid = regime_defaults;
    invalid.max_spread_atr_ratio = std::numeric_limits<double>::quiet_NaN();
    AurumClassifyRegime(INDICATORS_READY, snapshot, invalid, result);
    ExpectRegime(HIGH_VOLATILITY_UNSAFE, REGIME_DIRECTION_BLOCKED, REGIME_DATA_UNSAFE, result);

    indicators.Release();
    expect_unsafe_data(INDICATOR_HANDLE_FAILED);
    fixture.next_handle = 0;
    assert(indicators.Create("XAUUSDm", defaults));
    evaluate();
    ExpectRegime(TREND_DOWN, REGIME_SELL_ALLOWED, REGIME_TREND_CONFIRMED, result);
    indicators.Release();
}

int main() {
    CheckSnapshot();
    CheckFailuresAndRetry();
    CheckLifecycle();
    CheckRegimeBoundariesAndInvalidation();
}
