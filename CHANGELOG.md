# Changelog

## Unreleased — 23 November 2026

- AU-004: compile terisolasi per run, parameter CLI MetaEditor resmi, timeout,
  validasi ringkasan log dan EX5 baru, serta status kegagalan dengan reason code.
- Regresi runner Windows mencakup false PASS, stale evidence, launch failure,
  timeout proses nyata, dan error input/output; compile MetaEditor tetap NOT RUN.
- Publisher completion opt-in memverifikasi issue milik sendiri dan PR merged
  ke main; default dry-run tetap dipertahankan.
- AU-006: validasi OHLCV, gap sesi UTC, overlap, dan outlier, konversi spread
  memakai broker point, serta snapshot kausal M15/H1/H4.
- AU-008: konfirmasi H4 closed-bar, klasifikasi market regime, filter arah dan
  pemblokiran pada data invalid di EA. Aksi tetap WAIT pada fase fondasi.

## 0.3.0.dev0 — 22 November 2026

- Audit keenam berkas awal dan preservasi baseline v2.
- Fondasi paket Python, konfigurasi fail-closed, CLI doctor dan kontrak modul.
- Validator closed-bar awal dan tes negatif offline.
- EA diagnostik tanpa eksekusi, dua preset non-eksekusi, runner compile.
- Dashboard empty state read-only, CI, 33 issue lokal dan publisher dry-run.
- Belum mengimplementasikan strategi, ML v3, backtest atau eksekusi demo/live.
