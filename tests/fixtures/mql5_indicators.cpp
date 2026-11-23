#include <array>
#include <cassert>
#include <cmath>
#include <limits>
#include <string>
#include <tuple>
#include <vector>

using string = std::string;
using datetime = long long;

enum ENUM_TIMEFRAMES { PERIOD_M15 = 15, PERIOD_H1 = 60 };
constexpr int INVALID_HANDLE = -1;
constexpr int MODE_EMA = 1;
constexpr int PRICE_CLOSE = 0;
constexpr int SERIES_SYNCHRONIZED = 1;
constexpr double EMPTY_VALUE = std::numeric_limits<double>::max();

struct Fixture {
    // Latest first. The normal M15 cutoff is 10:45. The eligible H1 opened at 09:00.
    std::array<datetime, 2> m15{38700, 37800};
    std::array<datetime, 4> h1{36000, 32400, 28800, 25200};
    int m15_bars = 250;
    int h1_bars = 250;
    bool synchronized = true;
    int next_handle = 0;
    int create_failure = INVALID_HANDLE;
    int copy_failure = INVALID_HANDLE;
    int calculated = -1;
    bool calculate_on_copy = false;
    bool move_m15_during_copy = false;
    double newer_h1_ema = 2040.0;
    std::vector<int> releases;
    std::vector<std::tuple<int, int, int>> copies;
    std::vector<std::pair<ENUM_TIMEFRAMES, int>> periods;
    std::array<std::array<double, 3>, 8> values{{
        {2020.25}, {2019.5}, {2010.0}, {2000.0}, {63.5},
        {-1.25, -0.75}, {20.0, 30.0, 10.0}, {3.25}
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
    return timeframe == PERIOD_M15 ? fixture.m15.at(shift) : fixture.h1.at(shift);
}

int iBarShift(const string &, ENUM_TIMEFRAMES timeframe, datetime timestamp, bool exact) {
    assert(timeframe == PERIOD_H1 && !exact);
    for (std::size_t shift = 0; shift < fixture.h1.size(); ++shift) {
        if (fixture.h1[shift] <= timestamp)
            return static_cast<int>(shift);
    }
    return -1;
}

int Bars(const string &, ENUM_TIMEFRAMES timeframe) {
    return timeframe == PERIOD_M15 ? fixture.m15_bars : fixture.h1_bars;
}

bool SeriesInfoInteger(const string &, ENUM_TIMEFRAMES, int property) {
    assert(property == SERIES_SYNCHRONIZED);
    return fixture.synchronized;
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
    if (fixture.move_m15_during_copy) {
        fixture.m15 = {39600, 38700};
        fixture.move_m15_during_copy = false;
    }
    return 1;
}

bool MathIsValidNumber(double value) { return std::isfinite(value); }

template <typename T> void ZeroMemory(T &value) { value = {}; }

#include "Aurum/Indicators.mqh"

const AurumIndicatorPeriods defaults{20, 50, 50, 200, 14, 12, 26, 9, 14, 14};

void CheckSnapshot() {
    fixture = {};
    AurumIndicators indicators;
    AurumIndicatorSnapshot snapshot;
    assert(indicators.Create("XAUUSDm", defaults));
    assert((fixture.periods == std::vector<std::pair<ENUM_TIMEFRAMES, int>>{
        {PERIOD_M15, 20}, {PERIOD_M15, 50}, {PERIOD_H1, 50}, {PERIOD_H1, 200},
        {PERIOD_M15, 14}, {PERIOD_M15, 26}, {PERIOD_M15, 14}, {PERIOD_M15, 14}
    }));
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    assert(snapshot.m15_open == 37800 && snapshot.h1_open == 32400 && snapshot.decision_time == 38700);
    assert(snapshot.ema_m15_fast == 2020.25 && snapshot.ema_m15_slow == 2019.5);
    assert(snapshot.ema_h1_fast == 2010.0 && snapshot.ema_h1_slow == 2000.0);
    assert(snapshot.rsi == 63.5 && snapshot.macd_main == -1.25 && snapshot.macd_signal == -0.75);
    assert(snapshot.adx == 20.0 && snapshot.plus_di == 30.0 && snapshot.minus_di == 10.0 && snapshot.atr == 3.25);
    assert((fixture.copies == std::vector<std::tuple<int, int, int>>{
        {0, 0, 1}, {1, 0, 1}, {2, 0, 1}, {3, 0, 1}, {4, 0, 1},
        {5, 0, 1}, {5, 1, 1}, {6, 0, 1}, {6, 1, 1}, {6, 2, 1}, {7, 0, 1}
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
    fixture.create_failure = HANDLE_RSI;
    assert(!indicators.Create("XAUUSDm", defaults));
    assert((fixture.releases == std::vector<int>{0, 1, 2, 3, 5, 6, 7}));
    indicators.Release();
    assert(fixture.releases.size() == 7);
    fixture = {};
    assert(indicators.Create("XAUUSDm", defaults));
    indicators.Release();
    indicators.Release();
    assert(fixture.releases.size() == 8);
    fixture = {};
    assert(indicators.Create("XAUUSDm", defaults));
    AurumIndicatorSnapshot snapshot;
    assert(indicators.ReadLatest(snapshot) == INDICATORS_READY);
    indicators.Release();
}

int main() {
    CheckSnapshot();
    CheckFailuresAndRetry();
    CheckLifecycle();
}
