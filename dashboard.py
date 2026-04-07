"""Streamlit real-time anomaly detection dashboard.

Usage:
    # In terminal 1: start stream
    python stream.py --rate 50 --attack-prob 0.03 &

    # In terminal 2: launch dashboard
    streamlit run dashboard.py --server.port 8501
"""

from __future__ import annotations

import pathlib
import time

import pandas as pd
import streamlit as st

from presidio_ids.detector import IsolationForestDetector
from presidio_ids.features import FEATURE_COLS, get_X

STREAM_PATH = "data/stream_live.csv"
DEFAULT_MODEL = "models/ids_model.pkl"
REFRESH_INTERVAL = 2  # seconds
MAX_DISPLAY_ROWS = 200

st.set_page_config(page_title="Presidio IDS Dashboard", layout="wide")
st.title("Presidio IDS — Real-Time Anomaly Detection")

# Sidebar
st.sidebar.header("Configuration")
model_path = st.sidebar.text_input("Model path", value=DEFAULT_MODEL)
stream_path = st.sidebar.text_input("Stream file", value=STREAM_PATH)
threshold_override = st.sidebar.slider(
    "Anomaly threshold (lower = more sensitive)", -0.6, 0.0, -0.3, step=0.01
)
auto_refresh = st.sidebar.checkbox("Auto-refresh (2s)", value=True)


# Load detector
@st.cache_resource
def load_detector(path: str):
    if not pathlib.Path(path).exists():
        return None
    return IsolationForestDetector.load(path)


detector = load_detector(model_path)
if detector is None:
    st.warning(f"Model not found at `{model_path}`. Train first with `train.py`.")
    st.stop()

threshold = threshold_override if threshold_override != -0.3 else detector._threshold

# Load stream data
if not pathlib.Path(stream_path).exists():
    st.info(f"No stream file at `{stream_path}`. Start `stream.py` to begin.")
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()
    st.stop()

df = pd.read_csv(stream_path).tail(MAX_DISPLAY_ROWS)
if df.empty or not all(c in df.columns for c in FEATURE_COLS):
    st.info("Stream file is empty or missing features.")
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()
    st.stop()

X = get_X(df)
scores = detector.score_samples(X)
df["anomaly_score"] = scores
df["anomaly"] = (scores < threshold).astype(int)

# Metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Flows (last window)", len(df))
col2.metric("Anomalies detected", int(df["anomaly"].sum()))
col3.metric("Anomaly rate", f"{df['anomaly'].mean():.1%}")
col4.metric("Threshold", f"{threshold:.4f}")

# Anomaly score chart
st.subheader("Anomaly Scores (lower = more anomalous)")
chart_df = df[["anomaly_score"]].copy()
chart_df["threshold"] = threshold
st.line_chart(chart_df)

# Anomalous flows table
anomalies = df[df["anomaly"] == 1]
st.subheader(f"Flagged Flows ({len(anomalies)})")
if anomalies.empty:
    st.success("No anomalies in current window.")
else:
    st.dataframe(anomalies[FEATURE_COLS + ["anomaly_score"]].head(50), use_container_width=True)

if auto_refresh:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()
