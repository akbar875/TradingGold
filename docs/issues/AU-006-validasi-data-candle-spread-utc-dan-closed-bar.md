# [AU-006] Validasi data candle, spread, UTC dan closed-bar

- Status: DONE (fondasi terverifikasi offline; integrasi MT5 dan sinyal final NOT RUN)
- Priority: P0
- Epic / label: area:data, priority:P0, type:feature
- Dependencies: AU-005
- Publication: [GitHub #6](https://github.com/akbar875/TradingGold/issues/6)
- PR/commit: [PR #38](https://github.com/akbar875/TradingGold/pull/38), implementasi `2969bf8`.

## Latar belakang

Mencegah analisis dari candle tidak lengkap atau historis kotor.

## Scope dan deliverable

Audit OHLCV, monotonic timestamps, gap, duplicate, timezone, spread points conversion.

File/modul terkait: python/aurum/mt5_client.py, python/aurum/data_quality.py, tests/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [x] Verifikasi AU-005 dan kontrak input/output.
- [x] Implementasikan validator dan jalur fail-closed dengan reason code.
- [x] Tambahkan kasus positif, negatif, dan regresi kausalitas snapshot.
- [x] Perbarui konfigurasi, panduan kualitas data, dan laporan tes.
- [x] Review acceptance fondasi dan tautkan PR/commit.

## Acceptance criteria

- [x] Tes gap, duplicate, malformed, stale, dan posisi 1 pada input snapshot.
  Verifikasi pemakaian input pada sinyal final **NOT RUN** karena engine
  sinyal masih scaffold.
- [x] Input invalid memicu penolakan dengan reason code di jalur yang diuji.
- [x] Suite offline PASS dengan 176 tes. Status integrasi MT5 dan MetaEditor
  **NOT RUN** serta alasannya tercatat di [laporan tes](../TEST_REPORT.md#au-006--kualitas-candle-dan-snapshot-utc-23-november-2026).
- [x] [Panduan kualitas data](../INSTALL_WINDOWS_MT5.md#kualitas-candle-dan-snapshot-utc)
  mendokumentasikan jadwal UTC dari broker, heuristik outlier, dan semantik spread nol.

## Skenario tes

Missing terminal/suffix, stale/open/duplicate/unsorted bars, NaN OHLC dan gap report.

Offline: `python -m pytest -q`; lint: `python -m ruff check python tests scripts dashboard`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
