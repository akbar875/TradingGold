"""Read-only foundation view. No MT5 import or order controls."""

from pathlib import Path

import streamlit as st

from aurum import __version__
from aurum.config import load_config

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Aurum — Monitoring", layout="wide")
st.title("Aurum Expert AI MT5")
st.caption(f"Fondasi {__version__} · Monitoring read-only")
st.warning("WAIT · ENGINE_NOT_IMPLEMENTED · SIGNAL ONLY")
st.info("Belum ada data terverifikasi dari MT5. Koneksi broker belum diperiksa.")
st.write("Model: belum tersedia. Backtest: NO VALIDATED BACKTEST.")
st.write("Sinyal, posisi, jurnal, dan equity curve akan tersedia setelah fase integrasi.")
try:
    config = load_config(ROOT / "config/default.yaml")
except (OSError, ValueError) as exc:
    st.error(f"Konfigurasi tidak valid: {exc}")
else:
    with st.expander("Konfigurasi Python (bukan snapshot input EA)"):
        st.json(config.to_dict())
