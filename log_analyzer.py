import pandas as pd
import google.generativeai as genai
import json
import os
import re

# --- Our Confirmed Working Model ---
WORKING_MODEL = "models/gemini-2.5-flash"

# --- Master Prompt (For finding issues) ---
MASTER_PROMPT = """
You are a log analysis engine. Your task is to analyze log data.
You MUST NOT greet or ask questions.
You MUST ONLY output the analysis in the specified format.

Analyze the log data below. Find all 'ERROR', 'SECURITY', and 'WARN' logs.
Create one line for each unique issue.

Your response MUST follow this exact format:
TYPE | PRIORITY | SUMMARY | SUGGESTION

- TYPE must be 'Error' or 'Warning'.
- PRIORITY must be High, Medium, or Low.
- SUMMARY is a 1-sentence summary.
- SUGGESTION is the likely cause.

Label 'ERROR' and 'SECURITY' logs as 'Error' (High/Medium priority).
Label 'WARN' logs as 'Warning' (Low priority).

Example Output:
Error | High | PaymentAPI is down | BankConnector service is not responding.
Warning | Low | Database connection pool at 80% | The DB is under heavy load.
Error | Medium | Suspicious login attempts | Potential brute-force attack.

--- LOG DATA BEGINS ---
{logs}
--- LOG DATA ENDS ---
"""

# --- NEW "AI Insights" PROMPT ---
AI_INSIGHTS_PROMPT = """
You are a senior analyst AI. You will be given a list of log errors and warnings.
Your job is to find the SINGLE MOST IMPORTANT pattern or insight.
Do not list the errors. Just provide a 1-2 sentence summary.

Focus on:
- Time: Is there a spike at a specific time? (Logs have timestamps)
- Service: Is one service (like 'PaymentAPI') failing the most?
- Type: Is there a common error type (like 'timeout')?

Example: "I see a major spike in 'Payment failed: Bank server timeout' errors, all originating from the 'BankConnector' service between 3:00 and 3:10 AM. This suggests a critical outage with that specific partner."

Here are the logs to analyze:
{logs}
"""

# --- FUNCTION DEFINITION MODIFIED (FIX) ---
# It now accepts a DataFrame 'df' instead of 'uploaded_file'
def analyze_logs(df):
    """
    Analyzes a DataFrame of logs, sends it to Gemini for a PLAINTEXT analysis,
    and then parses that text into a DataFrame.
    """
    print("Starting log analysis (PlainText Method)...")
    proactive_df = pd.DataFrame()
    errors_df = pd.DataFrame()
    ai_insight_text = "" # Default empty string

    try:
        # 1. --- Configure the API ---
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(WORKING_MODEL) 

        # 2. --- Pre-filter Data (FIXED) ---
        # We NO LONGER read the file here. We just use the DataFrame 'df'
        filtered_df = df[df['LogLevel'].isin(['ERROR', 'WARN', 'SECURITY'])].copy()

        if filtered_df.empty:
            print("No actionable logs found. Returning empty DataFrames.")
            return proactive_df, errors_df, ai_insight_text

        # We'll use 100 logs. This is a safe number.
        if len(filtered_df) > 100: 
            filtered_df = filtered_df.sample(100)
            
        # We also need to add timestamps to the string for the AI Insights
        log_string = filtered_df[['Timestamp', 'LogLevel', 'ServiceID', 'Message']].to_string(index=False)


    except Exception as e:
        print(f"Error filtering DataFrame: {e}")
        return proactive_df, errors_df, ai_insight_text

    # 3. --- Call 1: Get the Table Data ---
    try:
        print(f"Sending PlainText prompt to Gemini model: {WORKING_MODEL}...")
        prompt = MASTER_PROMPT.format(logs=log_string)
        
        response = model.generate_content(prompt)
        print("--- RAW AI RESPONSE (Tables) ---")
        print(response.text)
        print("-----------------------")

        # 4. --- Parse the PLAINTEXT Response (ROBUST) ---
        # THIS IS THE UPDATED SECTION
        print("Parsing PlainText response...")
        ai_response_text = response.text
        
        error_list = []
        warning_list = []
        
        for line in ai_response_text.splitlines():
            if '|' in line:
                # 1. Strip whitespace AND any leading/trailing pipes
                clean_line = line.strip().strip('|')
                
                # 2. Split the cleaned line by the pipe
                parts = [p.strip() for p in clean_line.split('|')]
                
                # 3. Check for 4 parts AND ignore the table header
                if len(parts) == 4 and parts[0].strip().lower() not in ["type", "----"]:
                    issue_type = parts[0].strip().lower()
                    issue_data = {
                        "priority": parts[1].strip(),
                        "summary": parts[2].strip(),
                        "suggestion": parts[3].strip()
                    }
                    if issue_type == 'error':
                        error_list.append(issue_data)
                    elif issue_type == 'warning':
                        warning_list.append(issue_data)
        
        errors_df = pd.DataFrame(error_list)
        proactive_df = pd.DataFrame(warning_list)

        # 5. --- Call 2: Get the AI Insight (NEW) ---
        if not errors_df.empty or not proactive_df.empty:
            print("Sending AI Insights prompt...")
            # We send the *original* filtered log string (with timestamps)
            prompt_insight = AI_INSIGHTS_PROMPT.format(logs=log_string)
            response_insight = model.generate_content(prompt_insight)
            ai_insight_text = response_insight.text
            print(f"--- AI Insight Response --- \n{ai_insight_text}")
        
        print("Analysis complete. Returning all data.")
        return proactive_df, errors_df, ai_insight_text

    except Exception as e:
        print("\n" + "="*50)
        print("!!! CRITICAL ERROR DURING API CALL OR PARSING !!!")
        print(f"THE ERROR MESSAGE IS: {e}")
        print("="*50 + "\n")
        return proactive_df, errors_df, ai_insight_text