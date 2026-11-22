# [AU-005] MT5 Python client dan diagnostik broker/simbol

- Status: DONE (implementasi dan verifikasi offline; integrasi MT5 NOT RUN)
- Priority: P0
- Epic / label: area:data, priority:P0, type:feature
- Dependencies: AU-002
- Publication: [GitHub #5](https://github.com/akbar875/TradingGold/issues/5)
- PR/commit: [PR #37](https://github.com/akbar875/TradingGold/pull/37), implementasi `3b0d22c`.

## Latar belakang

Semua input market berasal dari simbol broker tepat.

## Scope dan deliverable

Doctor, koneksi, symbol_select, tick/point/contract/volume/margin, M15,H1,H4, masking akun.

File/modul terkait: python/aurum/mt5_client.py, python/aurum/data_quality.py, tests/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [x] Verifikasi dependensi AU-002 dan kontrak input/output.
- [x] Implementasikan diagnostik dan history read-only dengan reason code.
- [x] Tambahkan kasus positif, negatif, dan regresi.
- [x] Dokumentasikan argumen dan output di panduan Windows MT5 serta bukti di TEST_REPORT.md.
- [x] Review acceptance dan tautkan PR/commit.

## Acceptance criteria

- [x] Paket MT5 hilang dan kegagalan koneksi/simbol menghasilkan reason code.
- [x] Input invalid menghasilkan WAIT dan status gagal, tanpa candle parsial.
- [x] 145 tes offline PASS. Integrasi MT5/broker demo dan kompilasi EA NOT RUN.
- [x] [Panduan Windows MT5](../INSTALL_WINDOWS_MT5.md#diagnostik-dan-history-python)
  mendokumentasikan perilaku dan keterbatasan.

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
