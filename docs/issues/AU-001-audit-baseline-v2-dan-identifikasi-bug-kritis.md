# [AU-001] Audit baseline v2 dan identifikasi bug kritis

- Status: DONE
- Priority: P0
- Epic / label: area:infra, priority:P0, type:feature
- Dependencies: -
- Publication: NOT PUBLISHED
- PR/commit: lihat riwayat Git; belum ada PR khusus issue ini.

## Latar belakang

Tidak mengulang asumsi bahwa file EA v2 sudah berhasil dikompilasi.

## Scope dan deliverable

Inventaris file, pemeriksaan kompilasi, code review, bug/risk register, migrasi baseline.

File/modul terkait: pyproject.toml, config/, scripts/, .github/, docs/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [x] Verifikasi dependensi issue dan kontrak input/output.
- [x] Implementasikan scope di atas dengan reason code dan fail-closed path.
- [x] Tambahkan kasus positif, negatif, dan regression yang relevan.
- [x] Perbarui dokumentasi, konfigurasi, serta bukti di docs/TEST_REPORT.md.
- [x] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [x] Audit report, daftar masalah dengan severity, rencana migrasi dan tes awal.
- [x] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu.
- [x] Tes yang relevan PASS; tes yang tidak tersedia ditulis NOT RUN dengan alasan.
- [x] Dokumentasi menyebut perilaku aktual dan keterbatasan, tanpa klaim profit.

## Skenario tes

Offline import/config, input invalid, error exit, rerun idempotent; pytest dan lint.

Offline: `python -m pytest -q`; lint: `python -m ruff check python tests scripts dashboard`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.

Bukti audit: docs/BASELINE_AUDIT.md dan docs/BASELINE_HASHES.json.
