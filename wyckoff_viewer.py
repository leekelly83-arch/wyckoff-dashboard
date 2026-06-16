import os
import pandas as pd
import streamlit as st
from datetime import datetime

# =========================
# CONFIG
# =========================
FILE_PATH = r"C:\Users\leeke\OneDrive\Scanner\summaries\wyckoff_ranked_latest.csv"
LOGO_PATH = "logo.png"

# =========================
# HELPERS
# =========================
def get_file_timestamp(path):
    if os.path.exists(path):
        return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
    return "File not found"

def load_data():
    return pd.read_csv(FILE_PATH)

def section_header(title):
    st.markdown(
        f"""
        <div class="section-header">
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# PAGE SETTINGS
# =========================
st.set_page_config(page_title="Sovereign Analytics", layout="wide")

# =========================
# GLOBAL STYLING
# =========================
st.markdown("""
<style>

/* Buttons */
.stButton > button {
    background-color: #FDC9A3;
    color: black;
    border-radius: 6px;
    border: none;
    padding: 6px 12px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #fbbf94;
}

/* Section headers */
.section-header {
    background-color:#FDC9A3;
    padding:10px 14px;
    border-radius:6px;
    font-weight:600;
    margin-top:20px;
    margin-bottom:10px;
    color: black;
}

/* Tighten page top padding slightly */
.block-container {
    padding-top: 1rem;
}

/* Stronger labels */
label {
    font-weight: 600 !important;
}

/* Make the dataframe/editor text a bit tighter */
[data-testid="stDataFrame"] * {
    font-size: 13px !important;
}

/* Reduce extra padding around data editor cells a little */
[data-testid="stDataEditor"] * {
    font-size: 13px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
df = load_data()

# Normalize string columns
for col in ["symbol", "market_phase", "phase_confidence", "structure_quality"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# =========================
# HEADER (LOGO ONLY)
# =========================
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=320)

# =========================
# TOP BAR
# =========================
top_col1, top_col2 = st.columns([1, 4])

with top_col1:
    if st.button("Refresh Data"):
        st.rerun()

with top_col2:
    st.caption(f"Last Updated: {get_file_timestamp(FILE_PATH)}")

# =========================
# SCANNER
# Constrain width so table doesn't stretch too much
# =========================
section_header("Scanner")

scanner_container, _ = st.columns([7, 3])

with scanner_container:

    # -------------------------
    # FILTER ROW (aligned to columns)
    # -------------------------
    f1, f2, f3, f4, f5 = st.columns([1, 1, 1, 1, 1])

    with f1:
        symbol_filter = st.text_input("Symbol", "")

    with f2:
        phase_options = ["All"] + sorted(df["market_phase"].dropna().unique().tolist())
        phase_filter = st.selectbox("Phase", phase_options)

    with f3:
        conf_options = ["All"] + sorted(df["phase_confidence"].dropna().unique().tolist())
        confidence_filter = st.selectbox("Conf", conf_options)

    with f4:
        structure_options = ["All"] + sorted(df["structure_quality"].dropna().unique().tolist())
        structure_filter = st.selectbox("Struct", structure_options)

    with f5:
        min_score = st.number_input("Min Score", min_value=0, value=0, step=1)

    # -------------------------
    # APPLY FILTERS
    # -------------------------
    filtered_df = df.copy()

    if symbol_filter:
        filtered_df = filtered_df[
            filtered_df["symbol"].str.contains(symbol_filter, case=False, na=False)
        ]

    if phase_filter != "All":
        filtered_df = filtered_df[filtered_df["market_phase"] == phase_filter]

    if confidence_filter != "All":
        filtered_df = filtered_df[filtered_df["phase_confidence"] == confidence_filter]

    if structure_filter != "All":
        filtered_df = filtered_df[filtered_df["structure_quality"] == structure_filter]

    filtered_df = filtered_df[filtered_df["research_score"] >= min_score]

    # -------------------------
    # BUILD SCANNER TABLE
    # -------------------------
    scanner_df = filtered_df[[
        "symbol",
        "market_phase",
        "phase_confidence",
        "structure_quality",
        "research_score"
    ]].rename(columns={
        "symbol": "Symbol",
        "market_phase": "Phase",
        "phase_confidence": "Conf",
        "structure_quality": "Struct",
        "research_score": "Score"
    }).sort_values(by="Score", ascending=False)

    if scanner_df.empty:
        st.warning("No results match the selected filters.")
        st.stop()

    # -------------------------
    # TIGHTER TABLE
    # data_editor usually behaves better than dataframe here
    # -------------------------
    st.data_editor(
        scanner_df,
        use_container_width=True,
        height=320,
        hide_index=True,
        disabled=True,
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", width="small"),
            "Phase": st.column_config.TextColumn("Phase", width="small"),
            "Conf": st.column_config.TextColumn("Conf", width="small"),
            "Struct": st.column_config.TextColumn("Struct", width="small"),
            "Score": st.column_config.NumberColumn("Score", width="small", format="%d"),
        }
    )

# =========================
# SELECT SYMBOL
# =========================
section_header("Select Symbol")

symbols = scanner_df["Symbol"].tolist()
selected_symbol = st.selectbox("", symbols)

row = filtered_df[filtered_df["symbol"] == selected_symbol].iloc[0]

# =========================
# SYMBOL SUMMARY
# =========================
section_header(f"{selected_symbol} Summary")

st.markdown(f"""
<div style="
    display:flex;
    gap:40px;
    font-size:15px;
    padding:16px;
    background-color:#FDC9A3;
    border-radius:8px;
    color:black;
">
    <div><b>Market Phase</b><br>{row['market_phase']}</div>
    <div><b>Confidence</b><br>{row['phase_confidence']}</div>
    <div><b>Structure Quality</b><br>{row['structure_quality']}</div>
    <div><b>Score</b><br>{row['research_score']}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# SIGNAL SECTIONS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    section_header("Structural Events")
    for item in str(row["structural_events"]).split("|"):
        item = item.strip()
        if item:
            st.write(item)

with col2:
    section_header("Key Observations")
    for item in str(row["key_observations"]).split("|"):
        item = item.strip()
        if item:
            st.write(item)

with col3:
    section_header("Caution Flags")
    for item in str(row["caution_flags"]).split("|"):
        item = item.strip()
        if item:
            st.write(item)

# =========================
# FULL ANALYSIS
# =========================
with st.expander("Full Analysis"):

    section_header("Trend Structure")
    st.write(row["trend_structure"])

    section_header("Effort vs Result")
    st.write(row["effort_vs_result"])

    section_header("Volume Behavior")
    st.write(row["volume_behavior"])

    section_header("Accumulation / Distribution")
    st.write(row["accumulation_distribution"])

    section_header("Composite Operator")
    st.write(row["composite_operator"])