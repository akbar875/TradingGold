# Panduan kontributor Aurum

- Baca README.md, docs/ARCHITECTURE.md, docs/BASELINE_AUDIT.md, PRD dan issue terkait.
- Scope saat ini fondasi fase A. Jangan mengklaim produk trading lengkap.
- Python/dashboard tidak boleh mengirim order. Eksekusi nantinya hanya di EA.
- SignalOnly=true, AutoTrade=false, DemoOnly=true. News unknown atau AI invalid
  ketika required memblokir entry baru. Jangan aktifkan live dalam setup/tes.
- Fitur harus kausal, closed-bar, tanpa look-ahead atau shuffle time-series.
- Pertahankan keenam berkas baseline; hash di docs/BASELINE_HASHES.json.
- Jangan commit kredensial, nomor akun privat, dataset broker, model atau logs.
- Jalankan scripts/test_offline.ps1 atau perintah setara di CI setelah perubahan
  Python. Tes baru fokus pada kontrak dan failure paths yang bermakna.
- Compile EA hanya dinyatakan PASS jika MetaEditor benar-benar menghasilkan log
  serta artifact baru. Bila tool/terminal tidak tersedia, tulis NOT RUN.
- Update dokumen dan status issue secara faktual. Remote issue memerlukan
  publisher --publish; default dry-run. Jangan mengubah/menutup issue milik orang lain.
- Jangan memilih lisensi distribusi tanpa keputusan pemilik repo.
