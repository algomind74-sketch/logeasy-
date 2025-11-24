import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Search | LogEasy")
st.title("🔴 Detected Errors & Log Search")

# Check if the results exist in the session state
if 'errors_df' not in st.session_state:
    st.warning("Please upload a log file on the main '1_Dashboard' page first to see errors.")
else:
    # Get the dataframe from the session state
    errors_df = st.session_state.errors_df

    # --- Sidebar Filters ---
    st.sidebar.header("Filter Issues")
    
    if not errors_df.empty and 'priority' in errors_df.columns:
        priority_options = ["All"] + list(errors_df['priority'].unique())
        selected_priority = st.sidebar.selectbox("Filter by Priority", options=priority_options)
        search_term = st.sidebar.text_input("Search in Summary")
    else:
        selected_priority = "All"
        search_term = ""

    # --- Filtering Logic ---
    filtered_errors = errors_df

    if not errors_df.empty:
        if selected_priority != "All" and 'priority' in errors_df.columns:
            filtered_errors = filtered_errors[filtered_errors['priority'] == selected_priority]
        if search_term and 'summary' in filtered_errors.columns:
            filtered_errors = filtered_errors[filtered_errors['summary'].str.contains(search_term, case=False)]
    
    # --- Display the Results ---
    if errors_df.empty:
        st.info("No critical errors detected.")
    elif filtered_errors.empty:
        st.warning("No errors match your current filter settings.")
    else:
        st.dataframe(filtered_errors, use_container_width=True)