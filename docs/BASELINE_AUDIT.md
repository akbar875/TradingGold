# Audit baseline — 22 November 2026

Seluruh enam berkas awal diinspeksi sebagai teks/source. Tidak ada Git metadata
lokal saat mulai; remote tujuan dapat diakses tetapi tidak memiliki refs.
Git lokal diinisialisasi pada main dan origin diarahkan ke repo pengguna.

| Berkas | Temuan dan keputusan |
|---|---|
| PRD_AURUM_EXPERT_AI_MT5_V3.md | Target produk dan 33 issue; belum merupakan bukti implementasi. Menjadi sumber kebutuhan utama. |
| PROMPT_CODEX_AURUM_EXPERT_AI_MT5_V3.md | Alur fase A-F, struktur repo, default aman, persyaratan QA dan publikasi issue. Scope sekarang fase A. |
| BACKLOG_ISSUES_AURUM_MT5.md | 33 seed beserta dependency dan AC; dikembangkan ke docs/issues. |
| README_ID.md | Panduan v2 mengasumsikan EA, requirements dan test_offline yang tidak ada pada baseline. Tetap disimpan sebagai referensi historis. |
| aurum_ai.py | Random Forest nyata, fitur historis kausal, label barrier 8 bar, purge pada satu split 80/20, drop current bar, atomic replace. Tidak memanggil API order. Perlu migrasi, tidak dianggap ML v3. |
| xauusd-trading-demo.html | Paper trading browser: Math.random, localStorage, leverage/contract/spread tetap dan tombol BUY/SELL simulasi. Tidak terhubung broker. Bukan dashboard read-only target. |

## Risk register dan rencana migrasi

| Severity | Temuan | Tindak lanjut |
|---|---|---|
| P0 | EA v2, ZIP dan test_offline.py tidak disertakan; kompilasi tidak dapat diasumsikan | EA diagnostik baru; implementasi engine dan compile AU-004/007..016 |
| P0 | CSV v2 hanya account/symbol/bar/action/p_buy/p_sell; tanpa schema, server, generated/expiry, p_wait, quality dan checksum | Kontrak v1 dan parser/writer baru AU-021; jangan menghubungkan CSV v2 ke v3 |
| P0 | Cache joblib v2 tidak memvalidasi metadata broker/server/feature hash/quality secara lengkap; deserialisasi membutuhkan trust | Registry/quality gate AU-020; jangan memuat model dari pihak asing |
| P0 | Pengambilan v2 membuang bar terakhir tetapi tidak memvalidasi freshness, duplicate/gap/OHLC atau perubahan akun di loop | Read shift=1 + validasi UTC/history/source AU-005/006 |
| P1 | Fitur spread mempunyai fallback `spread * 0.01`; main runtime memasok spread_price tetapi pemanggil lain bisa memakai asumsi point tetap | Wajib broker point/price spread eksplisit di AU-017 |
| P1 | RSI mengganti rasio undefined menjadi 50, termasuk zero-loss uptrend; fitur perlu uji edge case | Rumus yang jelas dan parity test AU-017 |
| P1 | Evaluasi v2 satu holdout dengan purge horizon, belum walk-forward/embargo/final holdout/calibration atau P/L cost-aware | AU-019/023/025; jangan melabelinya evaluasi v3 |
| P1 | Cache model dan nama file memuat login; stdout v2 mencetak akun mentah | Masking diagnostic/journal AU-005/027, runtime artifacts di-ignore |
| P1 | HTML mereferensikan manifest, ikon dan sw.js yang tidak tersedia | Simpan sebagai referensi; jangan impor random feed atau kontrol order ke dashboard |
| P1 | Restore state HTML mengembalikan `{...initialDefaults,obj}`, sehingga data tersimpan berada pada properti obj, bukan state.candles/positions | Perbaiki hanya jika demo simulasi kelak masuk scope; jangan reuse sebagai monitoring broker |

## Verifikasi

Source awal dipertahankan tanpa perubahan. Hash SHA256 tercatat di
`docs/BASELINE_HASHES.json`. Runtime v2, training broker, compile MQL5 dan demo
forward belum dijalankan. Laporan tes fondasi di `TEST_REPORT.md`.

Commit audit awal adalah `5263159`. Tes
`test_baseline_files_match_original_sha256` memeriksa keenam nama dan hash
SHA256 berkas asli pada rangkaian pytest lokal dan CI.
