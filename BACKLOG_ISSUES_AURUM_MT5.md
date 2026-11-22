# Lampiran A: Seed Issue Resmi Aurum Expert AI MT5 v3.0

Dokumen ini adalah daftar minimal issue yang **wajib** dibuat oleh Codex. Setiap baris harus dikembangkan menjadi file `docs/issues/AU-XXX-*.md` dengan checklist tasks, acceptance criteria, test scenarios, dan links. P0 tidak boleh ditandai selesai tanpa tes dan bukti yang relevan.

| ID | Issue | Priority | Area | Dependencies |
|---|---|---|---|---|
| AU-001 | Audit baseline v2 dan identifikasi bug kritis | P0 | infra | - |
| AU-002 | Scaffold repo, konfigurasi dan kontrak modul | P0 | infra | AU-001 |
| AU-003 | CI Python, formatting, lint, typing dan pytest | P0 | infra | AU-002 |
| AU-004 | Script compile EA MT5 di Windows dan pelaporan | P0 | mql5 | AU-002 |
| AU-005 | MT5 Python client dan diagnostik broker/simbol | P0 | data | AU-002 |
| AU-006 | Validasi data candle, spread, UTC dan closed-bar | P0 | data | AU-005 |
| AU-007 | Indikator teknikal MQL5 yang konsisten | P0 | mql5 | AU-002 |
| AU-008 | Market regime dan filter arah H1/H4 | P0 | mql5 | AU-007 |
| AU-009 | Setup entry breakout retest dan trend pullback | P0 | mql5 | AU-008 |
| AU-010 | Explainable signal scoring dan reason codes | P0 | mql5 | AU-009 |
| AU-011 | Trading plan entry, stop loss dan take profit | P0 | risk | AU-010 |
| AU-012 | Position sizing dan margin gate 1:2000 | P0 | risk | AU-011 |
| AU-013 | Proteksi akun: drawdown, frekuensi, cooldown, kill switch | P0 | risk | AU-012 |
| AU-014 | Order execution demo, retcode, idempotency | P0 | mql5 | AU-013 |
| AU-015 | Breakeven, trailing dan partial TP yang aman | P0 | risk | AU-014 |
| AU-016 | Session, spread, rollover dan calendar news guard | P0 | risk | AU-008 |
| AU-017 | Feature engineering kausal Python | P0 | ml | AU-006 |
| AU-018 | Triple-barrier labels dan ambiguitas intrabar | P0 | ml | AU-017 |
| AU-019 | Purged walk-forward training, metrics dan baseline | P0 | ml | AU-018 |
| AU-020 | Model registry, calibration dan quality gate | P0 | ml | AU-019 |
| AU-021 | Atomic file bridge Python-MQL5 dengan schema ketat | P0 | infra | AU-020 |
| AU-022 | Integrasi AI gate, rules-only fallback dan panel chart MT5 | P0 | mql5 | AU-010, AU-021 |
| AU-023 | Backtest Python cost-aware dan trade journal | P0 | backtest | AU-011, AU-019 |
| AU-024 | MQL5 tester-compatible OOS signal replay | P1 | backtest | AU-021, AU-023 |
| AU-025 | Benchmark ablation, robustness dan Monte Carlo | P1 | backtest | AU-023 |
| AU-026 | Dashboard Streamlit monitoring read-only | P1 | dashboard | AU-022, AU-023 |
| AU-027 | Audit logs, journal, telemetry dan alerts | P1 | infra | AU-022 |
| AU-028 | Comprehensive risk regression dan safety tests | P0 | risk | AU-014, AU-015, AU-021 |
| AU-029 | Panduan Windows MT5, broker suffix, FAQ dan preset | P1 | docs | AU-022 |
| AU-030 | Laporan pengujian dan checklist demo forward test | P1 | docs | AU-028, AU-029 |
| AU-031 | Issue templates, backlog dan publisher idempotent | P0 | infra | AU-002 |
| AU-032 | Release candidate, versioning dan handoff | P1 | docs | AU-030, AU-031 |
| AU-033 | Skenario live safeguards dan manual review gate | P1 | risk | AU-014 |

## Issue Seed Detail

### [AU-001] Audit baseline v2 dan identifikasi bug kritis

- **Priority:** P0
- **Area:** infra
- **Dependencies:** -
- **Latar belakang:** Tidak mengulang asumsi bahwa file EA v2 sudah berhasil dikompilasi.
- **Scope implementasi:** Inventaris file, pemeriksaan kompilasi, code review, bug/risk register, migrasi baseline.
- **Acceptance criteria minimum:** Audit report, daftar masalah dengan severity, rencana migrasi dan tes awal.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-002] Scaffold repo, konfigurasi dan kontrak modul

- **Priority:** P0
- **Area:** infra
- **Dependencies:** AU-001
- **Latar belakang:** Repositori modular dengan konfigurasi tunggal dan dokumentasi dasar.
- **Scope implementasi:** Struktur paket Python, module MQL5, .gitignore, .env.example, AGENTS.md, pyproject dan default.yaml.
- **Acceptance criteria minimum:** Instal editable Python berhasil offline, import modul valid, tidak ada secret committed.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-003] CI Python, formatting, lint, typing dan pytest

- **Priority:** P0
- **Area:** infra
- **Dependencies:** AU-002
- **Latar belakang:** Semua perubahan penting bisa diuji otomatis.
- **Scope implementasi:** Workflow CI, scripts test, pytest, ruff, optional mypy, coverage minimum pada modul safety.
- **Acceptance criteria minimum:** Workflow valid dan pytest fixture offline PASS; laporan dapat diakses.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-004] Script compile EA MT5 di Windows dan pelaporan

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-002
- **Latar belakang:** Kompilasi MQL5 harus dapat diverifikasi, bukan klaim.
- **Scope implementasi:** PowerShell compile via MetaEditor CLI jika terpasang; tangkap exit code/log dan error.
- **Acceptance criteria minimum:** Compile PASS ketika lingkungan mendukung, jika tidak NOT RUN tercatat.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-005] MT5 Python client dan diagnostik broker/simbol

- **Priority:** P0
- **Area:** data
- **Dependencies:** AU-002
- **Latar belakang:** Semua input market berasal dari simbol broker tepat.
- **Scope implementasi:** Doctor, koneksi, symbol_select, tick/point/contract/volume/margin, M15,H1,H4, masking akun.
- **Acceptance criteria minimum:** Missing MT5/broker menghasilkan error jelas, data tidak dipalsukan.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-006] Validasi data candle, spread, UTC dan closed-bar

- **Priority:** P0
- **Area:** data
- **Dependencies:** AU-005
- **Latar belakang:** Mencegah analisis dari candle tidak lengkap atau historis kotor.
- **Scope implementasi:** Audit OHLCV, monotonic timestamps, gap, duplicate, timezone, spread points conversion.
- **Acceptance criteria minimum:** Tes gap/duplicate/malformed/stale dan bar 0 tidak dipakai pada sinyal final.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-007] Indikator teknikal MQL5 yang konsisten

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-002
- **Latar belakang:** Nilai indikator dapat diulang dan ditelusuri.
- **Scope implementasi:** EMA, RSI, MACD, ADX/+DI/-DI, ATR, copybuffer shift=1, handle lifecycle.
- **Acceptance criteria minimum:** Tes manual/banding fixture, tidak memakai future candle, onDeinit cleanup.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-008] Market regime dan filter arah H1/H4

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-007
- **Latar belakang:** EA mengenali kondisi trend, range dan volatilitas tinggi.
- **Scope implementasi:** H1 EMA50/200, H4 trend, ADX/ATR, dan state transition.
- **Acceptance criteria minimum:** Regime test cases bullish/bearish/range/unsafe; data invalid => WAIT.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-009] Setup entry breakout retest dan trend pullback

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-008
- **Latar belakang:** Entry hanya ketika trigger lengkap.
- **Scope implementasi:** Pisah fungsi setup, candle closed confirmation, swing, key level, invalidation, chase limit.
- **Acceptance criteria minimum:** Tes BUY/SELL/WAIT dan tidak terjadi duplikasi sinyal pada candle sama.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-010] Explainable signal scoring dan reason codes

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-009
- **Latar belakang:** Sinyal dapat diaudit oleh pengguna.
- **Scope implementasi:** Skor komponen heuristik, conflict gate, hasil WAIT beralasan, ID deterministik.
- **Acceptance criteria minimum:** Setiap sinyal punya reason code; skor tidak dilabeli probability.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-011] Trading plan entry, stop loss dan take profit

- **Priority:** P0
- **Area:** risk
- **Dependencies:** AU-010
- **Latar belakang:** Rencana trade valid menurut broker dan struktur pasar.
- **Scope implementasi:** Entry zona, ATR/swing SL, tick rounding, stop level, RR check, TP1/TP2 optional.
- **Acceptance criteria minimum:** SL selalu di sisi harga yang benar, invalid RR/distance => WAIT.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-012] Position sizing dan margin gate 1:2000

- **Priority:** P0
- **Area:** risk
- **Dependencies:** AU-011
- **Latar belakang:** Lot mengikuti risiko harga, bukan leverage maksimum.
- **Scope implementasi:** OrderCalcProfit/OrderCalcMargin, volume min/step/max, cap, actual leverage, worst-case.
- **Acceptance criteria minimum:** Min lot over risk => reject; leverage mismatch => auto entry reject.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-013] Proteksi akun: drawdown, frekuensi, cooldown, kill switch

- **Priority:** P0
- **Area:** risk
- **Dependencies:** AU-012
- **Latar belakang:** Kerugian dan frekuensi order dibatasi.
- **Scope implementasi:** Daily equity baseline persisted, max entries/day, max position, loss streak, emergency gate.
- **Acceptance criteria minimum:** Restart aman, hit limit => NO NEW ENTRY, existing SL tetap aktif.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-014] Order execution demo, retcode, idempotency

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-013
- **Latar belakang:** Tidak ada double execution atau order tanpa SL.
- **Scope implementasi:** CTrade, slippage/deviation, filling modes, retry safe, OnTradeTransaction, unique signal ID.
- **Acceptance criteria minimum:** Auto OFF default; DEMO only default; no duplicate entry; logs retcodes.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-015] Breakeven, trailing dan partial TP yang aman

- **Priority:** P0
- **Area:** risk
- **Dependencies:** AU-014
- **Latar belakang:** Posisi terbuka dikelola tanpa memperbesar stop risk.
- **Scope implementasi:** Break-even after 1R, ATR trailing at 1.5R, ownership filter, partial TP guarded.
- **Acceptance criteria minimum:** SL tidak pernah mundur, same position tidak dipartial berkali-kali, freeze aware.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-016] Session, spread, rollover dan calendar news guard

- **Priority:** P0
- **Area:** risk
- **Dependencies:** AU-008
- **Latar belakang:** Sistem tidak membuka posisi pada kondisi pasar tidak aman.
- **Scope implementasi:** Session conversion DST-safe, spread/ATR guard, MT5 high-impact USD events, fallback news unknown.
- **Acceptance criteria minimum:** News unavailable with required gate => WAIT; tester fixture used and documented.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-017] Feature engineering kausal Python

- **Priority:** P0
- **Area:** ml
- **Dependencies:** AU-006
- **Latar belakang:** Fitur machine learning bebas look-ahead.
- **Scope implementasi:** Features M15, H1/H4 alignment past-only, spread/ATR, nan policies, schema version.
- **Acceptance criteria minimum:** Tests memastikan perubahan future candles tidak mengubah fitur masa lalu.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-018] Triple-barrier labels dan ambiguitas intrabar

- **Priority:** P0
- **Area:** ml
- **Dependencies:** AU-017
- **Latar belakang:** Label trading disusun tanpa bias keuntungan berlebihan.
- **Scope implementasi:** 8-bar horizon, ATR barriers, ambiguous touches policy, masking unlabeled ending rows.
- **Acceptance criteria minimum:** Tests target masa depan tidak bocor dan ambiguous bar konservatif.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-019] Purged walk-forward training, metrics dan baseline

- **Priority:** P0
- **Area:** ml
- **Dependencies:** AU-018
- **Latar belakang:** Akurasi AI diuji pada data out-of-sample.
- **Scope implementasi:** RF baseline, chronological splits, purge/embargo, hyperparameter discipline, classification metrics.
- **Acceptance criteria minimum:** Deterministic seeds; no overlap label fold; holdout metrics and evidence.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-020] Model registry, calibration dan quality gate

- **Priority:** P0
- **Area:** ml
- **Dependencies:** AU-019
- **Latar belakang:** Model tidak aktif bila kedaluwarsa atau kualitas buruk.
- **Scope implementasi:** Versioned artifact, schema, metrics, expiry, drift, retrain, no untrusted joblib.
- **Acceptance criteria minimum:** Invalid/missing model => WAIT when RequireAI; no fake confidence.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-021] Atomic file bridge Python-MQL5 dengan schema ketat

- **Priority:** P0
- **Area:** infra
- **Dependencies:** AU-020
- **Latar belakang:** EA membaca sinyal AI yang cocok akun/simbol/candle.
- **Scope implementasi:** Fields schema, temp file replace, TTL, checksum/length, parse MQL5, fail closed.
- **Acceptance criteria minimum:** Test stale/account mismatch/partial/corrupt/unknown version => reject.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-022] Integrasi AI gate, rules-only fallback dan panel chart MT5

- **Priority:** P0
- **Area:** mql5
- **Dependencies:** AU-010, AU-021
- **Latar belakang:** User melihat keputusan final dan semua alasan.
- **Scope implementasi:** Combine rules+ML, timeframe checks, final WAIT logic, MT5 chart panel text/state.
- **Acceptance criteria minimum:** Valid signal only when gates pass; ML required + stale => WAIT.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-023] Backtest Python cost-aware dan trade journal

- **Priority:** P0
- **Area:** backtest
- **Dependencies:** AU-011, AU-019
- **Latar belakang:** Evaluasi strategi menghasilkan daftar trade dapat diaudit.
- **Scope implementasi:** Causal executor, spread/slippage/commission/swap, SL-first ambiguity, margin, broker rules.
- **Acceptance criteria minimum:** Trade log, P/L, DD, PF, R expectancy, no data leakage, fixtures tests.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-024] MQL5 tester-compatible OOS signal replay

- **Priority:** P1
- **Area:** backtest
- **Dependencies:** AU-021, AU-023
- **Latar belakang:** Tester dapat mereproduksi prediksi OOS tanpa Python live.
- **Scope implementasi:** Export CSV with timestamp and model version, tester reading and log parity.
- **Acceptance criteria minimum:** Replay deterministic, no WebRequest/tester calendar dependency.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-025] Benchmark ablation, robustness dan Monte Carlo

- **Priority:** P1
- **Area:** backtest
- **Dependencies:** AU-023
- **Latar belakang:** Mengetahui apakah ML benar-benar menambah nilai.
- **Scope implementasi:** Rules-only vs ML-only vs combined, stress spread, rolling performance, bootstrap trades.
- **Acceptance criteria minimum:** Metrik OOS terpisah, tabel per regime/session, limitations explicit.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-026] Dashboard Streamlit monitoring read-only

- **Priority:** P1
- **Area:** dashboard
- **Dependencies:** AU-022, AU-023
- **Latar belakang:** Pengguna dapat membaca sinyal/risk/status dengan jelas.
- **Scope implementasi:** Signal card, reasons, safety status, test metrics, trade log, equity/DD charts.
- **Acceptance criteria minimum:** Offline empty states, no order submission, no fake live price.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-027] Audit logs, journal, telemetry dan alerts

- **Priority:** P1
- **Area:** infra
- **Dependencies:** AU-022
- **Latar belakang:** Setiap keputusan bisa ditelusuri.
- **Scope implementasi:** Structured JSONL/CSV, safe account mask, no secret, alert throttling, path rotation.
- **Acceptance criteria minimum:** Entry, WAIT, reject, SL modify, model stale logged with IDs.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-028] Comprehensive risk regression dan safety tests

- **Priority:** P0
- **Area:** risk
- **Dependencies:** AU-014, AU-015, AU-021
- **Latar belakang:** Bug yang merugikan dicegah oleh test.
- **Scope implementasi:** Test suite min lot, no margin, bad spread, stale AI, daily loss, restart, netting, stop freeze.
- **Acceptance criteria minimum:** Semua negative cases fail closed dan tidak memanggil order saat auto OFF.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-029] Panduan Windows MT5, broker suffix, FAQ dan preset

- **Priority:** P1
- **Area:** docs
- **Dependencies:** AU-022
- **Latar belakang:** User bisa install dengan instruksi dari nol.
- **Scope implementasi:** README ID, setup PowerShell, MQL5 .set presets, MT5 permissions, demo runbook.
- **Acceptance criteria minimum:** Instruksi executable, troubleshooting, mode signal-only default.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-030] Laporan pengujian dan checklist demo forward test

- **Priority:** P1
- **Area:** docs
- **Dependencies:** AU-028, AU-029
- **Latar belakang:** Klaim selesai dibedakan dari tes nyata.
- **Scope implementasi:** TEST_REPORT PASS/FAIL/NOT RUN, checker, checklist demo forward, logs report.
- **Acceptance criteria minimum:** Tidak ada klaim broker test tanpa bukti; reproduction commands.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-031] Issue templates, backlog dan publisher idempotent

- **Priority:** P0
- **Area:** infra
- **Dependencies:** AU-002
- **Latar belakang:** Seluruh pekerjaan terdokumentasi sebagai issue yang siap publish.
- **Scope implementasi:** docs/issues/*.md, templates gh, CLI gh/glab auto-detect, dry-run, dedupe by AU ID.
- **Acceptance criteria minimum:** Semua 33 issue lokal ada, remote publish ketika auth tersedia; recap factual.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-032] Release candidate, versioning dan handoff

- **Priority:** P1
- **Area:** docs
- **Dependencies:** AU-030, AU-031
- **Latar belakang:** Paket siap diteruskan ke pengujian pengguna.
- **Scope implementasi:** changelog, release notes, threat/risks, install archive, checklist gates.
- **Acceptance criteria minimum:** All P0 complete or explicitly blocked; artefacts reproducible; no profit claims.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

### [AU-033] Skenario live safeguards dan manual review gate

- **Priority:** P1
- **Area:** risk
- **Dependencies:** AU-014
- **Latar belakang:** Akun real tidak aktif tanpa tindakan eksplisit.
- **Scope implementasi:** Live confirmation config, demo-only policy, prominent UI warning, stop-entry switch test.
- **Acceptance criteria minimum:** Live remains OFF by default; no automated test sends real order.
- **Checklist wajib:** implementasi source, negative-case tests, update docs, regression tests, laporan status, referensi commit/PR.

## Aturan status

- `OPEN`: belum dikerjakan.
- `IN_PROGRESS`: implementasi sedang berlangsung.
- `BLOCKED`: tergantung akses/terminal/data dan blocker ditulis dengan tepat.
- `DONE`: semua acceptance criteria dan tes yang relevan sudah diverifikasi.

## Pengelompokan milestone yang disarankan

- M1 Foundation & Safety: AU-001..AU-006, AU-012..AU-014, AU-031.
- M2 Decision & Trade Management: AU-007..AU-011, AU-015..AU-016, AU-022.
- M3 ML & Bridge: AU-017..AU-021.
- M4 Verification, Dashboard & Release: AU-023..AU-030, AU-032..AU-033.

Jangan menutup issue hanya karena sebagian implementasi tercakup dalam issue lain.
