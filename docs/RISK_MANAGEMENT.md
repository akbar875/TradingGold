# Risiko dan batas tahap fondasi

EA fondasi tidak memiliki OrderSend/CTrade atau manajemen posisi. Semua input
auto ditolak. Preset Demo_Conservative sengaja tetap non-eksekusi hingga AU-014
dan seluruh dependensi selesai. Jangan memasang scaffold sebagai pengelola posisi.

Default target: risiko 0,25% ekuitas, lot cap 0,05, daily loss 2%, entry/hari 3,
posisi/symbol 1, margin 15% free margin, loss beruntun 3. Break-even 1R,
trailing 1,5R, stop maksimum 3 ATR, planned RR minimum 2. Partial TP OFF.
Leverage aktual harus dibaca dari akun; pengecekan 2000 tidak menentukan lot.

Implementasi berikutnya wajib menggunakan OrderCalcProfit untuk risiko per lot,
round volume ke bawah sesuai broker step, menolak min lot di atas budget dan
memeriksa OrderCalcMargin. SL/TP server-side dan revalidasi tick wajib untuk order.
News unknown ketika wajib, data stale, AI invalid ketika wajib, spread berlebih,
state restart ambigu, kill switch dan daily gate harus memblokir entry baru.

Daily baseline harus persist berdasarkan hari broker, memasukkan floating loss,
dan tidak reset karena restart. Definisi rollover/timezone/DST harus terdokumentasi
dan diuji sebelum eksekusi diaktifkan. Ownership account/symbol/magic/ticket dan
reconciliation perlu diuji. SL tidak boleh dilonggarkan oleh trailing.

Semua aturan di atas adalah target AU-012..016/028/033, belum risk engine lengkap.
Gap/slippage/biaya dapat melampaui estimasi loss pada SL.
