# Backlog implementasi

33 seed lokal. AU-003 juga terverifikasi di [GitHub #3](https://github.com/akbar875/TradingGold/issues/3). Status fondasi tidak berarti produk siap trading.

| ID | Issue | Prioritas | Area | Dependencies | Status |
|---|---|---|---|---|---|
| AU-001 | [Audit baseline v2 dan identifikasi bug kritis](issues/AU-001-audit-baseline-v2-dan-identifikasi-bug-kritis.md) | P0 | infra | - | DONE |
| AU-002 | [Scaffold repo, konfigurasi dan kontrak modul](issues/AU-002-scaffold-repo-konfigurasi-dan-kontrak-modul.md) | P0 | infra | AU-001 | DONE |
| AU-003 | [CI Python, formatting, lint, typing dan pytest](issues/AU-003-ci-python-formatting-lint-typing-dan-pytest.md) | P0 | infra | AU-002 | DONE |
| AU-004 | [Script compile EA MT5 di Windows dan pelaporan](issues/AU-004-script-compile-ea-mt5-di-windows-dan-pelaporan.md) | P0 | mql5 | AU-002 | IN_PROGRESS |
| AU-005 | [MT5 Python client dan diagnostik broker/simbol](issues/AU-005-mt5-python-client-dan-diagnostik-broker-simbol.md) | P0 | data | AU-002 | IN_PROGRESS |
| AU-006 | [Validasi data candle, spread, UTC dan closed-bar](issues/AU-006-validasi-data-candle-spread-utc-dan-closed-bar.md) | P0 | data | AU-005 | IN_PROGRESS |
| AU-007 | [Indikator teknikal MQL5 yang konsisten](issues/AU-007-indikator-teknikal-mql5-yang-konsisten.md) | P0 | mql5 | AU-002 | OPEN |
| AU-008 | [Market regime dan filter arah H1/H4](issues/AU-008-market-regime-dan-filter-arah-h1-h4.md) | P0 | mql5 | AU-007 | OPEN |
| AU-009 | [Setup entry breakout retest dan trend pullback](issues/AU-009-setup-entry-breakout-retest-dan-trend-pullback.md) | P0 | mql5 | AU-008 | OPEN |
| AU-010 | [Explainable signal scoring dan reason codes](issues/AU-010-explainable-signal-scoring-dan-reason-codes.md) | P0 | mql5 | AU-009 | OPEN |
| AU-011 | [Trading plan entry, stop loss dan take profit](issues/AU-011-trading-plan-entry-stop-loss-dan-take-profit.md) | P0 | risk | AU-010 | OPEN |
| AU-012 | [Position sizing dan margin gate 1:2000](issues/AU-012-position-sizing-dan-margin-gate-1-2000.md) | P0 | risk | AU-011 | OPEN |
| AU-013 | [Proteksi akun: drawdown, frekuensi, cooldown, kill switch](issues/AU-013-proteksi-akun-drawdown-frekuensi-cooldown-kill-switch.md) | P0 | risk | AU-012 | OPEN |
| AU-014 | [Order execution demo, retcode, idempotency](issues/AU-014-order-execution-demo-retcode-idempotency.md) | P0 | mql5 | AU-013 | OPEN |
| AU-015 | [Breakeven, trailing dan partial TP yang aman](issues/AU-015-breakeven-trailing-dan-partial-tp-yang-aman.md) | P0 | risk | AU-014 | OPEN |
| AU-016 | [Session, spread, rollover dan calendar news guard](issues/AU-016-session-spread-rollover-dan-calendar-news-guard.md) | P0 | risk | AU-008 | OPEN |
| AU-017 | [Feature engineering kausal Python](issues/AU-017-feature-engineering-kausal-python.md) | P0 | ml | AU-006 | OPEN |
| AU-018 | [Triple-barrier labels dan ambiguitas intrabar](issues/AU-018-triple-barrier-labels-dan-ambiguitas-intrabar.md) | P0 | ml | AU-017 | OPEN |
| AU-019 | [Purged walk-forward training, metrics dan baseline](issues/AU-019-purged-walk-forward-training-metrics-dan-baseline.md) | P0 | ml | AU-018 | OPEN |
| AU-020 | [Model registry, calibration dan quality gate](issues/AU-020-model-registry-calibration-dan-quality-gate.md) | P0 | ml | AU-019 | OPEN |
| AU-021 | [Atomic file bridge Python-MQL5 dengan schema ketat](issues/AU-021-atomic-file-bridge-python-mql5-dengan-schema-ketat.md) | P0 | infra | AU-020 | OPEN |
| AU-022 | [Integrasi AI gate, rules-only fallback dan panel chart MT5](issues/AU-022-integrasi-ai-gate-rules-only-fallback-dan-panel-chart-mt5.md) | P0 | mql5 | AU-010, AU-021 | OPEN |
| AU-023 | [Backtest Python cost-aware dan trade journal](issues/AU-023-backtest-python-cost-aware-dan-trade-journal.md) | P0 | backtest | AU-011, AU-019 | OPEN |
| AU-024 | [MQL5 tester-compatible OOS signal replay](issues/AU-024-mql5-tester-compatible-oos-signal-replay.md) | P1 | backtest | AU-021, AU-023 | OPEN |
| AU-025 | [Benchmark ablation, robustness dan Monte Carlo](issues/AU-025-benchmark-ablation-robustness-dan-monte-carlo.md) | P1 | backtest | AU-023 | OPEN |
| AU-026 | [Dashboard Streamlit monitoring read-only](issues/AU-026-dashboard-streamlit-monitoring-read-only.md) | P1 | dashboard | AU-022, AU-023 | IN_PROGRESS |
| AU-027 | [Audit logs, journal, telemetry dan alerts](issues/AU-027-audit-logs-journal-telemetry-dan-alerts.md) | P1 | infra | AU-022 | OPEN |
| AU-028 | [Comprehensive risk regression dan safety tests](issues/AU-028-comprehensive-risk-regression-dan-safety-tests.md) | P0 | risk | AU-014, AU-015, AU-021 | OPEN |
| AU-029 | [Panduan Windows MT5, broker suffix, FAQ dan preset](issues/AU-029-panduan-windows-mt5-broker-suffix-faq-dan-preset.md) | P1 | docs | AU-022 | OPEN |
| AU-030 | [Laporan pengujian dan checklist demo forward test](issues/AU-030-laporan-pengujian-dan-checklist-demo-forward-test.md) | P1 | docs | AU-028, AU-029 | OPEN |
| AU-031 | [Issue templates, backlog dan publisher idempotent](issues/AU-031-issue-templates-backlog-dan-publisher-idempotent.md) | P0 | infra | AU-002 | IN_PROGRESS |
| AU-032 | [Release candidate, versioning dan handoff](issues/AU-032-release-candidate-versioning-dan-handoff.md) | P1 | docs | AU-030, AU-031 | OPEN |
| AU-033 | [Skenario live safeguards dan manual review gate](issues/AU-033-skenario-live-safeguards-dan-manual-review-gate.md) | P1 | risk | AU-014 | OPEN |

AU-001: audit selesai, kompilasi baseline tidak mungkin karena source tidak disertakan.
AU-002: scaffold fase A dan kontrak konfigurasi lulus verifikasi offline.
AU-003: runner offline, coverage safety, dan keempat job CI lulus verifikasi.
AU-004/005/006/026/031 masih IN_PROGRESS.
Issue lokal lainnya OPEN.
