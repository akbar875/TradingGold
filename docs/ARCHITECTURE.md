# Arsitektur fondasi

Scope permintaan saat ini: inspeksi seluruh berkas awal dan scaffolding fase A.
PRD v3 menjadi target produk; master prompt adalah referensi pengembangan, bukan
status implementasi. README v2 dan HTML simulasi tidak menjadi spesifikasi runtime.

Alur target: broker MT5 -> Python data -> data quality -> fitur -> training dan
registry -> inference -> atomic bridge Common Files -> EA technical/risk gates.
EA kelak menjadi satu-satunya pemilik order dan posisi; logs/journal -> dashboard
read-only. Riset/backtest terpisah dari jalur broker.

Alur yang tersedia: YAML -> Settings tervalidasi -> CLI/show-config/doctor/fetch-data.
Adapter mengimpor MT5 secara lazy. Doctor memeriksa snapshot M15/H1/H4 pada
waktu tutup M15. Fetch-data memvalidasi candle MT5 tertutup sebelum mencetak
JSON dan mengonversi spread points memakai point simbol. Offline mode
tidak menginisialisasi MT5. EA membaca snapshot indikator M15/H1/H4 dari terminal
MT5, mengklasifikasikan market regime dan menampilkan WAIT. Dashboard menampilkan empty states.

## Kontrak dan peta pengembangan

| Modul | Kontrak / tanggung jawab | Status / issue |
|---|---|---|
| config.py | Settings immutable, validasi key YAML dan nilai | Tersedia, signal-only dipaksakan |
| contracts.py | Bar UTC, Action, Decision, FeatureBuilder, Predictor | Kontrak fondasi |
| mt5_client.py | Diagnostik broker/akun/simbol dengan masking dan pembacaan closed bars M15/H1/H4 | AU-005, terverifikasi offline |
| data_quality.py | Validasi OHLCV/spread, overlap, outlier, gap sesi UTC, snapshot closed-bar kausal | AU-006, fondasi |
| features.py, labels.py | Fitur kausal dan label horizon | Direncanakan AU-017/018 |
| walk_forward.py, train.py | Purge/embargo, RF deterministik, laporan OOS | Direncanakan AU-019 |
| model_registry.py, predict.py | Metadata/schema/expiry/quality gate, inference | Direncanakan AU-020 |
| bridge.py | Atomic CSV writer, canonical checksum dan context validation | Direncanakan AU-021 |
| costs.py, backtest.py | Simulasi setelah biaya dan intrabar konservatif | Direncanakan AU-023 |
| journal.py | Structured audit events dan redaksi data akun | Direncanakan AU-027 |
| mt5/Experts dan Include | EA diagnostik dengan snapshot indikator M15/H1/H4 dan filter market regime | AU-007/008, verifikasi offline. Setup, sinyal dan risiko di AU-009..016/022 |
| dashboard/app.py | Empty states dan konfigurasi Python read-only | Awal; AU-026 belum selesai |

Modul yang belum dikerjakan dicatat di tabel; tidak dibuat sebagai file kosong
yang terlihat seolah implementasi tersedia. Antarmuka CLI yang belum tersedia
selalu exit 2. CSV bridge ditentukan di SIGNAL_SCHEMA; JSON Schema dipakai untuk
representasi logis. Parser MQL5 dan writer atomic belum tersedia.

## Keputusan safety dan konfigurasi

Tidak ada kredensial broker, dataset privat, artifact model atau log akun di Git.
Default dipusatkan pada config/default.yaml untuk Python. MQL5 membaca input/preset
sendiri; tes parity menjaga nilai default bersama. Perubahan YAML tidak otomatis
mengubah input EA. Pada fase ini Settings menolak auto/demo/live execution karena
engine pengaman lengkap belum tersedia. Ini pembatasan sementara yang lebih aman
daripada mengizinkan opsi auto yang belum memiliki implementasi.

Loader Python menolak key YAML duplikat (termasuk benturan hasil merge), key
non-string, key asing, dan nilai di luar kontrak. CLI menerapkan `--symbol`
ke Settings dengan validasi yang sama sebelum menampilkan konfigurasi efektif
atau mengakses diagnostik MT5. Nama simbol dengan suffix broker dipertahankan
persis. Simbol kosong atau berisi whitespace, karakter kontrol, garis miring,
atau koma ditolak.

Baseline dipertahankan di root agar provenance tetap jelas; modul v3 tidak
mengimpor aurum_ai.py. Lisensi tidak diasumsikan. CI hanya menjalankan tes offline;
tidak mengakses broker. Jalur order baru boleh ditambahkan setelah issue safety
dan pengujian MT5 yang relevan lulus.
