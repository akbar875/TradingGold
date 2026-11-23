# [AU-010] Explainable signal scoring dan reason codes

- Status: OPEN
- Priority: P0
- Epic / label: area:mql5, priority:P0, type:feature
- Dependencies: AU-009
- Publication: [GitHub #10](https://github.com/akbar875/TradingGold/issues/10)
- PR/commit: lihat riwayat Git.

## Latar belakang

Sinyal dapat diaudit oleh pengguna.

## Scope dan deliverable

`Signals.mqh` memakai hasil regime AU-008 dan setup AU-009 untuk menghasilkan
kandidat teknikal dengan ID deterministik, skor heuristik 0–100, dan bukti tiap
komponen. EA tetap WAIT untuk entry dan menampilkan alasan utama beserta gate
gagal lain yang dapat dievaluasi. Journal mencatat maksimal satu event per
akun, server, simbol, dan candle M15. Kedua preset tetap signal-only.

## Tasks

- [x] Verifikasi dependensi issue dan kontrak input/output.
- [x] Implementasikan scope di atas dengan reason code dan fail-closed path.
- [x] Tambahkan kasus positif, negatif, dan regresi yang relevan.
- [x] Dokumentasikan skor, aturan preset, serta bukti verifikasi.
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [x] Kandidat menyertakan `SETUP_CONFIRMED`, ID, skor berlabel heuristik dan
  bukti tiap komponen. WAIT menyertakan alasan yang terurut.
- [x] Snapshot, quote, akun, atau state yang invalid menahan kandidat dan
  penerbitan. Skor tidak mengesampingkan hard gate atau membuka order.
- [x] Suite offline **PASS**. MetaEditor dan terminal **NOT RUN** karena tool
  tidak tersedia. Lihat [laporan tes](../TEST_REPORT.md#au-010--skor-heuristik-dan-reason-codes-24-november-2026).
- [x] [Aturan strategi](../STRATEGY_RULES.md#skor-heuristik-dan-alasan-keputusan-au-010)
  mendokumentasikan bobot, prioritas gate, batas fondasi, dan perilaku restart.

## Skenario tes

Fixture offline mencakup BUY/SELL kedua setup, skor 75/100, WAIT karena banyak
gate, snapshot basi atau invalid, quote basi dan chase, pergantian scope akun,
state file gagal, serta ID dan deduplikasi setelah simulasi restart.
Verifikasi native mencakup compile, Strategy Tester, dan panel/Journal pada
preset Signal_Only. Ownership posisi dan retcode mengikuti AU-014.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
