# PROMPT MASTER CODEX: AURUM EXPERT AI MT5 V3.0

> Instruksi untuk Codex. Baca seluruh dokumen sebelum bekerja. Laksanakan implementasi, pengetesan, dokumentasi, dan pembuatan issue. Jangan berhenti pada perencanaan atau menulis issue saja.

## 0. Peran dan hasil akhir

Bertindak sebagai tim lintas disiplin yang terdiri atas senior MQL5/MetaTrader 5 engineer, Python machine learning engineer, quantitative developer, software architect, QA automation engineer, dan DevOps engineer.

Bangun **Aurum Expert AI MT5 v3.0**, sistem pendamping keputusan dan Expert Advisor (EA) trading XAUUSD pada MetaTrader 5 desktop Windows. Fokus utama adalah **kapan BUY, SELL, WAIT, kapan entry, penentuan Stop Loss, Take Profit, ukuran lot, pengelolaan posisi, dan alasan keputusan**. Gunakan harga real-time dari terminal broker MT5 saat sistem terhubung. Mesin AI ML harus benar-benar dilatih, diuji, dan menghasilkan prediksi yang dapat diverifikasi, bukan respons acak atau label "AI" tanpa model.

Saya menggunakan akun MT5 dengan leverage **1:2000**, tetapi leverage adalah pengaturan **broker/akun**, bukan sesuatu yang bisa ditetapkan EA. Baca leverage aktual dari terminal, periksa risiko berdasarkan spesifikasi simbol akun, dan peringatkan/blokir order otomatis jika input `RequireLeverage2000=true` tetapi akun berbeda. Leverage tinggi tidak boleh dijadikan alasan menaikkan lot.

**Target:** repository siap dikembangkan, source code lengkap, dokumentasi Indonesia, unit/integration tests, backtest yang dapat direproduksi, CI, dashboard monitoring lokal, dan seluruh **GitHub/GitLab Issues** sebagai backlog. Tidak perlu membuat aplikasi broker sendiri atau mengklaim sistem pasti profit.

**Aturan pekerjaan:**

1. Audit repository dan lampiran yang tersedia terlebih dahulu. Jika ada `Aurum_Expert_AI_MT5_v2.zip`, `Aurum_Expert_AI_XAUUSD.mq5`, `aurum_ai.py`, `README_ID.md`, atau `test_offline.py`, gunakan sebagai **baseline** dan identifikasi bagian yang benar-benar harus direfaktor/diperbaiki. Jangan menganggap baseline sudah lolos kompilasi MT5.
2. Bila repository kosong, inisialisasi seluruh struktur proyek sendiri. Jangan meminta pengguna menjelaskan ulang spesifikasi yang sudah tertulis.
3. Kerjakan fase secara berurutan; implementasikan file nyata, bukan pseudocode, placeholder `TODO`, atau mock tanpa penjelasan. Boleh gunakan fixture sintetis **hanya untuk tes**, jangan menyamarkannya sebagai data broker atau hasil trading sesungguhnya.
4. Jalankan tes yang didukung lingkungan. Jika MetaEditor, terminal Windows, broker, atau akses remote tidak tersedia, **jangan mengklaim compile/backtest/live test berhasil**. Buat test runner, instruksi verifikasi, dan catat status `NOT RUN (environment unavailable)`.
5. Jangan mengirim order real tanpa pengguna sengaja mengaktifkan beberapa pengaman. Default `SignalOnly=true`, `AutoTrade=false`, `DemoOnly=true`. Python ML **tidak boleh** mengirim order. EA MQL5 menjadi satu-satunya pemilik eksekusi dan perubahan posisi.
6. Semua keputusan dan order punya audit trail serta reason code. Jika data invalid/stale, spread berlebihan, koneksi hilang, model rusak, atau risk gate gagal: **WAIT / NO NEW ENTRY**. Pengelolaan SL untuk posisi yang sudah terbuka tetap berjalan jika memungkinkan.
7. Gunakan prinsip **no look-ahead, fail closed, no data leakage, reproducible evaluation, idempotent execution**.
8. Buat dan kelola issue sesuai Bagian 10. Jika remote + autentikasi tersedia, publish issue sungguhan. Jika tidak, buat file issue lengkap yang bisa di-publish kemudian. Jangan menyatakan issue remote sudah dibuat jika belum.
9. Jangan mengklaim ada akurasi atau imbal hasil tertentu. Semua metrik harus berasal dari eksperimen dan mencantumkan periode data, sample, biaya, serta keterbatasannya.

## 1. Konteks produk dan cara pakai

- Instrumen utama: `XAUUSD`, dengan suffix broker didukung (`XAUUSDm`, `XAUUSD.a`, dll). Jangan hardcode ukuran contract, tick, digit, atau tick value.
- Terminal: MetaTrader 5 Desktop Windows. Dashboard lokal dan ML Python boleh berjalan terpisah pada komputer sama.
- Chart utama entry: M15. M5 untuk pengamatan entry opsional. H1/H4 untuk filter arah, rezim, dan support/resistance. Seluruh timeframe bisa dikonfigurasi; pengaturan default konsisten di ML, EA, backtest, dan dokumentasi.
- Bahasa antarmuka, log utama, dan README: Indonesia yang jelas dan singkat. Nama kode/API tetap mengikuti konvensi Inggris.
- Mode 1: **Signal Only**. Tampilkan rencana trading tanpa mengirim order.
- Mode 2: **Demo Auto**. Order hanya pada akun demo, setelah tombol/input auto diaktifkan dan semua risk gate lolos.
- Mode 3: **Live Enabled**. Fitur disediakan, tetapi default terblokir. Aktif hanya jika pengguna mengubah `DemoOnly=false`, `AutoTrade=true`, dan konfirmasi eksplisit tambahan di konfigurasi; tetap wajib lolos risk gates. Jangan pernah mengaktifkannya saat setup awal atau tes otomatis.

## 2. Arsitektur wajib

Komponen terpisah:

**A. EA MQL5:** membaca bar/tick broker, menghitung indikator dan kondisi pasar, membangun trading plan, menerapkan semua hard risk gates, mengeksekusi order hanya bila diizinkan, mengelola posisi milik EA saja, membaca konfirmasi ML, menampilkan panel chart, dan menyimpan log. Gunakan `CTrade`, `OrderCalcProfit`, `OrderCalcMargin`, properti simbol dan akun yang relevan. Hormati stop level, freeze level, fill mode, tick-size, dan volume step.

**B. Python AI service:** mengambil data historis/closed-bar lewat paket `MetaTrader5`, membuat fitur kausal, melatih model klasifikasi dasar `BUY/SELL/WAIT`, melakukan walk-forward time-series validation dengan purging/embargo agar label yang menggunakan horizon masa depan tidak bocor, menyimpan artifact/metadata, lalu membuat prediksi dari candle M15 **yang sudah tutup**. Python **tidak memanggil `order_send`**.

**C. Local bridge:** komunikasi Python -> EA melalui file atomic yang bisa diakses lewat `TerminalInfo` Common Files. Header/field berisi `schema_version`, `model_version`, `account_login`, `server`, `symbol`, `timeframe`, `bar_open_time_utc`, `generated_at_utc`, `expiry_utc`, `action`, `p_buy`, `p_sell`, `p_wait`, `quality_status`, dan checksum atau validasi integritas setara. Pilih CSV dengan parsing MQL5 yang stabil atau format lain jika ada parser yang diuji. EA menolak schema asing, nilai invalid, akun/simbol/timeframe salah, timestamp mismatch, berkas tidak lengkap, versi model tidak cocok, atau sinyal kedaluwarsa. Tulis secara atomik (temp + replace). Tidak perlu WebRequest untuk jalur inti.

**D. Offline research/backtest:** Python pipeline untuk backtest dan walk-forward yang memakai data historis berizin dari broker atau file CSV pengguna. Slippage, spread, komisi, swap, ketidakpastian urutan hit SL/TP intra-bar, dan jam trading dimodelkan konservatif. Pisahkan hasil rules-only dari hasil rules+ML. Jangan menyamakan metrik klasifikasi dengan profitabilitas trading.

**E. Local dashboard:** UI lokal **read-only** (pilih Streamlit untuk MVP) untuk menampilkan status MT5 + ML, sinyal terkini, alasan WAIT/BUY/SELL, Entry/SL/TP, Risk/Reward, biaya/spread, jumlah posisi, trade journal, equity curve dari backtest, statistik model, dan pengaturan yang sedang aktif. Dashboard tidak boleh menjadi jalur pengiriman order. Jangan meminta kredensial broker melalui dashboard.

**F. Automation/DevOps:** script linting/test/build, data fixtures, GitHub Actions atau CI kompatibel repo, issue templates + publishing script, reproducible setup, logging dan troubleshooting.

## 3. Mesin keputusan layaknya analisis trader disiplin

### 3.1 Alur sinyal

1. Validasi kesiapan terminal, akun, simbol, sesi, data candle, jumlah history, harga bid/ask, kualitas tick, spread dan trading permission.
2. Identifikasi `market_regime`: `TREND_UP`, `TREND_DOWN`, `RANGE`, atau `HIGH_VOLATILITY/UNSAFE`, berdasarkan indikator yang terdefinisi dan diuji; jangan memaksa BUY/SELL pada semua candle.
3. Analisis multi-timeframe: H4 dan H1 sebagai arah umum dan tingkat key level, M15 sebagai trigger entry. Tidak memakai candle yang masih terbentuk untuk konfirmasi setup.
4. Indikator: EMA20/50 M15, EMA50/200 H1, RSI14, MACD histogram, ADX14/+DI/-DI, ATR14, swing high/low, support/resistance, breakout/retest, dan pullback. Setiap indikator disertai rumus/rule yang eksplisit dan test cases.
5. Deteksi setup terpisah: `TREND_PULLBACK`, `BREAKOUT_RETEST`, `RANGE_REJECTION` (opsional jika valid secara backtest). Tetapkan syarat minimum dan invalidation; jangan membuat semua indikator saling menghitung hal yang sama sebagai bukti independen.
6. Analisis sesi trading London/New York dan rollover: konversi timezone broker secara benar; hindari hardcode GMT offset tanpa memperhitungkan DST. Tentukan kebijakan untuk market closed, jam illiquid, dan widening spread.
7. News risk: gunakan kalender ekonomi MT5 untuk event USD high-impact jika tersedia. Tetapkan jendela konfigurabel, misalnya 30 menit sebelum dan 15 menit sesudah. Jika kalender live tidak tersedia, beri status `NEWS_UNKNOWN` dan kebijakan fail-closed untuk auto order ketika news filter diwajibkan. Mode backtest menggunakan fixture kalender yang timestamp-nya terdokumentasi, bukan klaim live calendar tersedia di tester.
8. Buat skor konfirmasi **heuristik yang dapat dijelaskan**: 0 sampai 100 untuk kekuatan setup, namun **bukan probabilitas menang**. Sertakan komponen, bobot, alasan setuju/menolak dan threshold dari konfigurasi.
9. Minta konfirmasi model ML jika `RequireAI=true`. Gabungkan secara eksplisit: misalnya setup teknikal valid + ML searah + margin probabilitas dan quality gate valid. Probabilitas model tidak otomatis berarti probabilitas keuntungan kecuali dilakukan calibration dan evaluation yang mendukung.
10. Output final `BUY / SELL / WAIT` dengan alasan prioritas tertinggi dan status validasi. Pilih WAIT bila bukti lemah, ada konflik sinyal, harga terlalu jauh dari setup, atau aturan risiko gagal.

### 3.2 Format sinyal di chart dan bridge

Setiap sinyal memiliki:

- `signal_id` unik dan deterministik: akun+symbol+timeframe+closed_bar+setup+direction.
- Waktu candle yang digunakan, waktu keputusan, broker/server, harga bid/ask, spread, dan usia data.
- Keputusan `BUY/SELL/WAIT`, setup, market_regime, timeframe entry, alignment H1/H4, reasoning score.
- Harga entry yang bersifat **rencana**. Jika sudah terlalu jauh dari zona entry, ubah menjadi WAIT. Mendukung `MARKET` pada MVP dan `LIMIT` sebagai kemampuan terpisah bila benar-benar diuji.
- Stop Loss berdasarkan invalidation struktur + buffer ATR yang realistis. Hormati `SYMBOL_TRADE_STOPS_LEVEL`, tick size, spread dan stop distance broker. Jangan menggunakan SL/TP terlalu dekat atau pada sisi harga yang salah.
- TP1/TP2 atau single TP, target R yang dapat dikonfigurasi; `RR >= 1:2` hanya diterapkan bila key level/struktur mendukung, bukan dipaksakan saat target realistis lebih dekat. Jika reward tidak memadai, WAIT.
- Lot yang dihitung dari risiko ekuitas dan `OrderCalcProfit`, dengan volume step dan min/max broker, margin dari `OrderCalcMargin`, batas lot tambahan, serta biaya/spread bila tersedia. **Jangan memaksa minimal lot** jika melebihi risk budget.
- `estimated_risk_money`, `estimated_reward_money`, `RR`, asumsi komisi/slippage, dan alasan mengapa order bisa ditolak.
- Catatan harga entry berubah saat eksekusi. Revalidasi harga, posisi, lot, SL, TP, izin trading, dan margin **sebelum** `OrderSend`/CTrade Buy/Sell.

### 3.3 Position management

- Berikan SL/TP server-side saat order dikirim. Jangan bergantung pada proses Python untuk SL/TP.
- Break-even saat profit mencapai konfigurasi 1R dengan buffer untuk biaya transaksi.
- Trailing stop mulai 1.5R menggunakan ATR + swing, tidak pernah melonggarkan SL.
- Partial take-profit opsional dan default OFF sampai ada pengujian. Jika ON, validasi volume minimum, volume step, aturan netting vs hedging, dan anti-eksekusi ganda.
- Optional time-stop saat setup invalid atau posisi melewati batas hold. Jangan otomatis menutup hanya karena output ML berubah sesaat, tanpa rule teruji.
- Magic number + symbol + ticket filter untuk mencegah perubahan posisi manual/EA lain.
- Setelah restart, rekonstruksi state posisi dari terminal dan persistent state yang konsisten. Jangan menggandakan order pada candle yang sama.
- Log alasan modify SL/TP, hasil broker retcode, error handling, partial fills, requote, busy market, dan retry terbatas dengan backoff. Jangan retry secara buta jika order mungkin sudah diterima.

### 3.4 Hard risk gates (default)

| Pengaturan | Default aman | Perilaku |
|---|---|---|
| `AutoTrade` | `false` | Hanya rekomendasi |
| `DemoOnly` | `true` | Tolak live execution |
| `RequireLeverage2000` | `true` | Tolak auto-entry jika leverage aktual bukan 2000 |
| `RiskPercentPerTrade` | `0.25` | Target risiko harga SL terhadap ekuitas |
| `MaxLot` | `0.05` | Cap tambahan, bukan lot wajib |
| `MaxDailyLossPercent` | `2.0` | Blokir entry baru ketika batas tercapai |
| `MaxEntriesPerDay` | `3` | Hitung order entry valid per broker day |
| `MaxOpenPositionsPerSymbol` | `1` | Tidak menumpuk entry |
| `MaxMarginUseOfFreeMarginPercent` | `15` | Tolak margin berlebihan |
| `MaxConsecutiveLosses` | `3` | Cooldown berdasarkan riwayat deal terverifikasi |
| `BreakEvenAtR` | `1.0` | SL naik ke area BE setelah biaya |
| `TrailingStartR` | `1.5` | SL hanya mengencang |
| `MaxStopDistanceATR` | `3.0` | Tolak setup SL terlalu jauh |
| `RequireAI` | `false` | Rules-only bisa berjalan pada Signal Only; jika true model invalid -> WAIT |
| `RequireNewsFilter` | `true` untuk demo auto/live | News data unknown -> blokir entry baru |
| `EmergencyKillSwitch` | `false` | Jika true langsung blokir semua order baru, tidak menghapus SL server-side |

Rumus target risiko harga tidak sama dengan kerugian maksimal. Gap, slippage, komisi, swap, perubahan likuiditas, atau stop-out dapat menyebabkan kerugian lebih besar. Aturan harian harus mendefinisikan baseline waktu server yang persisten, termasuk restart, posisi floating, dan reset hari. Saat batas harian tercapai, **stop membuka posisi baru**, tetap kelola posisi yang ada. Tambahkan emergency status yang terlihat.

## 4. Machine learning yang valid secara metodologi

### 4.1 Data

- Gunakan `MetaTrader5` Python untuk history OHLCV tick_volume, spread, time UTC, dan informasi simbol; pastikan data yang sama simbol + broker/account sesuai saat prediksi live.
- Pisahkan candle terakhir yang masih berjalan: prediksi hanya `shift=1` atau data tertutup hasil verifikasi timestamp.
- Periksa duplicate timestamps, bar hilang, timezone UTC/broker, spread zero/invalid, market holiday, anomali tick dan data outlier. Metadata dataset wajib jelas (broker, simbol, timeframe, rentang).
- Fixtures sintetis boleh hanya untuk unit test; larang memakai fixture sebagai bukti akurasi dunia nyata.
- Simpan dataset di `data/` yang di-`.gitignore` kecuali sample kecil tanpa data sensitif.

### 4.2 Fitur dan label

- Causal features: return multi-lag, EMA gap/slope, RSI, MACD histogram, ATR relative, ADX atau proxy diberi label jujur, candle body/wick, breakout distance, spread/ATR, session encoding, tick volume relative, distance to key level. Tidak ada `shift(-n)` di fitur.
- Label: triple-barrier berbasis SL/TP/symmetric ATR plus horizon 8 M15 (konfigurabel). Simpan definisi label lengkap. Jika dalam satu candle high dan low sama-sama menembus barrier, pakai kebijakan konservatif (ambiguous -> no-trade / stop-first) sesuai backtest, jangan mengasumsikan profit-first.
- Hindari label dengan future 8-bar yang melintasi fold training/test. Gunakan **purged/embargoed chronological splitting**, bukan shuffle.
- Pertimbangkan class imbalance, model drift, threshold calibration (jika digunakan) dan stabilitas lintas regime.

### 4.3 Training dan evaluasi

- Baseline `RandomForestClassifier` dengan seed tetap. Model tambahan (misalnya gradient boosting) opsional, hanya dipakai jika hasil out-of-sample lebih baik dan tetap reproducible.
- Training/validation/test disusun kronologis. Gunakan walk-forward: latih pada masa lalu -> prediksi masa depan -> geser jendela. Larang tuning threshold pada final test.
- Laporan: confusion matrix, precision/recall per kelas, balanced accuracy, Brier/calibration bila mengklaim probability, jumlah sinyal, coverage, distribusi prediksi, dan out-of-sample cost-aware trade results.
- Bandingkan baseline rules-only, ML-only (diagnostik), combined rules+ML, dan baseline WAIT/no-trade. Jelaskan jika ML tidak memperbaiki hasil.
- Tetapkan **model quality gate**: jumlah data minimum, metrik holdout, drift, usia model, kualitas kelas, prediksi valid, model version, dan masa berlaku. Jika gagal, `ML_DEGRADED` -> WAIT ketika RequireAI aktif.
- Registrasi artifact model lokal `model.joblib`, `metadata.json`, `metrics.json`, `feature_schema.json`; hindari membuka `joblib` dari sumber tidak terpercaya.
- Retain model lama yang valid saat retrain gagal tetapi jangan memakainya jika expired/quality gate gagal.

## 5. Backtest, forward test, dan kualitas

- Gunakan data broker yang dapat dipakai secara legal dan menyebutkan sumber. Sediakan CLI `fetch_data`, `train`, `evaluate`, `export_signals`, `backtest`, `paper_run`.
- Backtest Python menghitung entry/exit secara kausal dari **harga yang tersedia saat itu** (no look-ahead), spread, komisi, slippage, swap jika tersedia, session filter, news windows, broker min stop, dan lot/margin. Gunakan fill konservatif pada bar ambigu.
- Sediakan export sinyal out-of-sample berstempel timestamp untuk MQL5 Strategy Tester agar AI mode dapat direproduksi tanpa jaringan/Python live. Jangan mengklaim `WebRequest` maupun live economic calendar akan berjalan di Strategy Tester.
- Hasil yang wajib: net P/L, profit factor, expectancy R/trade, win rate, avg win/loss, max drawdown, #trades, exposure, risk-of-ruin estimate (opsional), trade-by-trade log, equity curve, evaluasi per regime/session/bulan, sensitivity analysis dengan spread/slippage lebih berat.
- Tambahkan analisis Monte Carlo berupa bootstrap distribusi trade returns **dengan pernyataan keterbatasan**. Jangan menyebutnya jaminan risiko masa depan.
- Sediakan minimal satu perintah menjalankan semua tes offline tanpa login MT5.
- Tes integrasi Windows + compile EA (bila MetaEditor tersedia). Bila tidak, siapkan skrip PowerShell `scripts/compile_mql5.ps1` dan instruksi sehingga manusia dapat memverifikasi tanpa menebak.
- Sediakan `TEST_REPORT.md` yang mencantumkan setiap jenis tes `PASS / FAIL / NOT RUN`, perintah, tanggal, lingkungan, serta bukti.

## 6. Dashboard monitoring lokal

Buat `dashboard/app.py` dengan Streamlit, menggunakan log JSONL/CSV dan model metrics. Minimal:

1. Header status: terminal MT5 connected/disconnected, broker/server masked, simbol, timeframe, actual leverage, `SIGNAL ONLY / DEMO AUTO / LIVE ENABLED`.
2. Signal card: `BUY/SELL/WAIT`, setup, entry plan, SL, TP, RR, estimated lot, alasan teknikal dan ML, market regime, news risk, timestamp, masa berlaku.
3. Signal breakdown: alignment H1/H4, EMA, RSI, MACD, ADX, ATR, breakout/retest, spread, source bar.
4. Safety panel: limit daily loss, risk %, margin gate, ML freshness, news gate, last error, emergency status.
5. Backtest results: equity curve, drawdown, summary metrik, timeframe/periode/biaya. Data harus berasal dari hasil nyata yang disimpan, bukan dummy yang muncul seolah live.
6. Trade journal: daftar entry/exit, alasan, SL/TP, R result, biaya, broker retcode (jika ada).
7. Empty/error/loading states jika layanan mati atau data belum tersedia. UI tidak boleh mengatakan "Connected" bila belum berhasil diverifikasi.

Dashboard **read-only**. Tidak ada tombol yang langsung mengirim market order atau mengubah pengaman akun.

## 7. Struktur repository target

```text
Aurum-Expert-AI-MT5/
  .github/
    workflows/python-ci.yml
    ISSUE_TEMPLATE/bug_report.yml
    ISSUE_TEMPLATE/feature_request.yml
    ISSUE_TEMPLATE/config.yml
  .gitignore
  .env.example
  README.md
  AGENTS.md
  CHANGELOG.md
  LICENSE                 # gunakan hanya jika kebijakan repo mengizinkan
  pyproject.toml
  requirements.txt
  mt5/
    Experts/Aurum_Expert_AI_XAUUSD.mq5
    Include/Aurum/       # modules untuk risk, signal, broker, bridge, UI
    Presets/Signal_Only.set
    Presets/Demo_Conservative.set
    README_MT5_ID.md
  python/aurum/
    __init__.py
    config.py
    mt5_client.py
    data_quality.py
    features.py
    labels.py
    walk_forward.py
    train.py
    predict.py
    bridge.py
    model_registry.py
    backtest.py
    costs.py
    journal.py
    cli.py
  dashboard/app.py
  config/default.yaml
  config/signal.schema.json
  scripts/
    setup_windows.ps1
    compile_mql5.ps1
    run_ai.ps1
    test_offline.ps1
    publish_issues.py
  tests/
    fixtures/
    test_features.py
    test_labels.py
    test_walk_forward.py
    test_bridge.py
    test_risk.py
    test_backtest.py
    test_data_quality.py
    test_model_registry.py
  docs/
    ARCHITECTURE.md
    STRATEGY_RULES.md
    SIGNAL_SCHEMA.md
    RISK_MANAGEMENT.md
    ML_METHODOLOGY.md
    BACKTEST_GUIDE.md
    INSTALL_WINDOWS_MT5.md
    TROUBLESHOOTING.md
    TEST_REPORT.md
    ISSUES_BACKLOG.md
    issues/               # setiap issue 1 .md berisi body siap publish
  data/.gitkeep
  logs/.gitkeep
  models/.gitkeep
```

Struktur boleh disesuaikan bila ada alasan teknis yang dicatat di `ARCHITECTURE.md`. Jangan menghapus baseline tanpa mencatat migrasi. Pakai modul kecil, fungsi teruji, tipe eksplisit, dan config terpusat. Jangan meng-commit password, token broker, data akun sensitif, model berbahaya, dan data trading privat. Tambahkan `.gitignore` untuk `.env`, data mentah, `logs/`, `models/`, caches, dan output test.

## 8. Rencana implementasi yang harus dikerjakan Codex

**Fase A, Audit dan fondasi:** periksa baseline, audit risk bugs dan informasi yang belum diuji, buat `docs/ARCHITECTURE.md`, skeleton repo, config schema, test offline, issue backlog. Commit pekerjaan hanya jika repo mengizinkan.

**Fase B, MQL5 rules dan risk:** implementasi market context, decision engine dan reason code, trade plan SL/TP, lot/margin risk, exit controls, chart panel, idempotency, error handling.

**Fase C, Python ML:** data client, features kausal, labeling, walk-forward, model registry, CLI, quality gates, atomic bridge.

**Fase D, Integrasi dan dashboard:** EA membaca bridge dan memvalidasi sinyal, panel/chart, log/journal, dashboard monitoring read-only.

**Fase E, Backtest dan QA:** offline and MQL tests, data fixtures, backtest cost-aware, baseline comparisons, walk-forward, sensitivity, security checks, documentation, release candidate.

**Fase F, Issue management dan handoff:** publish GitHub/GitLab issues bila bisa, update status setiap issue, tutup hanya issue yang benar-benar memenuhi definition of done. Berikan ringkasan hasil dan blocker berikut.

Setelah tiap fase: jalankan tes yang tersedia, rapikan error, catat artefak yang berubah. **Jangan berhenti setelah menulis rencana**. Jika anggaran eksekusi terbatas, prioritaskan P0 berjalan dan dites, baru P1, P2. Tinggalkan status faktual, bukan klaim selesai.

## 9. Definition of Done dan aturan verifikasi

Sebuah komponen dianggap selesai hanya jika: (a) source nyata tersedia, (b) antarmuka dan validasi didefinisikan, (c) error/fail-closed path diuji, (d) test berhasil jika lingkungan mendukung, (e) dokumentasi diperbarui, dan (f) lint/test report disertakan. Jangan menandai issue selesai untuk kode placeholder.

Kriteria keseluruhan rilis:

- EA menggunakan data dari broker dan menampilkan BUY/SELL/WAIT beserta alasan, Entry/SL/TP, lot, RR, dan status gate.
- Default tidak mengirim order. Jika mode demo dipilih, setiap entry mematuhi limit lot/risiko/margin/jumlah transaksi dan tidak menggandakan trade setelah restart.
- SL/TP dipasang di server untuk trade yang dieksekusi dan manajemen trailing tidak pernah memperlebar risiko awal secara diam-diam.
- Python hanya memprediksi dari candle tertutup, tidak mengirim order dan menolak prediksi/model stale.
- Setidaknya satu pipeline pengujian walk-forward berhasil dengan fixture offline, dan pelaporan jelas membedakan hasil fixture dari hasil broker.
- Backtest menggunakan biaya yang didokumentasikan dan file per-trade untuk audit.
- Dashboard berjalan dalam mode offline dan menunjukkan empty states. Jika koneksi broker tersedia, gunakan data yang terverifikasi.
- `pytest` lulus dan laporan test disimpan. Compile EA diverifikasi secara nyata di MetaEditor jika ada. Jika tidak ada, status wajib NOT RUN.
- Semua issue terdata dengan ID, status, prioritas, dependencies, test, acceptance criteria, dan tautan commit/PR bila tersedia.

## 10. Pembuatan GitHub/GitLab Issues WAJIB

**Tidak cukup sekadar daftar issue di chat.** Buat file `docs/ISSUES_BACKLOG.md` dan satu file Markdown per issue di `docs/issues/`, misalnya `AU-001-audit-baseline.md`, menggunakan daftar pada **Lampiran A**. Buat issue template untuk bug dan fitur. Untuk setiap issue body, isi:

- Judul presisi dengan awalan `[AU-XXX]`.
- Epic, severity/priority (`P0`, `P1`, `P2`), label teknis, status (`open`, `in_progress`, `blocked`, `done`).
- Latar belakang masalah dan mengapa perlu.
- Scope implementasi: file/modul yang terpengaruh, flow, dependensi issue lain.
- Tasks checklist yang bisa ditindaklanjuti.
- Acceptance criteria sebagai checklist terukur.
- Perintah/skenario test termasuk negative cases.
- Deliverable, definition of done, dan link PR/commit jika ada.

**Publish ke issue tracker jika tersedia:**

1. Jalankan `git remote -v`, deteksi GitHub (`gh`) atau GitLab (`glab`) dari remote; jangan menebak provider.
2. Periksa CLI dan autentikasi, serta izin membuat issue. Buat label `priority:P0`, `priority:P1`, `priority:P2`, `area:mql5`, `area:ml`, `area:risk`, `area:data`, `area:backtest`, `area:dashboard`, `area:infra`, `area:docs`, `type:bug`, `type:feature`, `status:blocked` bila memungkinkan.
3. Publish epic/milestone secara kompatibel provider bila tersedia, lalu publish issue dengan body file. Cari issue existing berdasarkan marker `[AU-XXX]` agar **idempotent**: jangan membuat duplikat. Bila issue sudah ada, update hanya apabila aman dan jelas milik proyek ini.
4. Buat `scripts/publish_issues.py` atau skrip yang setara dengan `--dry-run`, `--provider github|gitlab|auto`, `--label`, dan output hasil, dengan error handling dan idempotency. Perintah tidak boleh menampilkan token autentikasi.
5. Bila repo belum punya remote/CLI/auth atau izin, **jangan gagal total**: semua issue file tetap tersedia dan bisa dipublish belakangan. Catat `NOT PUBLISHED`, blocker konkret, dan contoh perintah eksekusi. Jangan mengklaim issue remote sudah aktif.
6. Issue implementation yang betul-betul selesai diberi `done` di backlog lokal dan ditutup remote jika tes + acceptance lengkap dan metadata izin tersedia. Issue belum beres tetap open.
7. Jangan membuat issue generik seperti "implement AI" tanpa subtasks dan acceptance. Jadikan Lampiran A sebagai seed minimum, pecah lagi jika diperlukan.

## 11. Perintah yang harus disediakan pada README

Contoh UX CLI yang diharapkan (sesuaikan nama paket jika perlu):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m aurum.cli doctor --symbol XAUUSD
python -m aurum.cli fetch-data --symbol XAUUSD --timeframe M15 --bars 10000
python -m aurum.cli train --config config/default.yaml
python -m aurum.cli evaluate --config config/default.yaml
python -m aurum.cli predict --symbol XAUUSD --once
python -m aurum.cli run --symbol XAUUSD
python -m aurum.cli backtest --config config/default.yaml
python -m aurum.cli export-signals --config config/default.yaml
pytest -q
streamlit run dashboard/app.py
python scripts/publish_issues.py --dry-run --provider auto
```

Perintah `doctor` wajib memverifikasi Python environment, paket, terminal MT5, akun login, simbol dan suffix, leverage aktual, trading permissions, spread info, folder Common/Files, kelengkapan history, dan data/AI freshness. Cetak informasi akun sensitif dalam bentuk masked.

## 12. Dokumentasi resmi yang sebaiknya dibaca dan diperiksa

- Python integration: https://www.mql5.com/en/docs/python_metatrader5
- Python market data: https://www.mql5.com/en/docs/python_metatrader5/mt5copyratesfrompos_py
- OrderCalcProfit: https://www.mql5.com/en/docs/trading/ordercalcprofit
- OrderCalcMargin: https://www.mql5.com/en/docs/trading/ordercalcmargin
- Economic calendar: https://www.mql5.com/en/docs/calendar
- MQL5 WebRequest tester limitation: https://www.mql5.com/en/docs/network/webrequest
- Strategy tester limitations: https://www.mql5.com/en/docs/runtime/testing

Verifikasi API dalam dokumentasi resmi sebelum coding jika ada keraguan. Jangan mengandalkan implementasi MT4 untuk MT5.

## 13. Format jawaban terakhir Codex

Pada akhir implementasi, kirim laporan berisi:

1. Yang sudah diimplementasikan (file dan modul nyata).
2. Struktur repo final, perintah instalasi/jalankan, contoh status `SIGNAL ONLY`.
3. Status tes per jenis: PASS, FAIL, NOT RUN, output ringkas dan lokasi report.
4. Status compile MetaEditor yang faktual, status backtest real broker yang faktual. Jangan mengarang.
5. Ringkasan issue: total dibuat lokal, total dipublish remote, open/done/blocked, issue P0 tersisa.
6. Daftar keterbatasan, asumsi, dan apa yang harus diuji manual pada MT5 Windows akun demo.
7. Jika ada blocker, jelaskan dampak dan solusi teknis, lalu tetap selesaikan bagian lain yang bisa dikerjakan.

**Mulai bekerja sekarang. Audit baseline, buat semua issue, implementasikan sistem, jalankan tes, perbaiki kegagalan, dan siapkan rilis yang terverifikasi.**

---

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
