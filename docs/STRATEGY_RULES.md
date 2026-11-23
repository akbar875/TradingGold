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

## Sinyal dan struktur pasar

Snapshot lengkap tetap menghasilkan `WAIT | ENGINE_NOT_IMPLEMENTED`.
Swing serta support/resistance FR-004 mengikuti AU-009 untuk setup dan AU-011
untuk SL/TP. Invalidation, chase limit, dan bobot skor mengikuti implementasi
setup/scoring.
BUY/SELL bergantung pada gate pasar, AI saat diwajibkan, dan risiko.
Setup target tetap TREND_PULLBACK dan BREAKOUT_RETEST. RANGE_REJECTION di luar
scope awal. Skor 0–100 adalah heuristik.
