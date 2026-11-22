# [AU-004] Script compile EA MT5 di Windows dan pelaporan

- Status: DONE (runner compile; MetaEditor nyata NOT RUN)
- Priority: P0
- Epic / label: area:mql5, priority:P0, type:feature
- Dependencies: AU-002
- Publication: [GitHub #4](https://github.com/akbar875/TradingGold/issues/4)
- PR/commit: branch `codex/au-004-compile-reporting`; bukti di [TEST_REPORT](../TEST_REPORT.md).

## Latar belakang

Kompilasi MQL5 harus dapat diverifikasi, bukan klaim.

## Scope dan deliverable

PowerShell compile via MetaEditor CLI jika terpasang; tangkap exit code/log dan error.

File/modul terkait: mt5/Experts/, mt5/Include/Aurum/, mt5/Presets/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [x] AU-002 DONE; input path compiler dan timeout, output status/log/EX5 serta exit code terdokumentasi.
- [x] Workspace unik, CLI resmi, reason code, timeout, validasi log dan artifact baru.
- [x] 18 regresi runner Windows dan 6 regresi publisher completion.
- [x] Panduan instalasi, README, changelog dan TEST_REPORT diperbarui.
- [x] Acceptance ditinjau; referensi branch dan bukti tercantum di atas.

## Acceptance criteria

- [x] MetaEditor tidak tersedia: NOT RUN / COMPILER_UNAVAILABLE, exit 2.
- [x] Input invalid, log error/ambigu, launch failure dan EX5 invalid ditolak tanpa PASS lama.
- [x] Tes offline Windows 96 PASS; kompilasi MetaEditor nyata NOT RUN, bukan PASS mock.
- [x] Dokumentasi menjelaskan lokasi build, exit code, timeout dan keterbatasan.

## Skenario tes

`tests/test_compile_mql5.py` menjalankan script PowerShell asli di salinan repo
dengan path berspasi dan compiler/process fixture: sukses (dua format summary),
compiler/source/include hilang, timeout invalid, launch failure, timeout proses
nyata, exit nonzero, 10 errors, warning, summary tertanam/duplikat, diagnostic
error, log hilang, EX5 hilang/kosong/lama. PASS lama dan EX5 source lama dipasang
sebagai sentinel. Fixture tidak membuktikan kompilasi MQL5.

Tes entry/ownership/retcode menjadi scope issue engine/eksekusi berikutnya;
AU-004 hanya membangun dan melaporkan hasil compile, tanpa menjalankan EA/order.

Offline: `python -m pytest -q`; lint: `python -m ruff check python tests scripts dashboard`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
