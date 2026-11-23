# [AU-009] Setup entry breakout retest dan trend pullback

- Status: OPEN
- Priority: P0
- Epic / label: area:mql5, priority:P0, type:feature
- Dependencies: AU-008
- Publication: [GitHub #9](https://github.com/akbar875/TradingGold/issues/9)

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
- [ ] Tautkan hasil tes dan PR yang menyelesaikan issue.
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [ ] Tes BUY/SELL/WAIT dan tidak terjadi duplikasi sinyal pada candle sama.
- [ ] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu.
- [ ] Tes yang relevan PASS; tes yang tidak tersedia ditulis NOT RUN dengan alasan.
- [ ] Dokumentasi menyebut perilaku aktual dan keterbatasan, tanpa klaim profit.

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
