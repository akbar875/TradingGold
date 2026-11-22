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
| Struktur YAML workflow CI | PASS | safe_load dan pemeriksaan matrix OS serta permissions |
| Pytest fondasi | PASS | `scripts/test_offline.ps1`: 72 passed, tanpa skip. JUnit di `reports/pytest.xml`. |
| Publisher dry-run | PASS | `python scripts/publish_issues.py --dry-run --provider auto`: 33 issue |
| .gitignore runtime/privacy | PASS | git check-ignore .env, data/private.csv, logs/private.jsonl, models/private.joblib dan .venv |
| Instal editable / import | PASS | `pip install --no-index --no-build-isolation -e ".[dev]"` setelah dependensi tersedia, `aurum.cli doctor --offline` menunjukkan SIGNAL_ONLY |
| Ruff lint / format | PASS | `scripts/test_offline.ps1`: 16 file sesuai format, lint lulus |
| Mypy strict | PASS | `scripts/test_offline.ps1`: 6 modul lulus |
| Compile MetaEditor | NOT RUN | MetaEditor tidak ditemukan; runner exit 2 dan reports/mql5-status.txt |
| MT5/broker integration dan forward demo | NOT RUN | Terminal/account/data broker tidak tersedia untuk pengujian ini |
| Training ML v3 dan backtest broker | NOT RUN | Modul masih backlog; tidak ada hasil akurasi/P&L |
| Streamlit runtime / visual QA | NOT RUN | Extra dashboard tidak dipasang; source syntax diperiksa |
| Coverage safety | PASS | Ambang 90% per modul dengan pengukuran branch. Hasil lokal: config 99%, CLI 97%, data quality 100%, MT5 client 100%. |
| GitHub Actions AU-003 | NOT RUN | Hasil matrix untuk perubahan AU-003 belum diverifikasi. |
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

## Verifikasi manual yang masih dibutuhkan

- Compile source dan include pada MetaEditor, periksa log/artifact baru.
- Pasang EA di chart M15 demo dan verifikasi panel WAIT serta penolakan auto input.
- Setelah modul produk tersedia: history/suffix/freshness, parser bridge lintas
  bahasa, news/session DST, lot/margin/stop/freeze, recovery dan ownership.
- Demo forward dan backtest OOS dengan sumber data/biaya terdokumentasi.
- Jalankan dashboard setelah memasang extras dan periksa empty/error states.
