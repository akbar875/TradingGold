# [AU-009] Setup entry breakout retest dan trend pullback

- Status: DONE (fondasi terverifikasi offline, MetaEditor dan terminal NOT RUN)
- Priority: P0
- Epic / label: area:mql5, priority:P0, type:feature
- Dependencies: AU-008
- Publication: [GitHub #9](https://github.com/akbar875/TradingGold/issues/9)
- PR/commit: [PR #41](https://github.com/akbar875/TradingGold/pull/41), implementasi `4394862`.

## Latar belakang

Entry hanya ketika trigger lengkap.

## Scope dan deliverable

`Setups.mqh` mengevaluasi TREND_PULLBACK dan BREAKOUT_RETEST menggunakan
snapshot AU-008, candle M15 tertutup, swing high/low, key level, invalidation,
dan chase limit. `SetupClaims.mqh` membatasi event Journal per simbol dan
candle M15. EA menampilkan kandidat diagnostik BUY/SELL atau alasan WAIT.
Aksi entry EA tetap WAIT dan kedua preset tetap signal-only.

## Tasks

- [x] Verifikasi dependensi AU-008 dan kontrak input/output.
- [x] Implementasikan evaluator, reason code, dan jalur fail-closed.
- [x] Tambahkan fixture positif, negatif, dan regresi closed-bar.
- [x] Dokumentasikan aturan, konfigurasi, dan bukti di docs/TEST_REPORT.md.
- [x] Tinjau acceptance dan tautkan PR serta commit implementasi.

## Acceptance criteria

- [x] Fixture menguji BUY/SELL untuk kedua setup dan WAIT, pemilihan satu
  kandidat saat pola bertumpuk, serta deduplikasi event pada candle yang sama.
- [x] Data, quote, dan state invalid memblokir penerbitan. EA tetap WAIT untuk entry.
- [x] Suite offline **PASS**. MetaEditor dan terminal **NOT RUN** karena tool
  tidak tersedia. Lihat [laporan tes](../TEST_REPORT.md#au-009--setup-entry-m15-24-november-2026).
- [x] Dokumentasi menjelaskan aturan setup, ambang, dan batas verifikasi.

## Skenario tes

Fixture offline mencakup kandidat BUY/SELL untuk kedua setup, WAIT, pola
ganda, false breakout, batas retest, invalidation, chase, OHLC/gap invalid,
rollover, quote invalid, serta simulasi retry dan restart. Verifikasi native
mencakup compile MetaEditor, Strategy Tester, dan attach/restart pada preset
Signal_Only. Ownership posisi, retcode, dan idempotensi order mengikuti AU-014.
Aturan dan batas diagnostik tercatat di [aturan strategi](../STRATEGY_RULES.md#setup-entry-au-009).

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
