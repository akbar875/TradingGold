# [AU-026] Dashboard Streamlit monitoring read-only

- Status: IN_PROGRESS
- Priority: P1
- Epic / label: area:dashboard, priority:P1, type:feature
- Dependencies: AU-022, AU-023
- Publication: NOT PUBLISHED
- PR/commit: lihat riwayat Git; belum ada PR khusus issue ini.

## Latar belakang

Pengguna dapat membaca sinyal/risk/status dengan jelas.

## Scope dan deliverable

Signal card, reasons, safety status, test metrics, trade log, equity/DD charts.

File/modul terkait: dashboard/app.py, python/aurum/journal.py, tests/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [ ] Verifikasi dependensi issue dan kontrak input/output.
- [ ] Implementasikan scope di atas dengan reason code dan fail-closed path.
- [ ] Tambahkan kasus positif, negatif, dan regression yang relevan.
- [ ] Perbarui dokumentasi, konfigurasi, serta bukti di docs/TEST_REPORT.md.
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [ ] Offline empty states, no order submission, no fake live price.
- [ ] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu.
- [ ] Tes yang relevan PASS; tes yang tidak tersedia ditulis NOT RUN dengan alasan.
- [ ] Dokumentasi menyebut perilaku aktual dan keterbatasan, tanpa klaim profit.

## Skenario tes

Empty/offline/error states, masking, tidak ada order/modify/close controls.

Offline: `python -m pytest -q`; lint: `python -m ruff check python tests scripts dashboard`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
