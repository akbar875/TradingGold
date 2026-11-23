# Aturan strategi Aurum

## Indikator AU-007

EA menggunakan nama simbol chart persis, termasuk suffix broker. Timeframe
indikator tetap M15, H1 dan H4 terlepas dari timeframe chart. H4 ditambahkan oleh AU-008.

| Indikator | Default dan timeframe | Sumber MT5 |
|---|---|---|
| EMA | 20/50 M15, 50/200 H1 dan H4 | `iMA`, `MODE_EMA`, `PRICE_CLOSE`, offset nol |
| RSI | 14 M15 | `iRSI`, `PRICE_CLOSE` |
| MACD | 12/26/9 M15 | `iMACD`, `PRICE_CLOSE`, main buffer 0, signal buffer 1 (SMA 9) |
| ADX, +DI, -DI | 14 M15 | `iADXWilder`, buffer 0, 1, 2 |
| ATR | 14 M15 | `iATR`, satuan harga |

Periode bisa diatur lewat input EA dan kedua preset. Semua periode harus positif.
Periode fast harus lebih kecil dari slow untuk EMA dan MACD. Hitungan pemanasan
minimum pada bar yang dibaca adalah periode EMA, periode + 1 untuk RSI dan ATR,
slow + signal - 1 untuk MACD, serta dua kali periode ADX. History yang dimuat dapat
memengaruhi nilai indikator rekursif. Perbandingan nilai harus memakai history,
parameter, simbol, timeframe, dan timestamp bar yang sama.

EA membaca M15 pada `shift=1`. Waktu keputusan adalah waktu buka bar itu
ditambah 15 menit. Untuk EMA H1/H4, EA memilih bar terbaru dengan waktu tutup
nominal di atau sebelum batas M15. Misalnya keputusan 10.45 memakai H1 yang
buka 09.00. Keputusan 11.00 boleh memakai H1 yang buka 10.00 setelah posisi
H1 tersinkronisasi. Keputusan 11.45 memakai H4 yang buka 04.00 dan keputusan
12.00 boleh memakai H4 yang buka 08.00 setelah H4 tersinkronisasi. Timestamp
panel menggunakan waktu server broker.

Jika bar M15 berjalan tidak bersebelahan dengan bar terakhir, atau bar H1/H4
tertutup tertinggal setidaknya satu intervalnya dari batas keputusan, hasilnya
`INDICATOR_DATA_STALE`.
History yang belum siap menghasilkan `INDICATOR_WARMUP`. Salinan buffer yang
tidak lengkap menghasilkan `INDICATOR_COPY_FAILED`. Nilai kosong, nonfinite,
atau di luar rentang menghasilkan `INDICATOR_VALUE_INVALID`. ATR nol tetap
dapat muncul pada snapshot diagnostik. Perubahan posisi bar saat membaca
menghasilkan `INDICATOR_BAR_CHANGED` dan pembacaan dicoba lagi pada tick berikutnya.
EA hanya menampilkan nilai setelah semua buffer lolos. Jika pembuatan handle
gagal, EA membersihkan handle yang sempat dibuat dan menolak inisialisasi.
Handle juga dilepas saat EA dilepas dari chart.

## Market regime AU-008

Rata-rata ATR berasal dari delapan candle M15 sebelum candle keputusan
(`shift=2..9`). Lebar konsolidasi adalah high tertinggi dikurangi low terendah
dari sembilan candle tertutup (`shift=1..9`). Semua candle harus berurutan
setiap 15 menit dengan OHLC valid. Gap sesi menghasilkan WAIT sampai jendela
kembali lengkap. Spread berasal dari `MqlRates.spread` candle keputusan dan
dikonversi ke satuan harga dengan `SYMBOL_POINT`. Spread nol atau negatif,
ATR saat ini nol, dan baseline ATR yang tidak positif memblokir arah.
Guard spread tick, sesi, rollover dan kalender dicakup oleh AU-016.
Lihat [CopyRates](https://www.mql5.com/en/docs/series/copyrates) dan
[CopyBuffer](https://www.mql5.com/en/docs/series/copybuffer).

| Input EA | Default | Aturan |
|---|---:|---|
| `InpRegimeMinTrendAdx` | 25.0 | ADX M15 minimal untuk tren, rentang valid (0, 100] |
| `InpRegimeAtrSpikeRatio` | 2.0 | ATR saat ini / baseline pada atau di atas batas memblokir arah, input harus > 1 |
| `InpRegimeMaxSpreadAtrRatio` | 0.25 | Spread harga / baseline pada atau di atas batas memblokir arah, input harus > 0 |
| `InpRegimeMaxRangeAtrRatio` | 4.0 | Lebar konsolidasi / baseline maksimal, inklusif, input harus > 0 |

Input harus finite. Nilai bawaan adalah parameter awal untuk diuji.
Klasifikasi berlaku menurut urutan berikut.

| Kondisi | Regime, izin arah, dan alasan |
|---|---|
| Snapshot gagal, rasio tidak valid, atau ATR saat ini nol | `HIGH_VOLATILITY_UNSAFE`, diblokir, `REGIME_DATA_UNSAFE`. Panel juga menampilkan reason code pembacaan jika gagal. |
| Batas ATR atau spread tercapai | `HIGH_VOLATILITY_UNSAFE`, diblokir, `REGIME_ATR_SPIKE` atau `REGIME_SPREAD_TOO_WIDE`. ATR diprioritaskan saat keduanya gagal. |
| Arah EMA H1 dan H4 berlawanan | `REGIME_UNCLASSIFIED`, diblokir, `REGIME_HTF_CONFLICT`. |
| ADX di bawah ambang dan lebar konsolidasi dalam batas | `RANGE`, diblokir, `REGIME_CONSOLIDATION`. |
| ADX memenuhi ambang dan EMA H1/H4/M15 serta +DI/-DI M15 searah | `TREND_UP` atau `TREND_DOWN`, masing-masing mengizinkan evaluasi setup buy atau sell, `REGIME_TREND_CONFIRMED`. |
| Kondisi valid lainnya | `REGIME_UNCLASSIFIED`, diblokir, `REGIME_INCONCLUSIVE`. |

Arah naik berarti EMA fast > slow dan +DI > -DI. Arah turun memakai perbandingan
sebaliknya. Nilai yang sama memberi arah netral. Klasifikasi dihitung ulang dari
snapshot tertutup terbaru pada setiap tick. Hasil lama langsung diganti saat
snapshot gagal. Jika history siap kembali, snapshot yang sama boleh dicoba
ulang. Restart menghitung hasil dari snapshot yang tersedia, tanpa menyimpan
regime sebelumnya atau menunggu beberapa bar konfirmasi.

## Setup entry AU-009

Kedua setup hanya dievaluasi bila AU-008 memberi izin arah. Candle keputusan
adalah M15 `shift=1` dan candle sentuh adalah `shift=2`. Evaluator memerlukan
`key_lookback + max_retest_bars + 2` candle M15 berurutan dengan OHLC valid,
berakhir tepat pada candle keputusan. Gap, salinan parsial, atau rollover
selama pembacaan menghasilkan WAIT. EMA untuk zona pullback adalah EMA fast
yang sudah tersedia saat candle sentuh tutup (`shift=2`).

| Input EA dan preset | Default | Aturan |
|---|---:|---|
| `InpSetupKeyLookback` | 12 | Jumlah bar tertutup sebelum breakout untuk swing high/low, 2–64 |
| `InpSetupMaxRetestBars` | 3 | Jarak breakout ke retest dalam bar, inklusif, 1–16 |
| `InpSetupZoneAtr` | 0.30 | Jarak ekstrem sentuh ke level maksimum di kedua sisi, dalam kelipatan ATR baseline |
| `InpSetupMinBreakoutBodyRatio` | 0.60 | Body searah minimal sebagai fraksi high–low breakout, dalam `(0, 1]` |
| `InpSetupMaxChaseAtr` | 1.50 | Jarak searah maksimum dari level ke harga, minimal sebesar toleransi zona |
| `InpSetupMaxStopAtr` | 3.00 | Jarak maksimum dari harga indikatif ke invalidation struktur, sebelum buffer dan pembulatan |

Ambang ATR memakai rata-rata ATR delapan candle sebelum keputusan seperti
AU-008. Parameter pecahan harus positif dan finite. Nilai ini adalah aturan
awal untuk verifikasi fondasi.

- **TREND_PULLBACK BUY.** Low candle sentuh berada dalam zona EMA fast dan
  candle itu tutup pada atau di atas EMA. Candle keputusan bullish, tutup di
  atas high candle sentuh dan memiliki low yang lebih tinggi. Invalidation
  berada di low candle sentuh. SELL mencerminkan semua perbandingan.
- **BREAKOUT_RETEST BUY.** Resistance adalah high tertinggi pada jendela yang
  berakhir sebelum breakout. Candle breakout buka pada atau di bawah level,
  tutup di atasnya dan memenuhi rasio body. Semua candle antara breakout dan
  retest wajib tutup di atas level. Retest adalah candle sentuh dengan low
  dalam zona dan close di atas level. Candle keputusan memakai aturan
  continuation dan invalidation yang sama seperti pullback. Untuk SELL,
  support adalah low terendah dan semua perbandingan dicerminkan. Breakout
  terbaru yang lolos dipilih. Jika kedua setup valid, breakout diprioritaskan
  sebelum cek harga.
- **Harga dan invalidation.** Setup memakai chart berbasis Bid dan quote dengan
  Bid/Ask valid pada interval M15 setelah keputusan. Bid yang mencapai
  invalidation atau bergerak melewati sisi berlawanan zona memblokir setup.
  Chase limit berlaku pada close konfirmasi dan harga indikatif Ask untuk BUY
  atau Bid untuk SELL. Harga indikatif juga harus di sisi aman invalidation dan
  dalam batas jarak stop struktur. Panel menampilkan alasan WAIT saat salah
  satu pemeriksaan gagal. SL/TP final, biaya, pembulatan broker, dan kelayakan
  R:R mengikuti AU-011.

EA menampilkan kandidat sebagai `SETUP_BUY` atau `SETUP_SELL` di baris
diagnostik. RANGE_REJECTION di luar scope awal.

## Skor heuristik dan alasan keputusan AU-010

Kandidat yang lolos gate teknikal memiliki `Heuristic score` dalam skala 0–100.
EA menjumlahkan bobot komponen yang `PASS` dan menampilkan nilai pembanding
untuk setiap komponen. Nilai bersumber dari snapshot dan struktur bar tertutup.
Quote berjalan menentukan apakah kandidat masih layak melalui cek AU-009.

| Komponen | Bobot | Kondisi lulus dan bukti |
|---|---:|---|
| Setup | 30 | Setup terkonfirmasi. Tampilkan level dan invalidation. |
| EMA H1 | 15 | EMA cepat di atas EMA lambat untuk BUY dan di bawahnya untuk SELL. Tampilkan kedua EMA. |
| EMA H4 | 15 | Aturan arah yang sama pada H4. Tampilkan kedua EMA. |
| ADX M15 | 15 | ADX mencapai `InpRegimeMinTrendAdx`. Tampilkan ADX dan ambangnya. |
| MACD M15 | 15 | Main di atas signal untuk BUY dan di bawahnya untuk SELL. Tampilkan kedua nilai. |
| RSI M15 | 10 | RSI di atas 50 untuk BUY dan di bawah 50 untuk SELL. Tampilkan RSI dan 50. |

Empat komponen pertama mendokumentasikan prasyarat kandidat. MACD dan RSI
menambah skor ketika searah, sehingga kandidat yang lolos memiliki skor 75–100.
Bobot AU-010 tetap dan totalnya 100. EA tidak memakai ambang skor tambahan.
Skor mengukur dukungan aturan heuristik. Probabilitas model memiliki kontrak
tersendiri pada bridge AU-021.

Keputusan entry selalu `WAIT`. Panel memakai alasan utama dan menampilkan
gate gagal lain yang dapat dievaluasi. Prioritasnya mencakup kill switch dan
koneksi, validitas akun/data, lonjakan ATR dan spread bar, news, konflik arah
dan validitas setup, lalu AI. Ketika prasyarat data gagal, gate yang bergantung
pada data itu dilewati. Bila news diwajibkan, `NEWS_UNKNOWN` memblokir entry.
Bila AI diwajibkan, `AI_UNAVAILABLE` juga tercatat. `ENGINE_NOT_IMPLEMENTED`
dipakai ketika tidak ada gate lain yang gagal. Kandidat teknikal yang valid
dapat tetap terlihat dengan skor meskipun news atau AI memblokir entry.
Kedua preset tetap signal-only, auto trade nonaktif, dan demo-only.

ID kandidat `AUR1-…` memakai digest deterministik dari akun dan server broker,
nama simbol persis, timeframe, waktu buka bar tertutup dalam jam server,
setup, dan arah. Quote, skor, serta restart tidak mengubah ID untuk identitas
yang sama. Digest dipakai untuk korelasi dan tidak menampilkan login mentah.
Hasil tanpa kandidat tidak menampilkan ID atau skor.

Journal mencatat `SETUP_CONFIRMED` sebagai event diagnostik dengan ID, skor,
bukti, dan keputusan `WAIT`. Klaim dibatasi sekali per akun, server, simbol,
dan bar M15 pada terminal yang sama. EA menyimpan timestamp di
`MQL5/Files/Aurum_signal_v1_*.bin` sebelum mencatat event, dengan file dibuka
eksklusif antar-chart. File AU-009 memakai scope berbeda, sehingga event pada
bar aktif bisa dicatat sekali saat upgrade. `DUPLICATE_SIGNAL` menandai event yang
sudah diklaim, dengan kandidat tetap terlihat di panel. File rusak atau akses
gagal menghasilkan `SETUP_STATE_UNAVAILABLE` dan mengosongkan kandidat. Jika
proses terhenti setelah timestamp tersimpan dan sebelum penulisan Journal,
event bisa terlewat. Strategy Tester memakai memori per run. State eksekusi dan
rekonsiliasi order mengikuti AU-014.
