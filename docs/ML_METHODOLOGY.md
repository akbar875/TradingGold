# Metodologi ML target

Scaffold belum melatih model v3. Baseline aurum_ai.py tetap terpisah untuk audit.
AU-017..020 akan memigrasikan fitur kausal, label dan training ke modul kecil.

Fitur memakai bar tertutup dan higher timeframe past-only. Label triple barrier
horizon awal 8 M15 memakai masa depan hanya pada training. Bar menyentuh dua
barrier menghasilkan WAIT; ekor tanpa horizon penuh tetap unlabeled.
RandomForest seed 42, chronological walk-forward dengan purge minimal horizon,
embargo yang eksplisit dan holdout final terpisah dari tuning.

Artifact wajib punya schema fitur/hash dataset/config, broker, rentang waktu,
model version, metrics, expiry dan quality. Metrik klasifikasi bukan profitabilitas
atau win rate trading. Tidak ada angka akurasi nyata yang dilaporkan pada scaffold.
Pemilihan model/threshold dan ablation biaya dilakukan pada data yang sumbernya
tercatat; fixture sintetis hanya untuk tes. Joblib pihak asing tidak boleh dimuat.
