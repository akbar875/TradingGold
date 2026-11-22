# [AU-003] CI Python, formatting, lint, typing dan pytest

- Status: IN_PROGRESS
- Priority: P0
- Epic / label: area:infra, priority:P0, type:feature
- Dependencies: AU-002
- Publication: [GitHub #3](https://github.com/akbar875/TradingGold/issues/3)

## Latar belakang

Semua perubahan penting bisa diuji otomatis.

## Scope dan deliverable

Workflow CI, scripts test, pytest, ruff, optional mypy, coverage minimum pada modul safety.

File/modul terkait: pyproject.toml, config/, scripts/, .github/, docs/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [x] Verifikasi AU-002 di main melalui PR #34.
- [x] Jalankan lint, format, mypy, doctor offline, pytest dan coverage melalui satu runner.
- [x] Uji keberadaan preset wajib dan jalur kegagalan diagnostik MT5 dengan mock.
- [x] Catat hasil lokal dan keterbatasan di [laporan tes](../TEST_REPORT.md).
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [ ] Workflow valid dan pytest fixture offline PASS; laporan dapat diakses.
- [x] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu pada pengujian offline fondasi.
- [x] Coverage dengan pengukuran branch minimal 90% per modul `config`, `cli`, `data_quality`, dan `mt5_client`.
- [x] Dokumentasi mencatat hasil verifikasi lokal dan keterbatasan lingkungan.

## Skenario tes

Offline import/config, input invalid, error exit, rerun idempotent; pytest dan lint.

Jalankan `scripts/test_offline.ps1` di Windows atau `python scripts/test_offline.py`
di Linux. Periksa `reports/pytest.xml` dan `reports/coverage.xml`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
