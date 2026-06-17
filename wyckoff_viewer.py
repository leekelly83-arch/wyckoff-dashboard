import streamlit as st
import pandas as pd

# ✅ Set file path for cloud
FILE_PATH = "data/wyckoff_ranked_latest.csv"

# ✅ Load data
@st.cache_data
def load_data():
    return pd.read_csv(FILE_PATH)

# ✅ Main app
def main():
    st.title("Wyckoff Scanner Dashboard")

    try:
        df = load_data()
        
        st.success("Data loaded successfully ✅")
        
        # Show data
        st.dataframe(df)
        
        # Show basic info
        st.subheader("Data Summary")
        st.write(df.describe())

    except Exception as e:
        st.error("Error loading data ❌")
        st.write(e)


if __name__ == "__main__":
    main()
