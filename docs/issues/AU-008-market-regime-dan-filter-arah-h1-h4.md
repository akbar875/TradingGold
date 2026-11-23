# [AU-008] Market regime dan filter arah H1/H4

- Status: DONE (fondasi terverifikasi offline, MetaEditor dan terminal NOT RUN)
- Priority: P0
- Epic / label: area:mql5, priority:P0, type:feature
- Dependencies: AU-007
- Publication: [GitHub #8](https://github.com/akbar875/TradingGold/issues/8)
- PR/commit: [PR #40](https://github.com/akbar875/TradingGold/pull/40), implementasi `fa2942f`.

## Latar belakang

EA mengenali kondisi trend, range dan volatilitas tinggi.

## Scope dan deliverable

Snapshot tertutup M15/H1/H4, EMA50/200 H1 dan H4, ADX/DI M15, guard ATR dan
spread candle, serta konsolidasi. `mt5/Include/Aurum/Regime.mqh` menghasilkan
regime, izin arah dan reason code. Hasil dihitung ulang tiap pembacaan dan
langsung diblokir jika data tidak aman. Panel EA tetap menampilkan WAIT.

## Tasks

- [x] Verifikasi dependensi AU-007 dan kontrak input/output.
- [x] Implementasikan klasifikasi, reason code dan jalur fail-closed.
- [x] Tambahkan fixture positif, negatif dan regresi closed-bar.
- [x] Dokumentasikan aturan, preset dan bukti tes.
- [x] Tinjau acceptance dan tautkan PR serta commit implementasi.

## Acceptance criteria

- [x] Fixture menguji bullish, bearish, range, keadaan unsafe, serta data
  invalid yang memblokir arah dan membuat EA WAIT.
- [x] Input invalid diblokir dan EA fondasi hanya menampilkan WAIT.
- [x] Suite offline **PASS**. MetaEditor dan terminal **NOT RUN** karena
  tool tidak tersedia. Lihat [laporan tes](../TEST_REPORT.md#au-008--market-regime-h1h4-23-november-2026).
- [x] [Aturan strategi](../STRATEGY_RULES.md#market-regime-au-008) menjelaskan
  ambang, sumber spread, transisi dan perilaku WAIT.

## Skenario tes

Fixture offline mencakup izin arah buy/sell, konflik H1/H4, batas klasifikasi,
ketidaklengkapan history dan buffer, rollover, retry, pelepasan handle, dan
pembuatan ulang. Verifikasi native mencakup compile MetaEditor, pemasangan
ulang EA, perubahan timestamp H4 dan panel WAIT pada preset Signal_Only.
Keputusan BUY/SELL final mengikuti AU-009/AU-010. Ownership dan retcode
mengikuti AU-014.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
