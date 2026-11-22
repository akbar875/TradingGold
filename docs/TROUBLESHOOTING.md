# Troubleshooting

| Status | Langkah |
|---|---|
| Python tidak ditemukan | Pasang Python 3.11+ 64-bit, cek `py -0p`, buat ulang venv melalui interpreter itu |
| Module aurum tidak ditemukan | Jalankan `python -m pip install -e ".[dev]"` di venv dari root repo |
| MT5_PACKAGE_MISSING | Pasang ekstra `[mt5]` pada Windows jika ingin diagnostik broker |
| MT5_INITIALIZE_FAILED / DISCONNECTED | Buka terminal desktop dan login sendiri; jangan simpan password di repo |
| SYMBOL_UNAVAILABLE | Cek nama simbol termasuk suffix di Market Watch |
| TICK_INVALID_OR_STALE | Cek sesi pasar, koneksi broker, bid/ask dan clock UTC |
| NOT_IMPLEMENTED | Fitur masih backlog; tidak ada hasil atau order yang dijalankan |
| EXECUTION_NOT_IMPLEMENTED | Kembalikan konfigurasi signal-only; auto belum didukung |
| Compile NOT RUN | Tentukan path MetaEditor; lihat reports/mql5-status.txt |

HTML demo memakai harga simulasi dan dependency PWA yang tidak dilampirkan. Jangan
menafsirkan saldo atau order HTML sebagai koneksi akun MT5.
