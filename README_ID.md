# Aurum Expert AI XAUUSD (MetaTrader 5)

Versi 2.0. Paket berisi Expert Advisor (MQL5) dan model machine learning lokal (Python). Ditujukan untuk chart XAUUSD M15. Ini **alat bantu keputusan dan eksperimen**, bukan layanan sinyal terverifikasi. Tidak ada jaminan laba. Kode MQL5 belum diuji kompilasi di MetaEditor karena lingkungan ini tidak menyediakan terminal MT5. Uji dan perbaiki error kompilasi jika muncul.

## Komponen

- `Aurum_Expert_AI_XAUUSD.mq5` : EA MT5. Menganalisis tren H1, EMA20/50 M15, RSI, MACD, ADX, breakout/pullback, swing low/high dan ATR. Menghasilkan BUY/SELL/WAIT, Entry, SL, TP dan lot maksimum berdasarkan risiko. Mengatur break-even di 1R dan trailing stop setelah 1,5R ketika opsi AutoTrade aktif.
- `aurum_ai.py` : Machine learning Random Forest, dilatih dari history XAUUSD M15 broker yang sama. Label dibuat dari barrier harga pada delapan candle berikutnya, hanya untuk training. Data candle yang masih terbentuk **tidak** dipakai untuk prediksi. Python tidak pernah mengirim order.
- `requirements.txt` : dependensi Python.
- `test_offline.py` : uji fitur dan training memakai data sintetis, tanpa koneksi broker.

## Instalasi cepat. MT5 tanpa AI Python

1. Buka MetaTrader 5 desktop di Windows, login ke **akun demo**.
2. Buka menu `File` > `Open Data Folder` > `MQL5` > `Experts`.
3. Tempel `Aurum_Expert_AI_XAUUSD.mq5`, buka di MetaEditor (F4), kemudian tekan **F7** (Compile).
4. Buka chart **XAUUSD** timeframe **M15**. Pilih EA dari Navigator kemudian drag ke chart.
5. Biarkan `InpEnableAutoTrade = false` dan `InpRequirePythonAI = false` pada awalnya. Panel pada chart memberi rekomendasi berdasarkan aturan, bukan model ML.
6. Untuk mengevaluasi kinerja historis, buka `View` > `Strategy Tester`. Pilih periode yang mencakup tren dan sideways, tick real, lalu uji akun demo.

## Instalasi machine learning sungguhan (Windows)

1. Instal Python versi 64-bit yang didukung paket `MetaTrader5` pada sistem kamu. Instal dependensi dengan:

   ```powershell
   cd C:\path\to\Aurum_Expert_AI_MT5
   py -m pip install -r requirements.txt
   ```
2. Jalankan terminal MT5 Windows, login akun broker, dan pastikan simbol XAUUSD tersedia di Market Watch. Muat history M15 minimal sekitar 3.000 candle, idealnya 8.500 atau lebih.
3. Jalankan satu kali untuk mengecek model dan folder output:

   ```powershell
   py aurum_ai.py --symbol XAUUSD --once
   ```
4. Lanjutkan sebagai proses aktif agar sinyal diperbarui saat ada candle M15 baru:

   ```powershell
   py aurum_ai.py --symbol XAUUSD
   ```
5. Di input EA aktifkan `InpRequirePythonAI = true`. Jika Python berhenti, data lambat, prediksi tidak cocok dengan akun / simbol / waktu candle, atau probabilitas model tidak memenuhi batas, EA memberi **WAIT**.
6. Untuk simbol broker dengan suffix, jalankan dengan nama persis, misalnya `--symbol XAUUSDm`, dan pasang EA di chart `XAUUSDm`.

**Cara kerja:** Python membaca data pasar lewat integrasi MT5, membuat fitur historis, melatih model, mengevaluasi model dengan bagian terakhir data yang tidak termasuk data training, lalu menulis file sinyal ke folder bersama terminal MT5 (`Common/Files`). EA membaca file itu sebagai konfirmasi. Model menyimpan laporan `models/*.metrics.json`. Skor model tidak terkalibrasi sebagai probabilitas keuntungan; laporan klasifikasi historis bukan backtest P/L.

## Kapan BUY, SELL, WAIT?

EA mencari arah tren EMA50 terhadap EMA200 pada H1. Pada M15, EA memeriksa posisi EMA20/50, candle konfirmasi breakout atau pullback, kekuatan tren ADX, RSI, MACD, dan arah DI. Untuk BUY atau SELL harus lolos syarat penting, skor aturan minimum (default 80/100), batas spread serta jarak harga dari candle sinyal. Jika salah satu pengaman kritis tidak lolos, EA memberi WAIT. Skor 80/100 **bukan estimasi peluang menang 80%**.

- Entry adalah harga Ask untuk BUY, Bid untuk SELL, dihitung ulang saat analisis.
- SL berdasarkan swing high/low dan minimal kelipatan ATR, dengan batas stop maksimum 3 ATR. Jika terlalu jauh, EA tidak menyarankan entry.
- TP berdasarkan jarak risiko ke SL, default risk-reward 1:2,2.
- Lot berdasarkan risiko uang aktual memakai `OrderCalcProfit` sesuai spesifikasi kontrak broker. Jika lot minimum melebihi budget risiko, EA memberi WAIT. Perhitungan ini tidak menjamin kerugian maksimal karena gap/slippage/komisi/swap.
- Saat auto trading diaktifkan, break-even dipertimbangkan setelah +1R, dan trailing stop setelah +1,5R. SL tidak dilonggarkan. Perubahan SL dapat ditolak oleh broker.

## Leverage 1:2000 dan pengaman

Leverage **ditetapkan broker pada akun**, bukan oleh EA. Input `InpRequire2000 = true` membuat EA menolak **order otomatis** jika leverage akun bukan persis 1:2000. Bahkan pada leverage tinggi, posisi tetap rugi berdasarkan besaran lot dan perubahan harga; margin kecil tidak berarti risiko kecil.

Nilai default:

| Parameter | Default |
|---|---:|
| Mode auto trading | OFF |
| Khusus akun demo | ON |
| Wajib leverage 1:2000 untuk order otomatis | ON |
| Risiko per transaksi | 0,25% ekuitas |
| Lot maksimum | 0,05 |
| Batas drawdown sejak baseline harian | 2% |
| Maksimum entry per hari | 3 |
| Maksimum margin satu order | 15% margin bebas |
| Break-even | 1R |
| Trailing stop | mulai 1,5R |
| Stop Loss maksimal | 3 ATR |

Baseline drawdown harian adalah nilai ekuitas saat EA pertama kali aktif pada hari broker itu, bukan mutlak ekuitas pukul 00.00. Batas harian memblokir **entry baru**, tidak otomatis menutup semua posisi. Pengaman EA tidak mencegah stop-out akibat gap atau gangguan koneksi. SL/TP terpasang di broker ketika order diterima.

## Mengaktifkan auto trading (hanya setelah uji)

1. Uji dahulu di Strategy Tester. Ingat model Python perlu proses hidup secara terpisah dan file historisnya tidak direproduksi otomatis pada Strategy Tester, sehingga mode AI wajib dimatikan untuk backtest standar EA tanpa bridge tester khusus.
2. Gunakan akun **demo** dengan leverage 1:2000, ubah `InpEnableAutoTrade=true`. Aktifkan Algo Trading di terminal.
3. Untuk akun real, harus **secara eksplisit** mengubah `InpDemoOnly=false`. Gunakan pertimbangan sendiri setelah uji forward di akun demo. Pada akun real, leverage 1:2000 memungkinkan kerugian sangat cepat.

## Keterbatasan

- Bukan AI bahasa yang membaca berita. Model hanya membaca history harga/volume tick broker; tidak memproses berita suku bunga AS, NFP, CPI atau pernyataan bank sentral. Hindari trading saat rilis penting dengan mengawasi kalender ekonomi secara manual.
- Belum mencakup slippage empiris, komisi/swap menyeluruh, real-time calendar, spread ekstrem mendadak setelah order, atau kendala koneksi terminal.
- Sinyal dievaluasi pada candle M15 yang sudah tutup. Entry otomatis dapat dilakukan hanya dalam 120 detik pertama candle berikutnya.
- Python dan EA perlu berjalan bersamaan untuk mode machine learning. Program Python hanya mendukung terminal MT5 desktop Windows. Python tidak boleh dipakai untuk menguji strategi ML di tester tanpa pipeline pengujian historis terpisah.
- Tidak dijamin cocok pada setiap broker. Compile dan cek log `Experts` serta `Journal`.
