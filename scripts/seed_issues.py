"""Generate local seed issues once from the preserved project backlog."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA_FILES = {
    "infra": "pyproject.toml, config/, scripts/, .github/, docs/",
    "mql5": "mt5/Experts/, mt5/Include/Aurum/, mt5/Presets/",
    "data": "python/aurum/mt5_client.py, python/aurum/data_quality.py, tests/",
    "ml": "python/aurum/{features,labels,walk_forward,train,predict,model_registry}.py",
    "risk": "mt5/Include/Aurum/, config/default.yaml, tests/test_risk.py",
    "backtest": "python/aurum/{costs,backtest}.py, tests/, reports/",
    "dashboard": "dashboard/app.py, python/aurum/journal.py, tests/",
    "docs": "docs/, README.md, mt5/README_MT5_ID.md",
}
AREA_TESTS = {
    "infra": "Offline import/config, input invalid, error exit, rerun idempotent; pytest dan lint.",
    "mql5": "Compile MetaEditor, sinyal closed-bar, data gagal, restart, ownership dan retcode.",
    "data": "Missing terminal/suffix, stale/open/duplicate/unsorted bars, NaN OHLC dan gap report.",
    "ml": "Fitur kausal, label ambigu, horizon purge dan penolakan model invalid.",
    "risk": "Min lot melebihi budget, margin gagal, leverage, news unknown, restart dan SL.",
    "backtest": "Entry setelah sinyal, biaya lengkap, SL-first intrabar, OOS replay deterministik.",
    "dashboard": "Empty/offline/error states, masking, tidak ada order/modify/close controls.",
    "docs": "Ikuti perintah dari venv bersih; cek tautan, status NOT RUN dan default non-eksekusi.",
}


def main() -> None:
    text = (ROOT / "BACKLOG_ISSUES_AURUM_MT5.md").read_text(encoding="utf-8")
    blocks = re.findall(r"### \[(AU-\d{3})\] (.*?)\n(.*?)(?=\n### |\n## |\Z)", text, re.S)
    if len(blocks) != 33:
        raise ValueError("Expected exactly 33 seed issues")
    target = ROOT / "docs/issues"
    target.mkdir(parents=True, exist_ok=True)
    rows = []
    for issue_id, title, body in blocks:
        fields = dict(re.findall(r"- \*\*(.*?):\*\* (.*)", body))
        priority, area = fields["Priority"], fields["Area"]
        status = "DONE" if issue_id == "AU-001" else "OPEN"
        if issue_id in {"AU-002", "AU-003", "AU-004", "AU-005", "AU-006", "AU-026", "AU-031"}:
            status = "IN_PROGRESS"
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        path = target / f"{issue_id}-{slug}.md"
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite reviewed issue: {path.name}")
        content = f"""# [{issue_id}] {title}

- Status: {status}
- Priority: {priority}
- Epic / label: area:{area}, priority:{priority}, type:feature
- Dependencies: {fields["Dependencies"]}
- Publication: NOT PUBLISHED
- PR/commit: lihat riwayat Git; belum ada PR khusus issue ini.

## Latar belakang

{fields["Latar belakang"]}

## Scope dan deliverable

{fields["Scope implementasi"]}

File/modul terkait: {AREA_FILES[area]}. Nama modul yang belum tersedia adalah target
implementasi, bukan klaim source sudah lengkap.

## Tasks

- [ ] Verifikasi dependensi issue dan kontrak input/output.
- [ ] Implementasikan scope di atas dengan reason code dan fail-closed path.
- [ ] Tambahkan kasus positif, negatif, dan regression yang relevan.
- [ ] Perbarui dokumentasi, konfigurasi, serta bukti di docs/TEST_REPORT.md.
- [ ] Review acceptance dan tautkan PR/commit sebelum menandai DONE.

## Acceptance criteria

- [ ] {fields["Acceptance criteria minimum"]}
- [ ] Input invalid tidak menghasilkan sinyal/order/hasil sukses palsu.
- [ ] Tes yang relevan PASS; tes yang tidak tersedia ditulis NOT RUN dengan alasan.
- [ ] Dokumentasi menyebut perilaku aktual dan keterbatasan, tanpa klaim profit.

## Skenario tes

{AREA_TESTS[area]}

Offline: `python -m pytest -q`; lint: `python -m ruff check python tests scripts dashboard`.
Kompilasi terminal jika relevan: `./scripts/compile_mql5.ps1 -MetaEditor <path>`.
Kasus tambahan harus mengikuti scope dan AC spesifik di atas; tes umum saja tidak
cukup untuk menutup issue.

## Definition of done

Source/contract nyata, AC terverifikasi, negative-case tests dan dokumentasi
diperbarui, bukti tes disimpan, lalu status dan referensi PR/commit diperbarui.
Status seed bukan bukti bahwa implementasi produk telah selesai.
"""
        if issue_id == "AU-001":
            content += "\nBukti audit: docs/BASELINE_AUDIT.md dan docs/BASELINE_HASHES.json.\n"
        path.write_text(content, encoding="utf-8")
        rows.append(
            f"| {issue_id} | [{title}](issues/{path.name}) | {priority} | {area} | "
            f"{fields['Dependencies']} | {status} |"
        )
    (ROOT / "docs/ISSUES_BACKLOG.md").write_text(
        "# Backlog implementasi\n\n33 seed lokal. NOT PUBLISHED: GitHub CLI belum tersedia; "
        "publikasi remote belum dijalankan. Status fondasi tidak berarti produk siap trading.\n\n"
        "| ID | Issue | Prioritas | Area | Dependencies | Status |\n"
        "|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
        "AU-001: audit selesai, kompilasi baseline tidak mungkin karena source tidak disertakan.\n"
        "AU-002/003/004/005/006/026/031: fondasi tersedia, acceptance produk belum lengkap.\n"
        "Issue lainnya OPEN. Tidak ada issue ditutup di GitHub.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
