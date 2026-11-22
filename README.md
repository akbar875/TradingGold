# TradingGold — Aurum Expert AI MT5

Fondasi pengembangan Aurum v3 untuk XAUUSD pada MetaTrader 5 Windows.
**Status: scaffolding fase A, belum siap trading atau rilis produk.**

Default `SIGNAL_ONLY=true`, `AutoTrade=false`, `DemoOnly=true`. EA saat ini
hanya menampilkan `WAIT / ENGINE_NOT_IMPLEMENTED`. Tidak ada jalur order pada
Python, dashboard, maupun EA fondasi ini. Engine teknikal, eksekusi demo,
ML v3, bridge runtime dan backtest masih pekerjaan lanjutan.

## Mulai di Windows

Pasang Python 3.11+ 64-bit, lalu dari root repo:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m aurum.cli doctor --offline
.\.venv\Scripts\python.exe -m aurum.cli show-config
.\scripts\test_offline.ps1
```

`doctor --offline` memeriksa konfigurasi tanpa menghubungi broker, dengan status
`OFFLINE / BROKER_NOT_CHECKED`. Untuk diagnostik koneksi opsional:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[mt5]"
.\.venv\Scripts\python.exe -m aurum.cli doctor --symbol XAUUSDm
```

Gunakan nama simbol broker persis. Diagnostik awal memeriksa koneksi, akun masked,
leverage, izin dan tick/spread. Pemeriksaan history, Common Files dan freshness
model belum lengkap (AU-005). Tidak perlu memasukkan kredensial ke repo.

## Dashboard awal

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dashboard]"
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Dashboard read-only menunjukkan empty states dan konfigurasi Python. Status
koneksi tetap belum diperiksa; tidak ada harga atau performa buatan.

## Struktur

```text
python/aurum/       konfigurasi, kontrak tipe, validator closed-bar, doctor, CLI
mt5/               EA diagnostik, Include/Aurum, preset non-eksekusi
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
`fetch-data`, `train`, `evaluate`, `predict`, `run`, `backtest`, `export-signals`
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
menutup atau mengubah issue existing.

Lihat [laporan tes](docs/TEST_REPORT.md), [instalasi MT5](docs/INSTALL_WINDOWS_MT5.md),
dan [aturan risiko](docs/RISK_MANAGEMENT.md). Leverage adalah pengaturan broker.
Belum ada hasil training v3, backtest broker, atau forward demo terverifikasi.
Lisensi distribusi belum ditetapkan pemilik repo.
