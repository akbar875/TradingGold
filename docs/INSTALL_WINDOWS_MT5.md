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

Atau jalankan dari root repo:

```powershell
.\scripts\compile_mql5.ps1 -MetaEditor 'C:\Program Files\MetaTrader 5\metaeditor64.exe' -TimeoutSeconds 120
```

Script menyalin source dan Include ke workspace unik
`reports/mql5/<run-id>/MQL5/`, lalu memakai `/compile`, `/include` dan `/log`
sesuai [CLI resmi MetaEditor](https://www.metatrader5.com/en/metaeditor/help/beginning/integration_ide).
Tidak menginstal atau menjalankan terminal, tidak mengubah EX5 lama di source,
dan tidak menyalin hasil build ke terminal. Lokasi log dan EX5 hasil build
dicetak pada `reports/mql5-status.txt`; setelah PASS, salin EX5 tersebut ke
folder `MQL5/Experts` terminal secara manual.

Exit 0 / PASS membutuhkan compiler exit 0, tepat satu ringkasan log dengan
0 errors dan 0 warnings, serta EX5 baru yang tidak kosong. Log UTF-16 dengan BOM
didukung. Ringkasan ambigu, error, warning, log hilang, dan artifact lama/kosong
menghasilkan exit 1 / FAIL dengan reason code. Compiler tidak tersedia
menghasilkan exit 2 / NOT RUN (`COMPILER_UNAVAILABLE`). Status lama dibatalkan
sebelum validasi atau peluncuran, sehingga launch failure tidak mempertahankan
PASS sebelumnya. Timeout default 120 detik (rentang 1..600) menghentikan proses
compiler yang diluncurkan runner dan menghasilkan `COMPILER_TIMEOUT` / exit 1.

Tes Windows memakai compiler fixture; PASS tes tersebut hanya membuktikan
kontrak runner, bukan kompilasi EA oleh MetaEditor. Kompilasi nyata tetap
NOT RUN bila MetaEditor tidak tersedia.

`METAEDITOR_PATH` dapat ditentukan melalui environment. .env.example hanya contoh;
script tidak otomatis memuat .env. Source build dan data terminal memiliki lokasi
berbeda. Jangan menganggap perubahan YAML mengubah preset EA secara otomatis.
