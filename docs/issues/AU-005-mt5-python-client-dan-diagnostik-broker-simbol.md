# [AU-005] MT5 Python client dan diagnostik broker/simbol

- Status: IN_PROGRESS
- Priority: P0
- Epic / label: area:data, priority:P0, type:feature
- Dependencies: AU-002
- Publication: NOT PUBLISHED
- PR/commit: lihat riwayat Git; belum ada PR khusus issue ini.

## Latar belakang

Semua input market berasal dari simbol broker tepat.

## Scope dan deliverable

Doctor, koneksi, symbol_select, tick/point/contract/volume/margin, M15,H1,H4, masking akun.

File/modul terkait: python/aurum/mt5_client.py, python/aurum/data_quality.py, tests/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [ ] Verifikasi dependensi issue dan kontrak input/output.
- [ ] Implementasikan scope di atas dengan reason code dan fail-closed path.
- [ ] Tambahkan kasus positif, negatif, dan regression yang relevan.
- [ ] Perbarui dokumentasi, konfigurasi, serta bukti di docs/TEST_REPORT.md.
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [ ] Missing MT5/broker menghasilkan error jelas, data tidak dipalsukan.
- [ ] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu.
- [ ] Tes yang relevan PASS; tes yang tidak tersedia ditulis NOT RUN dengan alasan.
- [ ] Dokumentasi menyebut perilaku aktual dan keterbatasan, tanpa klaim profit.

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
