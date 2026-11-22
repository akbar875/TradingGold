# [AU-002] Scaffold repo, konfigurasi dan kontrak modul

- Status: DONE (scaffold fase A)
- Priority: P0
- Epic / label: area:infra, priority:P0, type:feature
- Dependencies: AU-001
- Publication: NOT PUBLISHED
- Commit scaffold awal: `5263159` (`Scaffold Aurum MT5 v3 foundation`).
- Bukti tindak lanjut: [laporan tes](../TEST_REPORT.md).

## Latar belakang

Repositori modular dengan konfigurasi tunggal dan dokumentasi dasar.

## Scope dan deliverable

Struktur paket Python, module MQL5, .gitignore, .env.example, AGENTS.md, pyproject dan default.yaml.

File/modul terkait: pyproject.toml, config/, scripts/, .github/, docs/. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [x] Verifikasi dependensi AU-001 dan kontrak konfigurasi di arsitektur.
- [x] Tolak konfigurasi ambigu atau invalid dan validasi override simbol sebelum diagnostik.
- [x] Tambahkan regresi untuk respons CLI dan preservasi baseline.
- [x] Catat hasil verifikasi dan batas lingkup fase A.
- [x] Review acceptance dan catat commit scaffold awal serta bukti tindak lanjut.

## Acceptance criteria

- [x] Instal editable Python dengan dependensi tersedia dan import lulus. Pemeriksaan pola kredensial umum pada berkas tracked tidak menemukan kecocokan.
- [x] Konfigurasi dan simbol invalid menghasilkan error JSON dengan exit 2 sebelum diagnostik atau sinyal.
- [x] Tes offline lulus. Verifikasi MetaEditor dicatat `NOT RUN` dan ditangani pada AU-004.
- [x] Dokumentasi menjelaskan kontrak yang tersedia dan status engine fase A.

## Skenario tes

- `test_invalid_config_returns_structured_error` mencakup key duplikat,
  benturan merge, key non-string, bentuk YAML invalid, integer di luar rentang
  float, karakter kontrol dalam simbol, dan encoding invalid.
- Tes override simbol memeriksa sufiks broker di `show-config` dan mock
  diagnostik serta memastikan input invalid berhenti sebelum adapter MT5.
- `scripts/test_offline.ps1` menjalankan verifikasi lint, format, typing, dan pytest.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
