# Laporan verifikasi fondasi — 23 November 2026 (Asia/Jakarta)

Scope: scaffold fase A, bukan validasi strategi atau rilis trading.
Lingkungan: Windows, Python 3.12.14 dari runtime bawaan Codex, venv lokal.
Python sistem/launcher belum menemukan instalasi mandiri; runtime bawaan dipakai
untuk QA. Tidak ada login broker atau operasi order yang dijalankan.

| Pemeriksaan | Status | Bukti / perintah |
|---|---|---|
| Inspeksi 6 berkas awal dan preservasi hash | PASS | BASELINE_AUDIT.md, BASELINE_HASHES.json, seluruh SHA256 cocok |
| Sintaks Python (15 file), TOML dan JSON | PASS | ast.parse, compileall, tomllib, json.loads |
| Sintaks PowerShell 4 script | PASS | System.Management.Automation.Language.Parser |
| Struktur YAML workflow CI | PASS | safe_load dan pemeriksaan matrix OS serta permissions |
| Pytest fondasi | PASS | `python -m pytest -q --junitxml=reports/pytest.xml`: 54 passed |
| Publisher dry-run | PASS | `python scripts/publish_issues.py --dry-run --provider auto`: 33 issue |
| .gitignore runtime/privacy | PASS | git check-ignore .env, data/private.csv, logs/private.jsonl, models/private.joblib dan .venv |
| Instal editable / import | PASS | `pip install --no-index --no-build-isolation -e ".[dev]"` setelah dependensi tersedia, `aurum.cli doctor --offline` menunjukkan SIGNAL_ONLY |
| Ruff lint / format | PASS | `scripts/test_offline.ps1`: 15 file sesuai format, lint lulus |
| Mypy strict | PASS | `scripts/test_offline.ps1`: 6 modul lulus |
| Compile MetaEditor | NOT RUN | MetaEditor tidak ditemukan; runner exit 2 dan reports/mql5-status.txt |
| MT5/broker integration dan forward demo | NOT RUN | Terminal/account/data broker tidak tersedia untuk pengujian ini |
| Training ML v3 dan backtest broker | NOT RUN | Modul masih backlog; tidak ada hasil akurasi/P&L |
| Streamlit runtime / visual QA | NOT RUN | Extra dashboard tidak dipasang; source syntax diperiksa |
| GitHub Actions remote | NOT RUN | Workflow tersedia; hasil CI remote belum diamati |
| Issue remote | NOT PUBLISHED | gh belum tersedia; 33 body lokal dan publisher disiapkan |

JUnit dan output compile adalah artefak lokal di reports/ yang di-ignore; laporan
ringkas ini disimpan di Git. CI mengunggah JUnit pada masing-masing OS/Python.

Tes meliputi penolakan konfigurasi eksekusi/tipe salah/angka nonfinite, closed-bar
boundary dan OHLC invalid, diagnosa MT5 mock dengan masking dan shutdown, offline
doctor tanpa broker, perintah yang belum tersedia exit nonzero, static order API
checks, parity default Python/EA/preset, 33 issue unik, schema JSON valid, publisher
dry-run tanpa jaringan dan skip marker issue existing.

Pada run awal ada error temp sandbox pytest dan mock importlib yang terlalu luas.
Temp dipindah ke reports/pytest-tmp dan mock dibatasi pada modul adapter. Run ulang
54 tes PASS. Fixture/mock bukan data broker atau bukti integrasi MT5.

## Verifikasi manual yang masih dibutuhkan

- Compile source dan include pada MetaEditor, periksa log/artifact baru.
- Pasang EA di chart M15 demo dan verifikasi panel WAIT serta penolakan auto input.
- Setelah modul produk tersedia: history/suffix/freshness, parser bridge lintas
  bahasa, news/session DST, lot/margin/stop/freeze, recovery dan ownership.
- Demo forward dan backtest OOS dengan sumber data/biaya terdokumentasi.
- Jalankan dashboard setelah memasang extras dan periksa empty/error states.
