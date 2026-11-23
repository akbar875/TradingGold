# TradingGold — Aurum Expert AI MT5

Fondasi pengembangan Aurum v3 untuk XAUUSD pada MetaTrader 5 Windows.
**Status: scaffolding fase A, belum siap trading atau rilis produk.**

Default `SIGNAL_ONLY=true`, `AutoTrade=false`, `DemoOnly=true`. EA
menampilkan snapshot indikator M15/H1 saat siap. Aksi tetap `WAIT` karena
engine sinyal belum tersedia. Python, dashboard, dan EA fondasi ini
tidak memiliki jalur order. Lihat [aturan indikator](docs/STRATEGY_RULES.md).

## Mulai di Windows

Pasang Python 3.11+ 64-bit, lalu dari root repo:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m aurum.cli doctor --offline
.\.venv\Scripts\python.exe -m aurum.cli show-config
.\scripts\test_offline.ps1
```

`scripts/test_offline.ps1` menjalankan pemeriksaan yang sama dengan CI.
Di Linux gunakan `python scripts/test_offline.py` setelah memasang extra dev.
Laporan pytest dan coverage tersedia di `reports/`.

`doctor --offline` memeriksa konfigurasi tanpa menghubungi broker, dengan status
`OFFLINE / BROKER_NOT_CHECKED`. Untuk diagnostik koneksi opsional:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mt5]"
.\.venv\Scripts\python.exe -m aurum.cli doctor --symbol XAUUSDm
```

Gunakan nama simbol broker persis dan terminal demo yang sudah login. Doctor
memeriksa koneksi, akun masked, izin, properti simbol dan margin, tick, history
M15/H1/H4, serta keberadaan folder Common Files. Lihat
[kontrak diagnostik dan data](docs/INSTALL_WINDOWS_MT5.md#diagnostik-dan-history-python).

```powershell
.\.venv\Scripts\python.exe -m aurum.cli fetch-data --symbol XAUUSDm --timeframe M15 --bars 2
```

`fetch-data` memvalidasi candle tertutup dan mencetak JSON ke stdout. Untuk
history yang melewati jeda pasar, masukkan jadwal penutupan UTC broker melalui
`--config`. Gap yang belum dijelaskan menghasilkan exit 1 tanpa candle.
Jangan commit keluaran yang berisi data broker atau informasi akun. Lihat
[kontrak kualitas data](docs/INSTALL_WINDOWS_MT5.md#kualitas-candle-dan-snapshot-utc).

## Dashboard awal

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dashboard]"
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Dashboard read-only menunjukkan empty states dan konfigurasi Python. Status
koneksi tetap belum diperiksa; tidak ada harga atau performa buatan.

## Struktur

```text
python/aurum/       konfigurasi, kontrak tipe, validator closed-bar, doctor dan history MT5
mt5/               EA diagnostik, indikator closed-bar, preset non-eksekusi
dashboard/         Streamlit read-only
config/            default aman dan kontrak JSON Schema bridge
tests/             tes offline fondasi dan kasus negatif
scripts/           setup, lint/test, compile MT5, publisher issue
.github/           CI Windows/Linux dan issue templates
docs/              audit, arsitektur, panduan, status dan 33 issue lokal
data/logs/models/  direktori runtime; isinya diabaikan Git
```

Dokumen asli dan baseline tetap di root, tanpa perubahan. `README_ID.md` adalah
panduan **v2 historis**; file yang disebut di sana belum tentu tersedia.
`aurum_ai.py` belum dimigrasikan ke v3 dan tidak dijalankan oleh CLI baru.
`xauusd-trading-demo.html` adalah simulasi paper trading terpisah, bukan dashboard
live. Lihat [audit](docs/BASELINE_AUDIT.md) dan [arsitektur](docs/ARCHITECTURE.md).

## Pekerjaan berikutnya

33 seed issue tersedia di [backlog](docs/ISSUES_BACKLOG.md). Perintah produk akhir
`train`, `evaluate`, `predict`, `run`, `backtest`, `export-signals`
sudah mempunyai antarmuka CLI, tetapi mengembalikan `NOT_IMPLEMENTED` dan exit 2.
Jangan mengartikannya sebagai pipeline yang sudah berjalan.

```powershell
.\.venv\Scripts\python.exe scripts/publish_issues.py --dry-run --provider auto
# Publikasi manual setelah review, jika GitHub CLI terautentikasi tersedia:
.\.venv\Scripts\python.exe scripts/publish_issues.py --publish --provider github
.\scripts\compile_mql5.ps1 -MetaEditor 'C:\Program Files\MetaTrader 5\metaeditor64.exe'
```

Publisher default dry-run, memakai `--body-file`, dan melewati marker AU yang
sudah ada pada issue terbuka maupun tertutup. Hanya GitHub didukung pada scaffold
ini. Label opsional `--label` harus sudah tersedia di repo; publikasi tidak
menutup atau mengubah issue existing pada mode publikasi seed.
Penyelesaian issue milik akun sendiri melalui publisher memerlukan
`--complete AU-004 --pull-request <nomor> --publish`; tanpa `--publish` tetap
dry-run. Publisher memverifikasi PR sudah merged ke `main` repo ini dan memiliki
baris `Issue: #<issue>` (atau closing keyword GitHub). Issue milik orang lain ditolak.

Runner compile memakai workspace unik di `reports/mql5/`, timeout default
120 detik, dan exit 0/1/2 untuk PASS/FAIL/NOT RUN. Path log serta EX5 dicatat
di `reports/mql5-status.txt`; lihat panduan instalasi sebelum menyalin hasilnya
ke terminal. Tes compiler mock tidak menjadi bukti compile MetaEditor nyata.

Lihat [laporan tes](docs/TEST_REPORT.md), [instalasi MT5](docs/INSTALL_WINDOWS_MT5.md),
dan [aturan risiko](docs/RISK_MANAGEMENT.md). Leverage adalah pengaturan broker.
Belum ada hasil training v3, backtest broker, atau forward demo terverifikasi.
Lisensi distribusi belum ditetapkan pemilik repo.
