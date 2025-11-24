import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Warnings | LogEasy")
st.title("🔥 Proactive Warnings")

# Check if the results exist in the session state
if 'proactive_df' not in st.session_state:
    st.warning("Please upload a log file on the main '1_Dashboard' page first to see warnings.")
else:
    # Get the dataframe from the session state
    proactive_df = st.session_state.proactive_df

    # Display the results
    if proactive_df.empty:
        st.info("No proactive warnings found.")
    else:
        st.dataframe(proactive_df, use_container_width=True)