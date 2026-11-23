# Laporan verifikasi fondasi — 23 November 2026 (Asia/Jakarta)

Scope: scaffold fase A, bukan validasi strategi atau rilis trading.
Lingkungan: Windows, Python 3.12.14 dari runtime bawaan Codex, venv lokal.
Python sistem/launcher belum menemukan instalasi mandiri; runtime bawaan dipakai
untuk QA. Tidak ada login broker atau operasi order yang dijalankan.

| Pemeriksaan | Status | Bukti / perintah |
|---|---|---|
| Inspeksi 6 berkas awal dan preservasi hash | PASS | Seluruh SHA256 cocok. Tes regresi membandingkan keenam berkas dengan BASELINE_HASHES.json dan ikut dijalankan oleh pytest di CI. |
| Sintaks Python (15 file), TOML dan JSON | PASS | ast.parse, compileall, tomllib, json.loads |
| Sintaks PowerShell 4 script | PASS | System.Management.Automation.Language.Parser |
| Struktur YAML workflow CI | PASS | Pemeriksaan trigger push/PR, matrix OS/Python dan permission read-only. |
| Pytest fondasi | PASS | `scripts/test_offline.ps1`: 96 passed, tanpa skip (termasuk AU-004). JUnit di `reports/pytest.xml`. |
| Publisher dry-run | PASS | `python scripts/publish_issues.py --dry-run --provider auto`: 33 issue |
| .gitignore runtime/privacy | PASS | git check-ignore .env, data/private.csv, logs/private.jsonl, models/private.joblib dan .venv |
| Instal editable / import | PASS | `pip install --no-index --no-build-isolation -e ".[dev]"` setelah dependensi tersedia, `aurum.cli doctor --offline` menunjukkan SIGNAL_ONLY |
| Ruff lint / format | PASS | `scripts/test_offline.ps1`: 17 file sesuai format, lint lulus |
| Mypy strict | PASS | `scripts/test_offline.ps1`: 6 modul lulus |
| Compile MetaEditor | NOT RUN | MetaEditor tidak ditemukan; runner exit 2 dan reports/mql5-status.txt |
| MT5/broker integration dan forward demo | NOT RUN | Terminal/account/data broker tidak tersedia untuk pengujian ini |
| Training ML v3 dan backtest broker | NOT RUN | Modul masih backlog; tidak ada hasil akurasi/P&L |
| Streamlit runtime / visual QA | NOT RUN | Extra dashboard tidak dipasang; source syntax diperiksa |
| Coverage safety | PASS | Ambang 90% per modul dengan pengukuran branch. Hasil lokal: config 99%, CLI 97%, data quality 100%, MT5 client 100%. |
| GitHub Actions AU-003 | PASS | [Run PR #35](https://github.com/akbar875/TradingGold/actions/runs/45051372481) pada commit implementasi `2bdeab2`: empat job lulus (Ubuntu/Windows × Python 3.11/3.12), empat artefak tes tersedia. |
| Issue remote AU-003 | OPEN | Scope terverifikasi terhadap [GitHub #3](https://github.com/akbar875/TradingGold/issues/3). |

JUnit, coverage XML dan output compile disimpan di `reports/`, yang diabaikan
oleh Git. CI mengunggah laporan pytest dan coverage dari setiap kombinasi
OS/Python yang mencapai tahap pembuatan laporan. Runner bersama menghentikan
pemeriksaan bila satu modul safety di bawah 90%. Ambang 100% sengaja dicoba
pada CLI yang terukur 97% dan menghasilkan exit 2.

Tes meliputi penolakan konfigurasi eksekusi/tipe salah/angka nonfinite, closed-bar
boundary dan OHLC invalid, diagnosa MT5 mock dengan masking dan shutdown, offline
doctor tanpa broker, perintah yang belum tersedia exit nonzero, static order API
checks, parity default Python/EA/preset, 33 issue unik, schema JSON valid, publisher
dry-run tanpa jaringan dan skip marker issue existing.

AU-003 memeriksa keberadaan kedua preset wajib, penolakan auto trading di preset,
kegagalan inisialisasi MT5 dan pemilihan simbol, data simbol/tick yang hilang,
serta shutdown dan exit CLI saat diagnostik melempar exception.

Pada run awal ada error temp sandbox pytest dan mock importlib yang terlalu luas.
Temp dipindah ke reports/pytest-tmp dan mock dibatasi pada modul adapter. Run ulang
54 tes PASS. Tindak lanjut AU-001/AU-002 menambah regresi untuk hash keenam
baseline, YAML ambigu atau invalid, angka di luar rentang float, dan konfigurasi
efektif dari override simbol. Tes diagnostik memakai mock. Verifikasi MetaEditor
dan broker tidak dijalankan ulang pada tindak lanjut ini.

## AU-004 — runner compile dan pelaporan, 23 November 2026

Branch `codex/au-004-compile-reporting`, [PR #36](https://github.com/akbar875/TradingGold/pull/36),
commit implementasi `3c4b2e4`, Windows PowerShell 7, Python 3.12.14.
Dependency AU-002 DONE. `scripts/test_offline.ps1` PASS: **96 passed, tanpa skip**,
17 file lolos format/lint, 6 modul lolos mypy. Coverage safety tetap config 99%,
CLI 97%, data quality 100%, MT5 client 100%. JUnit dan coverage di `reports/`.
Hash keenam baseline ikut diverifikasi oleh tes dan tidak berubah.

18 tes baru menjalankan runner PowerShell asli dalam workspace fixture berspasi.
Tes memverifikasi dua format ringkasan sukses (log UTF-16 BOM), termasuk
WaitForExit/Refresh/ExitCode pada proses PowerShell nyata yang exit 0; compiler/source/
include tidak tersedia, timeout invalid, launch failure setelah PASS lama,
timeout dengan proses PowerShell nyata yang dipastikan berhenti, exit compiler
nonzero, log 10 errors/warning/summary ambigu/diagnostic error/hilang, dan EX5
hilang/kosong/lama. Tes sukses memakai artifact dummy, **bukan hasil compile EA**.
Enam tes publisher completion memverifikasi dry-run tanpa jaringan, penyelesaian
issue sendiri, dan penolakan owner/merge/base/link yang tidak sesuai.

Parse PowerShell PASS. Runner tanpa METAEDITOR_PATH: **NOT RUN**, reason
`COMPILER_UNAVAILABLE`, exit 2; bukti `reports/mql5-status.txt`. MetaEditor,
kompilasi MQL5 nyata, terminal/broker dan demo forward **NOT RUN** pada pekerjaan
ini. Tidak ada operasi order atau perubahan mode aman EA.

Runner baru memakai `/include` dan `/log` sesuai
[dokumentasi MetaEditor](https://www.metatrader5.com/en/metaeditor/help/beginning/integration_ide),
workspace build unik, log summary tunggal 0 errors/0 warnings, EX5 baru tidak
kosong, timeout 120 detik (1..600), dan reason code dengan exit 0/1/2.
Status run sebelumnya dibatalkan sebelum validasi/launch.

CI [run PR #36](https://github.com/akbar875/TradingGold/actions/runs/45053773769)
pada `f7a249b`: keempat job Windows/Linux × Python 3.11/3.12 PASS.
Job Windows menjalankan 96 tes; job Linux melewati 18 kontrak runner Windows
secara eksplisit. Hasil ini tidak menyatakan kompilasi MetaEditor PASS.

## AU-005 — diagnostik broker dan history MT5, 23 November 2026

[PR #37](https://github.com/akbar875/TradingGold/pull/37), commit implementasi
`3b0d22c`, Windows PowerShell 7 dan Python 3.12.14. `scripts/test_offline.ps1`
PASS dengan **145 tes**, 17 file lulus Ruff, dan 6 modul lulus mypy. Coverage
branch safety config 99%, CLI 97%, data quality 100%, adapter MT5 99%.
Regresi hash enam baseline ikut lulus.

Tes mock memeriksa suffix persis, metadata broker, leverage aktual, masking
akun, izin ditolak, quote basi dan spread nonfinite. Untuk M15/H1/H4, tes
memeriksa posisi 1, missing/short history, candle berjalan, NaN, duplikasi,
urutan terbalik, history basi, dan pelaporan gap. Tes perubahan sesi
memastikan data dibuang dan koneksi ditutup. Kedua perintah juga diuji dari
shell tanpa paket MT5. Keduanya mengembalikan `NOT_READY /
MT5_PACKAGE_MISSING` dan exit 1.

Integrasi MT5/broker demo **NOT RUN** karena paket MT5 tidak terpasang dan
terminal demo tidak tersedia untuk verifikasi. Kompilasi EA **NOT RUN** karena
MetaEditor tidak tersedia. Mode safe tetap diuji offline. Klasifikasi gap sesi
sebelumnya dilacak di AU-006. Freshness registry model dilacak di AU-020.

## AU-006 — kualitas candle dan snapshot UTC, 23 November 2026

[PR #38](https://github.com/akbar875/TradingGold/pull/38), commit implementasi
`2969bf8`. `scripts/test_offline.ps1` **PASS**, 176 tes pada Windows dan Python 3.12.14.
Ruff, pemeriksaan format, mypy, doctor offline, dan regresi hash keenam
baseline lulus. Coverage branch modul config 99%, CLI 97%, data quality 99%,
dan adapter MT5 98%.

Regresi memeriksa overlap walaupun timestamp meningkat, gap tanpa jadwal
yang gagal di CLI, penutupan sesi UTC yang mencakup seluruh gap, spread
harga berdasarkan broker point, spread nol pada snapshot M15, OHLCV yang
rusak, outlier, dan batas stale satu interval. Fixture MT5 memverifikasi
posisi 1 dan penolakan candle terbuka. Regresi snapshot mengubah nilai
candle masa depan dan memverifikasi hasil lama tetap sama. `doctor` diuji
dengan H4 yang baru tutup setelah batas keputusan M15.

Integrasi terminal MT5/broker demo **NOT RUN** karena paket dan terminal demo
untuk pengujian tidak tersedia. Kompilasi MetaEditor **NOT RUN** karena
compiler tidak tersedia. Pengujian sinyal final **NOT RUN** karena engine
sinyal masih scaffold. Tes snapshot memverifikasi kontrak input ke engine.

## AU-007 — indikator MQL5 closed-bar, 23 November 2026

[PR #39](https://github.com/akbar875/TradingGold/pull/39), commit implementasi
`19d7b8d`. `scripts/test_offline.ps1` **PASS**, 177 tes pada Windows dengan
Python 3.12.14 dan MinGW g++ 14.2. Ruff, format, mypy, doctor offline, dan
verifikasi hash keenam baseline lulus.

Fixture C++ menjalankan `Indicators.mqh` produksi dengan API terminal stub.
Tes memeriksa timeframe, periode, buffer, angka fixture, cutoff H1 tepat di
pergantian jam, dan nilai H1 yang tetap sama ketika data setelah cutoff berubah.
Kasus negatif meliputi periode invalid, pembuatan handle gagal sebagian,
history atau kalkulasi belum siap, gap M15/H1, buffer parsial, EMPTY_VALUE,
NaN, ATR negatif, rollover saat membaca, serta pemulihan pada tick berikutnya.
Fixture memverifikasi pelepasan handle berulang dan pembuatan ulang.

Compile MetaEditor **NOT RUN** (`COMPILER_UNAVAILABLE`, exit 2,
`reports/mql5-status.txt`). Pengujian attach/detach, Strategy Tester, dan
perbandingan nilai indikator native **NOT RUN** karena MetaEditor dan terminal
tidak tersedia. Fixture memeriksa kontrak pembacaan dan cleanup offline.
EA tetap menampilkan WAIT. BUY/SELL, ownership, dan retcode mengikuti issue
engine sinyal dan eksekusi.

Checklist verifikasi terminal untuk AU-007

1. Jalankan `scripts/compile_mql5.ps1 -MetaEditor <path>` dan simpan log serta
   EX5 baru.
2. Di chart demo dengan preset Signal_Only, bandingkan nilai setiap buffer
   dengan Data Window indikator bawaan untuk simbol, timestamp sumber,
   timeframe, dan periode yang sama. Periksa pergantian M15 dan jam H1.
   Selama candle M15 berjalan, nilai snapshot tertutup harus tetap sama.
3. Uji history belum siap, periode invalid, lepas dan pasang ulang EA.
   Periksa panel atau Journal untuk reason code serta status WAIT.

## AU-008 — market regime H1/H4, 23 November 2026

[PR #40](https://github.com/akbar875/TradingGold/pull/40), commit implementasi
`fa2942f`. Hasil CI tercantum di [checks PR](https://github.com/akbar875/TradingGold/pull/40/checks).

`scripts/test_offline.ps1` **PASS** pada Windows dan Python 3.12.14 dengan
**178 tes**. Ruff, format, mypy, doctor offline, dan hash keenam baseline lulus.
Fixture C++ menjalankan `Indicators.mqh` dan `Regime.mqh` dengan API terminal
stub. Fixture dan tes parity memverifikasi periode H4 dan ambang preset,
cutoff H1/H4, pemilihan candle saat pergantian H4, pelepasan handle,
klasifikasi bullish/bearish/range/unsafe, konflik, serta batas ADX, ATR,
spread, dan konsolidasi. Kasus negatif mencakup H4 basi/tidak siap, rollover
selama pembacaan, hasil parsial, gap M15, OHLC rusak, spread nol, broker point
invalid dan ATR baseline invalid. Uji transisi memeriksa pemblokiran arah
saat data gagal, retry setelah history pulih dan perhitungan ulang setelah
handle dibuat kembali.

Compile MetaEditor **NOT RUN** (`COMPILER_UNAVAILABLE`, runner exit 2,
`reports/mql5-status.txt`). Strategy Tester, perbandingan nilai indikator
native, attach/detach, dan terminal demo **NOT RUN** karena MetaEditor serta
terminal untuk pengujian tidak tersedia. EA tetap WAIT dan preset memakai
SignalOnly=true, AutoTrade=false, DemoOnly=true.

## AU-009 — setup entry M15, 24 November 2026

[PR #41](https://github.com/akbar875/TradingGold/pull/41), implementasi
`4394862`. `scripts/test_offline.ps1` **PASS** pada Windows dan Python
3.12.14 dengan **178 tes**. Ruff, format, mypy, doctor offline, serta
verifikasi hash keenam baseline lulus. Hasil CI ada di [checks PR](https://github.com/akbar875/TradingGold/pull/41/checks).

Fixture C++ menjalankan include MQL5 produksi dengan API terminal stub.
Kasus mencakup BUY dan SELL untuk setiap setup, WAIT pada sentuhan intrabar,
body breakout lemah, false breakout, batas retest, batas chase limit,
invalidation, batas stop struktur, dan dua pola pada satu candle. Uji data
mencakup future bar di luar window, gap, OHLC invalid, quote basi/terbalik,
hasil parsial, rollover, dan retry. Stub file menguji klaim lintas instance,
restart, bar lama, kegagalan lock/tulis/flush dan ukuran file rusak. Tes
parity memeriksa kedua preset dan suite memeriksa ketiadaan jalur order.

Compile MetaEditor **NOT RUN** (`COMPILER_UNAVAILABLE`,
`reports/mql5-status.txt`). Strategy Tester dan attach/restart pada terminal
demo **NOT RUN** karena terminal pengujian tidak tersedia. Verifikasi native
masih perlu memeriksa panel WAIT, quote Bid/Ask, dan satu catatan Journal saat
dua chart simbol yang sama berjalan serta setelah EA dipasang ulang.

## Verifikasi manual yang masih dibutuhkan

- Compile source dan include pada MetaEditor, periksa log/artifact baru.
- Pasang EA di chart M15 demo dan verifikasi panel WAIT serta penolakan auto input.
- Setelah modul produk tersedia: history/suffix/freshness, parser bridge lintas
  bahasa, news/session DST, lot/margin/stop/freeze, recovery dan ownership.
- Demo forward dan backtest OOS dengan sumber data/biaya terdokumentasi.
- Jalankan dashboard setelah memasang extras dan periksa empty/error states.
