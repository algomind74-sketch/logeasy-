import streamlit as st
import pandas as pd
from log_analyzer import analyze_logs
import os

# --- Page Setup (NEW THEME) ---
# --- Page Setup (FIXED) ---
st.set_page_config(
    layout="wide", 
    page_title="Dashboard | LogEasy",
    initial_sidebar_state="expanded"
    # 'theme' argument removed to support older Streamlit versions
)

st.title("LogEasy AI Dashboard 🤖")
st.markdown("Upload a log file to see the automated analysis. Navigate using the sidebar.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload your log set (.csv)", type=["csv"])

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

if uploaded_file is not None and uploaded_file != st.session_state.last_uploaded_file:
    st.session_state.last_uploaded_file = uploaded_file
    st.session_state.pop('df_full', None)
    st.session_state.pop('proactive_df', None)
    st.session_state.pop('errors_df', None)
    st.session_state.pop('ai_insight_text', None)

# --- Run App if File Exists ---
if uploaded_file is not None:
    
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY not set. Please set it in your terminal and restart.")
    else:
        # --- Check if we've already processed this file ---
        if 'df_full' not in st.session_state:
            with st.spinner('Analyzing... This may take a moment...'):
                try:
                    df_full = pd.read_csv(uploaded_file)
                    st.session_state.df_full = df_full 

                    @st.cache_data
                    def get_analysis(data):
                        print("Running AI analysis...")
                        return analyze_logs(data)
                    
                    proactive_df, errors_df, ai_insight_text = get_analysis(df_full)
                    
                    st.session_state.proactive_df = proactive_df
                    st.session_state.errors_df = errors_df
                    st.session_state.ai_insight_text = ai_insight_text
                    
                    st.success('Analysis Complete!')
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.stop()
        
        # --- Display Data from Session State ---
        df_full = st.session_state.df_full
        ai_insight_text = st.session_state.ai_insight_text
        
        # --- GRAPH SECTION (CHANGED TO MATCH VIDEO) ---
        
        # --- Chart 1: Error Trend (Line Chart) ---
        st.header("📈 Error Trend (Recent Days)")
        
        if 'Timestamp' not in df_full.columns or 'LogLevel' not in df_full.columns:
            st.warning("Cannot draw trend: Log file is missing 'Timestamp' or 'LogLevel' column.")
        else:
            df_graph = df_full.copy()
            df_graph['Timestamp'] = pd.to_datetime(df_graph['Timestamp'])
            
            # Group by day and count *only* errors
            df_errors_trend = df_graph[df_graph['LogLevel'] == 'ERROR'].set_index('Timestamp').resample('D')['Message'].count()
            df_errors_trend = df_errors_trend.rename("error_count")

            if df_errors_trend.empty:
                st.info("No ERROR logs found to plot trend.")
            else:
                st.line_chart(df_errors_trend, color="#FF0000") # Red line like video

        # --- Chart 2: Errors by Service (Bar Chart) ---
        st.header("📊 Errors by Service")
        if 'ServiceID' not in df_full.columns or 'LogLevel' not in df_full.columns:
            st.warning("Cannot draw chart: Log file is missing 'ServiceID' or 'LogLevel' column.")
        else:
            # Group by ServiceID and count *only* errors
            df_service_errors = df_full[df_full['LogLevel'] == 'ERROR']['ServiceID'].value_counts()
            
            if df_service_errors.empty:
                st.info("No ERROR logs found to plot services.")
            else:
                # Use the primaryColor for the bars
                st.bar_chart(df_service_errors, color="#1976D2") 

        # --- AI INSIGHTS BAR ---
        if ai_insight_text:
            st.header("💡 AI Insights")
            st.info(ai_insight_text)
        else:
            st.info("AI analysis found no major patterns.")
else:
    st.info("Please upload a log file (.csv) to begin.")