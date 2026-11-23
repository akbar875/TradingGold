# [AU-007] Indikator teknikal MQL5 yang konsisten

- Status: DONE (fondasi terverifikasi offline; MetaEditor dan terminal NOT RUN)
- Priority: P0
- Epic / label: area:mql5, priority:P0, type:feature
- Dependencies: AU-002
- Publication: [GitHub #7](https://github.com/akbar875/TradingGold/issues/7)
- PR/commit: [PR #39](https://github.com/akbar875/TradingGold/pull/39), implementasi `19d7b8d`.

## Latar belakang

Nilai indikator dapat diulang dan ditelusuri.

## Scope dan deliverable

Snapshot EMA M15/H1 dan RSI, MACD, ADX/+DI/-DI, serta ATR M15 di
`mt5/Include/Aurum/Indicators.mqh`. M15 memakai `CopyBuffer` pada shift 1.
H1 memakai bar yang sudah selesai pada batas keputusan M15. Preset dan EA
memuat periode default FR-004. H4 berada di AU-008, swing dan level struktur
di AU-009/AU-011.

## Tasks

- [x] Verifikasi dependensi AU-002 serta kontrak input/output.
- [x] Implementasikan snapshot dan reason code fail-closed.
- [x] Tambahkan fixture positif dan regresi kasus negatif.
- [x] Perbarui aturan strategi, preset, dan laporan tes.
- [x] Tautkan PR/commit dan catat batas verifikasi.

## Acceptance criteria

- [x] Fixture offline memeriksa nilai dan pemetaan buffer, cutoff kausal, serta
  pelepasan handle. `OnDeinit` memanggil pelepasan; pengujian attach/detach dan
  pembandingan nilai native di terminal **NOT RUN**.
- [x] Input invalid gagal sebelum handle dibuat. Snapshot gagal dikosongkan;
  aksi EA tetap WAIT dan tidak ada jalur order.
- [x] Suite offline **PASS**. Kompilasi dan pengujian terminal **NOT RUN**
  karena tool tidak tersedia. Lihat [laporan tes](../TEST_REPORT.md#au-007--indikator-mql5-closed-bar-23-november-2026).
- [x] [Aturan strategi](../STRATEGY_RULES.md#indikator-au-007) menjelaskan waktu
  bar, pemanasan, validasi, serta perilaku WAIT.

## Skenario tes

Fixture menguji pemetaan buffer, batas H1, warmup, hasil parsial, nilai invalid,
retry, dan lifecycle. Checklist native mencakup compile MetaEditor, perbandingan
Data Window, serta restart dan detach dalam mode Signal_Only. BUY/SELL diuji
saat engine sinyal tersedia. Ownership dan retcode berada di AU-014.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
