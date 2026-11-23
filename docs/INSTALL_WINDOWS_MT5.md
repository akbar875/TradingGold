# Instalasi Windows dan MT5

Ikuti README untuk venv dan instalasi paket. Ekstra `[mt5]` hanya untuk Windows
desktop dengan terminal yang sudah login. Gunakan akun demo saat kelak pengujian
integrasi tersedia; scaffold ini tidak mengeksekusi atau mengelola posisi.

1. Di MT5 pilih File > Open Data Folder.
2. Salin mt5/Experts/Aurum_Expert_AI_XAUUSD.mq5 ke MQL5/Experts dan folder
   mt5/Include/Aurum ke MQL5/Include/Aurum.
3. Buka source di MetaEditor dan F7; periksa Errors dan log.
4. Setelah compile terverifikasi, pasang pada chart simbol broker M15 dan muat
   mt5/Presets/Signal_Only.set. Panel menampilkan WAIT dan status indikator.
   Setelah history siap, nilai M15/H1/H4 dan hasil market regime ditampilkan
   bersama timestamp bar sumber. Lihat [aturan regime](STRATEGY_RULES.md#market-regime-au-008).

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
- Doctor meminta dua candle dari posisi 1 per timeframe M15/H1/H4 dan memeriksa keberadaan
  direktori `Files` di `commondata_path` tanpa menulis atau mencetak path tersebut.
  Tick harus berumur 0–120 detik dan memiliki bid positif serta ask minimal
  sebesar bid. Quote dengan ask sama seperti bid dilaporkan sebagai spread nol.
  Doctor mengembalikan exit 0 dengan `CONNECTED / DIAGNOSTICS_ONLY` jika
  pemeriksaan tersebut siap. Exit 1 dengan `NOT_READY` menyertakan reason code
  dan status per pemeriksaan yang sempat berjalan. Freshness model belum
  tersedia dan tetap dilaporkan sebagai `NOT_IMPLEMENTED`.
- `fetch-data --symbol XAUUSDm --timeframe M15 --bars 2` menerima
  M15/H1/H4 dan 1–100.000 bar. Default M15 dan 10.000 bar. Exit 0
  mengembalikan `READY`, metadata sumber/simbol/timeframe/point, dan candle
  OHLC, tick volume, `spread` dalam broker points dan `spread_price` dalam satuan
  harga. Field `time` adalah timestamp open UTC dalam detik Unix. Data ini bisa dibaca saat izin
  trading dimatikan. Argumen invalid exit 2, kegagalan baca/validasi exit 1
  tanpa kumpulan candle parsial.

### Kualitas candle dan snapshot UTC

- Kedua perintah memeriksa ulang penutupan candle dan identitas sesi. Candle
  duplikat atau mundur, interval overlap, OHLC invalid, tick volume negatif
  atau noninteger, dan spread negatif, pecahan atau nonfinite ditolak.
  Harga yang menyimpang dari close sebelumnya atau memiliki range terhadap
  open melebihi `history_max_bar_move_percent` menghasilkan `DATA_BAR_OUTLIER`.
  Default heuristik mutu data ini 10%. Candle pertama memakai open sebagai
  referensi harga. Ambang berlaku juga setelah penutupan sesi.
- `history_session_closures_utc` berisi pasangan `[mulai, selesai]` dalam detik
  Unix UTC untuk simbol broker yang sedang diaudit. Urutkan interval menurut
  waktu dan gabungkan interval yang bersinggungan. Jadwal default kosong.
  Tambahkan jadwal broker yang sudah diverifikasi melalui `--config`,
  termasuk libur, jeda harian dan perubahan DST yang relevan dengan history.
  Gap menjadi `SCHEDULED_CLOSURE` bila seluruh rentangnya tercakup. Gap lain
  menjadi `UNKNOWN` dan menghasilkan `NOT_READY / DATA_GAP_UNEXPLAINED`.
  `history.gaps` memuat awal gap dan waktu open berikutnya.
  `gap_timestamps_utc` tetap memuat waktu open sesudah gap. Batas history
  bergantung pada broker dan **Max. bars in chart**.
- Formula spread history adalah `spread_price = spread × point`. Spread nol
  diekspor dengan `spread_price: null` karena biaya historisnya tidak diketahui.
  Snapshot dengan spread nol pada candle M15 terbaru menghasilkan
  `DATA_SPREAD_UNAVAILABLE`. Quote bid sama dengan ask tetap bisa dilaporkan
  untuk diagnostik koneksi.
- Doctor melaporkan `closed_snapshot` hanya saat data lolos pemeriksaan.
  Waktu keputusan adalah waktu tutup candle M15. H1/H4 dengan waktu tutup
  setelah batas itu dikeluarkan sebelum nilai OHLCV dipakai, sehingga
  `evaluated_bars` bisa lebih kecil dari `received_bars`. Waktu tutup
  dihitung sebagai open UTC ditambah durasi nominal timeframe. Snapshot
  mengembalikan `WARMUP` bila jumlah bar yang tersedia belum mencapai
  minimum yang diminta pemanggil. Pengambilan history yang terlalu pendek
  tetap mengembalikan `HISTORY_INSUFFICIENT`.
- History dianggap `DATA_STALE` ketika umur penutupan terakhir mencapai satu
  interval timeframe. Fetch memakai waktu baca UTC. Konfirmasi H1/H4 di doctor
  memakai waktu keputusan M15. Pasar yang sedang tutup tetap bisa menghasilkan
  `DATA_STALE`. Snapshot merupakan input untuk engine sinyal fase berikutnya.
  [Referensi MetaQuotes tentang posisi bar dan batas history](https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrompos_py).
