# Aturan strategi Aurum

## Indikator AU-007

EA menggunakan nama simbol chart persis, termasuk suffix broker. Timeframe
indikator tetap M15 dan H1 terlepas dari timeframe chart.

| Indikator | Default dan timeframe | Sumber MT5 |
|---|---|---|
| EMA | 20/50 M15, 50/200 H1 | `iMA`, `MODE_EMA`, `PRICE_CLOSE`, offset nol |
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
ditambah 15 menit. Untuk EMA H1, EA memilih bar terbaru dengan waktu tutup
nominal di atau sebelum batas M15. Misalnya keputusan 10.45 memakai H1 yang
buka 09.00. Keputusan 11.00 boleh memakai H1 yang buka 10.00 setelah posisi
H1 tersinkronisasi. Timestamp panel menggunakan waktu server broker.

Jika bar M15 berjalan tidak bersebelahan dengan bar terakhir, atau H1 tertutup
tertinggal satu jam atau lebih dari batas keputusan, hasilnya `INDICATOR_DATA_STALE`.
History yang belum siap menghasilkan `INDICATOR_WARMUP`. Salinan buffer yang
tidak lengkap menghasilkan `INDICATOR_COPY_FAILED`. Nilai kosong, nonfinite,
atau di luar rentang menghasilkan `INDICATOR_VALUE_INVALID`. ATR nol tetap
dapat muncul pada snapshot diagnostik. Perubahan posisi bar saat membaca
menghasilkan `INDICATOR_BAR_CHANGED` dan pembacaan dicoba lagi pada tick berikutnya.
EA hanya menampilkan nilai setelah semua buffer lolos. Jika pembuatan handle
gagal, EA membersihkan handle yang sempat dibuat dan menolak inisialisasi.
Handle juga dilepas saat EA dilepas dari chart.

## Sinyal dan struktur pasar

Snapshot lengkap tetap menghasilkan `WAIT | ENGINE_NOT_IMPLEMENTED`.
AU-008 menangani konfirmasi H4 dan market regime. Swing serta support/resistance
FR-004 mengikuti AU-009 untuk setup dan AU-011 untuk SL/TP. Threshold,
invalidation, chase limit, dan bobot skor mengikuti implementasi setup/scoring.
BUY/SELL bergantung pada gate pasar, AI saat diwajibkan, dan risiko.
Setup target tetap TREND_PULLBACK dan BREAKOUT_RETEST. RANGE_REJECTION di luar
scope awal. Skor 0–100 adalah heuristik.
