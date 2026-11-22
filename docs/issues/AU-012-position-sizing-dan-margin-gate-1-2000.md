# [AU-012] Position sizing dan margin gate 1:2000

- Status: OPEN
- Priority: P0
- Epic / label: area:risk, priority:P0, type:feature
- Dependencies: AU-011
- Publication: NOT PUBLISHED
- PR/commit: lihat riwayat Git; belum ada PR khusus issue ini.

## Latar belakang

Lot mengikuti risiko harga, bukan leverage maksimum.

## Scope dan deliverable

OrderCalcProfit/OrderCalcMargin, volume min/step/max, cap, actual leverage, worst-case.

File/modul terkait: mt5/Include/Aurum/, config/default.yaml, tests/test_risk.py. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [ ] Verifikasi dependensi issue dan kontrak input/output.
- [ ] Implementasikan scope di atas dengan reason code dan fail-closed path.
- [ ] Tambahkan kasus positif, negatif, dan regression yang relevan.
- [ ] Perbarui dokumentasi, konfigurasi, serta bukti di docs/TEST_REPORT.md.
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [ ] Min lot over risk => reject; leverage mismatch => auto entry reject.
- [ ] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu.
- [ ] Tes yang relevan PASS; tes yang tidak tersedia ditulis NOT RUN dengan alasan.
- [ ] Dokumentasi menyebut perilaku aktual dan keterbatasan, tanpa klaim profit.

## Skenario tes

Min lot over budget, margin gagal, leverage mismatch, news unknown, restart dan SL monotonic.

Offline: `python -m pytest -q`; lint: `python -m ruff check python tests scripts dashboard`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
