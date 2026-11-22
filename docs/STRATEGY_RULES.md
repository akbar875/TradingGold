# Aturan strategi target

Belum ada engine strategi pada scaffold. Output EA adalah WAIT dengan
ENGINE_NOT_IMPLEMENTED, bukan rekomendasi teknikal.

Target PRD: entry M15 closed-bar, konfirmasi H1/H4 yang sudah tutup secara kausal;
EMA20/50 M15, EMA50/200 H1, RSI14, MACD12/26/9, Wilder ADX/DI14, ATR14,
swing/support/resistance. Setup terpisah TREND_PULLBACK dan BREAKOUT_RETEST.
RANGE_REJECTION belum masuk scope awal. Skor 0..100 adalah heuristik.

Threshold, rumus edge case, lookback swing, invalidation, chase limit, target
struktur dan bobot skor harus ditentukan dan diuji dalam AU-007..011.
BUY/SELL baru valid setelah gate pasar, AI opsional dan risiko lolos. Data invalid,
HTF conflict atau setup tidak lengkap menghasilkan WAIT dengan reason code.
