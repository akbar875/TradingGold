#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <limits>
#include <string>
#include <tuple>
#include <vector>

using string = std::string;
using datetime = long long;
using uint = unsigned int;
using ulong = unsigned long;

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

struct MqlTick {
    datetime time;
    double bid;
    double ask;
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
    bool move_m15_during_rates = false;
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
    assert(timeframe == PERIOD_M15 && shift == 1 && count <= static_cast<int>(Size));
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
    if (fixture.move_m15_during_rates)
        fixture.m15 = {39600, 38700};
    return count;
}

double SymbolInfoDouble(const string &symbol, int property) {
    assert(symbol == "XAUUSDm" && property == SYMBOL_POINT);
    return fixture.point;
}

constexpr int FILE_READ = 1;
constexpr int FILE_WRITE = 2;
constexpr int FILE_BIN = 4;

struct ClaimFile {
    bool locked;
    bool fail_write;
    bool fail_flush;
    int error;
    ulong size;
    long watermark;
} claim_file;

int StringLen(const string &value) { return static_cast<int>(value.size()); }
int StringGetCharacter(const string &value, int index) { return value.at(index); }
string StringFormat(const string &format, uint value) {
    assert(format == "%04X");
    string encoded;
    for (int shift = 12; shift >= 0; shift -= 4)
        encoded += "0123456789ABCDEF"[(value >> shift) & 15];
    return encoded;
}

int FileOpen(const string &path, int flags) {
    assert(!path.empty() && flags == (FILE_READ | FILE_WRITE | FILE_BIN));
    if (claim_file.locked)
        return INVALID_HANDLE;
    claim_file.locked = true;
    return 1;
}
void ResetLastError() { claim_file.error = 0; }
int GetLastError() { return claim_file.error; }
ulong FileSize(int) { return claim_file.size; }
long FileReadLong(int) { return claim_file.watermark; }
bool FileSeek(int, long offset, int origin) { return offset == 0 && origin == SEEK_SET; }
uint FileWriteLong(int, long value) {
    if (claim_file.fail_write)
        return 0;
    claim_file.watermark = value;
    claim_file.size = sizeof(long);
    return sizeof(long);
}
void FileFlush(int) { claim_file.error = claim_file.fail_flush ? 1 : 0; }
void FileClose(int) { claim_file.locked = false; }

#include "Aurum/Setups.mqh"
#include "Aurum/SetupClaims.mqh"

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

const AurumSetupSettings setup_defaults{12, 3, 0.30, 0.60, 1.50, 3.00};

void CheckSetupHistory() {
    fixture = {};
    AurumIndicators indicators;
    AurumIndicatorSnapshot snapshot;
    AurumSetupHistory history;
    assert(indicators.Create("XAUUSDm", defaults));
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(indicators.ReadSetupHistory(snapshot, 17, history) == INDICATORS_READY);
    assert(history.count == 17 && history.bars[16].time == snapshot.m15_open);
    assert(history.bars[0].time == snapshot.decision_time - 17 * 900);
    assert((fixture.copies.back() == std::tuple<int, int, int>{HANDLE_EMA_M15_FAST, 0, 2}));

    fixture.rates_partial = true;
    assert(indicators.ReadSetupHistory(snapshot, 17, history) == INDICATOR_COPY_FAILED);
    assert(history.count == 0);
    fixture.rates_partial = false;
    fixture.move_m15_during_rates = true;
    assert(indicators.ReadSetupHistory(snapshot, 17, history) == INDICATOR_BAR_CHANGED);
    assert(history.count == 0);
    fixture.move_m15_during_rates = false;
    fixture.h1 = {39600, 36000, 32400, 28800};
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(indicators.ReadSetupHistory(snapshot, 17, history) == INDICATORS_READY);
    indicators.Release();
}

struct SetupFixture {
    AurumIndicatorSnapshot snapshot{};
    AurumRegimeResult regime{TREND_UP, REGIME_BUY_ALLOWED, REGIME_TREND_CONFIRMED};
    AurumSetupHistory history{};
    MqlTick tick{38700, 101.25, 101.375};
    AurumSetupSettings settings = setup_defaults;

    explicit SetupFixture(bool breakout) {
        snapshot.m15_open = 37800;
        snapshot.decision_time = 38700;
        snapshot.prior_atr_mean = 1.0;
        history.count = 17;
        history.pullback_ema = breakout ? 96.0 : 100.0;
        for (int index = 0; index < history.count; ++index)
            history.bars[index] = {snapshot.decision_time - (history.count - index) * 900,
                                   99.0, breakout ? 100.0 : 102.0, 98.0, 99.5, 0};
        history.bars[14] = {36000, 99.75, 101.25, 99.625, 101.0, 0};
        history.bars[15] = {36900, 100.75, 101.0, 99.875, 100.625, 0};
        history.bars[16] = {37800, 100.5, 101.375, 100.25, 101.25, 0};
    }

    void Mirror() {
        regime = {TREND_DOWN, REGIME_SELL_ALLOWED, REGIME_TREND_CONFIRMED};
        history.pullback_ema = 200.0 - history.pullback_ema;
        for (int index = 0; index < history.count; ++index) {
            MqlRates &bar = history.bars[index];
            const double high = bar.high;
            bar.high = 200.0 - bar.low;
            bar.low = 200.0 - high;
            bar.open = 200.0 - bar.open;
            bar.close = 200.0 - bar.close;
        }
        tick.bid = 98.625;
        tick.ask = 98.75;
    }

    AurumSetupResult Evaluate() const {
        AurumSetupResult result{SETUP_BUY, TREND_PULLBACK, SETUP_CONFIRMED, 1, 1.0, 1.0};
        AurumEvaluateSetup(snapshot, regime, history, settings, tick, result);
        return result;
    }

    void ExpectWait(AurumSetupReason reason) const {
        const auto result = Evaluate();
        assert(result.action == SETUP_WAIT && result.kind == NO_SETUP && result.reason == reason);
        assert(result.bar_time == 0 && result.key_level == 0 && result.invalidation == 0);
    }
};

void CheckClosedBarSetups() {
    for (bool breakout : {false, true}) {
        SetupFixture input(breakout);
        const AurumSetupKind expected = breakout ? BREAKOUT_RETEST : TREND_PULLBACK;
        const auto buy = input.Evaluate();
        assert(buy.action == SETUP_BUY && buy.kind == expected && buy.reason == SETUP_CONFIRMED);
        assert(buy.bar_time == 37800 && buy.key_level == 100.0 && buy.invalidation == 99.875);
        // Bars outside the committed window, including a hypothetical future bar, are ignored.
        input.history.bars[17] = {38700, 50.0, 300.0, 1.0, 30.0, 0};
        assert(input.Evaluate().kind == expected);
        input.Mirror();
        const auto sell = input.Evaluate();
        assert(sell.action == SETUP_SELL && sell.kind == expected && sell.key_level == 100.0);
        assert(sell.invalidation == 100.125);
        input.tick.bid = 98.0;
        input.ExpectWait(PRICE_CHASED);
    }

    SetupFixture input(true);
    input.history.pullback_ema = 100.0;
    assert(input.Evaluate().kind == BREAKOUT_RETEST); // Both patterns qualify, one result wins.
    input = SetupFixture(true);
    input.history.bars[16].close = 101.0;
    input.ExpectWait(NO_VALID_SETUP); // High pierced retest high, closed price did not.
    input = SetupFixture(true);
    input.history.bars[14].open = 100.0;
    input.history.bars[14].low = 98.0;
    input.ExpectWait(NO_VALID_SETUP); // Breakout body too small.
    input = SetupFixture(true);
    input.history.bars[15].close = 99.9;
    input.ExpectWait(NO_VALID_SETUP); // Retest closed back inside.
    input = SetupFixture(true);
    input.history.bars[13] = input.history.bars[14];
    input.history.bars[13].time = 35100;
    input.history.bars[14] = {36000, 100.5, 100.6, 99.75, 100.25, 0};
    assert(input.Evaluate().kind == BREAKOUT_RETEST); // Level remains frozen from before breakout.
    input.history.bars[14].close = 99.9;
    input.ExpectWait(NO_VALID_SETUP); // An intervening close cancels the breakout.
    input = SetupFixture(true);
    input.history.bars[12] = input.history.bars[14];
    input.history.bars[12].time = 34200;
    input.history.bars[13] = {35100, 100.5, 100.6, 100.1, 100.25, 0};
    input.history.bars[14] = {36000, 100.5, 100.6, 100.1, 100.25, 0};
    assert(input.Evaluate().kind == BREAKOUT_RETEST); // Exactly three bars to retest.
    input = SetupFixture(true);
    input.history.bars[11] = input.history.bars[14];
    input.history.bars[11].time = 33300;
    input.history.bars[12] = {34200, 100.5, 100.6, 100.1, 100.25, 0};
    input.history.bars[13] = {35100, 100.5, 100.6, 100.1, 100.25, 0};
    input.history.bars[14] = {36000, 100.5, 100.6, 100.1, 100.25, 0};
    input.ExpectWait(NO_VALID_SETUP); // Breakout four bars before retest exceeds the limit.
    input = SetupFixture(false);
    input.history.bars[16].low = 99.875;
    input.ExpectWait(NO_VALID_SETUP); // Confirmation wick reached the invalidation.
    input = SetupFixture(false);
    input.tick.ask = 101.5;
    assert(input.Evaluate().action == SETUP_BUY);
    input.tick.ask = 101.501;
    input.ExpectWait(PRICE_CHASED);
    input.tick = {38700, 99.875, 100.0};
    input.ExpectWait(SETUP_INVALIDATED);
    input.tick = {38699, 101.25, 101.375};
    input.ExpectWait(SETUP_QUOTE_INVALID);
    input.tick.time = 39600;
    input.ExpectWait(SETUP_QUOTE_INVALID);
    input.tick = {38700, 101.25, 101.0};
    input.ExpectWait(SETUP_QUOTE_INVALID);
    input.tick.ask = 101.375;
    input.settings.max_stop_atr = 1.0;
    input.ExpectWait(SETUP_STOP_DISTANCE);
    input = SetupFixture(false);
    input.regime = {RANGE, REGIME_DIRECTION_BLOCKED, REGIME_CONSOLIDATION};
    input.ExpectWait(SETUP_REGIME_BLOCKED);
    input = SetupFixture(false);
    input.history.bars[0].time += 900;
    input.ExpectWait(SETUP_DATA_INVALID);
    input = SetupFixture(false);
    input.history.bars[0].low = EMPTY_VALUE;
    input.ExpectWait(SETUP_DATA_INVALID);
    input = SetupFixture(false);
    input.settings.zone_atr = std::numeric_limits<double>::quiet_NaN();
    input.ExpectWait(SETUP_DATA_INVALID);
}

void CheckSetupClaims() {
    claim_file = {};
    const string path = AurumSetupClaimPath("XAUUSDm");
    assert(path == "Aurum_setup_m15_005800410055005500530044006D.bin");
    assert(path != AurumSetupClaimPath("XAUUSDM"));
    datetime watermark = 0;
    claim_file.locked = true;
    assert(AurumClaimSetupBar(path, 37800, false, watermark) == SETUP_STATE_UNAVAILABLE);
    assert(watermark == 0);
    claim_file.locked = false;
    assert(AurumClaimSetupBar(path, 37800, false, watermark) == SETUP_CLAIMED);
    assert(AurumClaimSetupBar(path, 37800, false, watermark) == DUPLICATE_SIGNAL);
    datetime after_restart = 0;
    assert(AurumClaimSetupBar(path, 37800, false, after_restart) == DUPLICATE_SIGNAL);
    assert(AurumClaimSetupBar(path, 36900, false, after_restart) == DUPLICATE_SIGNAL);
    claim_file.fail_write = true;
    assert(AurumClaimSetupBar(path, 38700, false, after_restart) == SETUP_STATE_UNAVAILABLE);
    assert(after_restart == 37800 && !claim_file.locked);
    claim_file.fail_write = false;
    assert(AurumClaimSetupBar(path, 38700, false, after_restart) == SETUP_CLAIMED);
    claim_file.fail_flush = true;
    assert(AurumClaimSetupBar(path, 39600, false, after_restart) == SETUP_STATE_UNAVAILABLE);
    assert(after_restart == 38700 && !claim_file.locked);
    claim_file.size = 1;
    assert(AurumClaimSetupBar(path, 40500, false, after_restart) == SETUP_STATE_UNAVAILABLE);
    datetime tester = 0;
    assert(AurumClaimSetupBar(path, 37800, true, tester) == SETUP_CLAIMED);
    assert(AurumClaimSetupBar(path, 37800, true, tester) == DUPLICATE_SIGNAL);
    tester = 0;
    assert(AurumClaimSetupBar(path, 37800, true, tester) == SETUP_CLAIMED);
}

int main() {
    CheckSnapshot();
    CheckFailuresAndRetry();
    CheckLifecycle();
    CheckRegimeBoundariesAndInvalidation();
    CheckSetupHistory();
    CheckClosedBarSetups();
    CheckSetupClaims();
}
