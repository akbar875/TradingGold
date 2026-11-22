# Instalasi Windows dan MT5

Ikuti README untuk venv dan instalasi paket. Ekstra `[mt5]` hanya untuk Windows
desktop dengan terminal yang sudah login. Gunakan akun demo saat kelak pengujian
integrasi tersedia; scaffold ini tidak mengeksekusi atau mengelola posisi.

1. Di MT5 pilih File > Open Data Folder.
2. Salin mt5/Experts/Aurum_Expert_AI_XAUUSD.mq5 ke MQL5/Experts dan folder
   mt5/Include/Aurum ke MQL5/Include/Aurum.
3. Buka source di MetaEditor dan F7; periksa Errors dan log.
4. Setelah compile terverifikasi, pasang pada chart simbol broker M15 dan muat
   mt5/Presets/Signal_Only.set. Panel saat ini WAIT/ENGINE_NOT_IMPLEMENTED.

Atau compile via scripts/compile_mql5.ps1 -MetaEditor <path>. Script tidak
menginstal terminal atau menyalin ke folder terminal, dan menuntut artifact baru
serta log 0 errors, 0 warnings. Compiler yang tidak tersedia menghasilkan exit 2
dan reports/mql5-status.txt NOT RUN. Tidak adanya log tidak dianggap sukses.

`METAEDITOR_PATH` dapat ditentukan melalui environment. .env.example hanya contoh;
script tidak otomatis memuat .env. Source build dan data terminal memiliki lokasi
berbeda. Jangan menganggap perubahan YAML mengubah preset EA secara otomatis.
