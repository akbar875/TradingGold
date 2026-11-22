# Kontrak bridge 1.0 — belum menjadi runtime

`config/signal.schema.json` mendeskripsikan payload logis. Transport target adalah
CSV UTF-8 tanpa BOM, dua record: header field dan satu record data. Urutan field
persis urutan `required` pada JSON Schema; newline LF; csv quoting standar.
Writer kelak menulis file temporary unik pada direktori sama, flush + fsync, lalu
os.replace ke file final di Common/Files terminal yang terverifikasi.

Timestamp integer UTC epoch seconds. `bar_open_time_utc` adalah waktu buka candle
M15 tertutup, bukan waktu close. `account_login` string digit, simbol suffix dan
server harus cocok persis dengan konteks EA; nomor akun hanya pada bridge lokal,
bukan dashboard/log publik. Semua probability finite [0,1], jumlah harus dalam
toleransi 1e-6 terhadap 1. Nilai decimal memakai titik dan bukan locale broker.

Checksum target SHA256 atas JSON canonical dari semua field selain checksum:
sort_keys=true, separators=(',', ':'), ensure_ascii=true, allow_nan=false,
encoded UTF-8. Implementasi Python/MQL5 harus membuktikan parity format angka
dengan fixture golden sebelum kontrak dianggap siap produksi.

Di luar JSON Schema, runtime wajib menolak: bar mismatch, generated sebelum
bar+900, generated di masa depan, expiry <= now atau <= generated, umur melampaui
TTL konfigurasi, model tidak di-allowlist/expired, quality != VALID, probability
tidak finite/tidak normalized, action tidak sesuai threshold/margin model, file
parsial, extra field, checksum mismatch, dan akun/server/symbol/timeframe berbeda.

JSON Schema saja tidak memverifikasi konteks, checksum, TTL, jumlah probability
atau quality model. AU-020/021/022 tetap OPEN sampai writer/parser dan tes negatif
Python serta MetaEditor tersedia. CSV v2 aurum_ai.py tidak kompatibel.
