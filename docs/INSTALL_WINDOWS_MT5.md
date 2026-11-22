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

## Diagnostik dan history Python

Pasang ekstra `[mt5]` sesuai README. Gunakan terminal demo yang sudah login dan
nama simbol persis, misalnya `XAUUSDm`. Adapter memakai sesi yang ditemukan
terminal melalui `initialize()`. Pemilihan simbol bisa menambahkannya ke Market
Watch. Seluruh operasi tetap berstatus `WAIT` dengan `execution_available=false`.

- `doctor --offline` melaporkan `OFFLINE / BROKER_NOT_CHECKED`, exit 0.
- `doctor --symbol XAUUSDm` melaporkan koneksi, izin terminal/akun/simbol,
  snapshot akun dengan login masked, mata uang, leverage dan margin aktual,
  properti simbol sesuai broker, serta bid/ask dan spread dalam points. Login
  satu atau dua digit ditutup seluruhnya. Leverage 1:2000 hanya dilaporkan
  sebagai kecocokan pada mode signal-only.
- Doctor memeriksa dua candle tertutup per timeframe M15/H1/H4 dan keberadaan
  direktori `Files` di `commondata_path` tanpa menulis atau mencetak path tersebut.
  Tick harus berumur 0–120 detik dan memiliki bid positif serta ask minimal
  sebesar bid. Quote dengan ask sama seperti bid dilaporkan sebagai spread nol.
  Doctor mengembalikan exit 0 dengan `CONNECTED / DIAGNOSTICS_ONLY` jika
  pemeriksaan tersebut siap. Exit 1 dengan `NOT_READY` menyertakan reason code
  dan status per pemeriksaan yang sempat berjalan. Freshness model belum
  tersedia dan tetap dilaporkan sebagai `NOT_IMPLEMENTED`.
- `fetch-data --symbol XAUUSDm --timeframe M15 --bars 10000` menerima
  M15/H1/H4 dan 1–100.000 bar. Default M15 dan 10.000 bar. Exit 0
  mengembalikan `READY`, metadata sumber/simbol/timeframe/point, dan candle
  OHLC, tick volume serta spread dalam broker points. Field `time` adalah
  timestamp open UTC dalam detik Unix. Data ini juga bisa dibaca saat izin
  trading dimatikan. Argumen invalid exit 2, kegagalan baca/validasi exit 1
  tanpa kumpulan candle parsial.

Kedua perintah membaca mulai dari posisi 1 dan memeriksa ulang timestamp candle
serta identitas sesi. History menjadi `DATA_STALE` jika umur penutupan bar
terbaru mencapai satu interval timeframe, termasuk saat pasar tutup. Gap
historis tetap terlihat pada `gap_timestamps_utc`, yang berisi waktu open bar
sesudah gap. Kelengkapan history bergantung pada broker dan pengaturan
**Max. bars in chart**. Klasifikasi gap berdasarkan sesi dilacak di AU-006.
Dasar posisi bar dan batas history ada di
[referensi MetaQuotes](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrompos_py).
