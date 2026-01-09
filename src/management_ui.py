import streamlit as st
import requests
import pandas as pd
from tab_lang_graph.config import settings

# This is a placeholder for the UI logic described in spec 005
# In a real app, this would be a separate streamlit app file.

def render_sidebar():
    st.sidebar.title("TabLangGraph")
    status = get_status()
    st.sidebar.metric("Status", status.get("status", "Unknown"))
    
    if st.sidebar.button("Pause/Resume"):
        toggle_status(status.get("status"))

def get_status():
    try:
        resp = requests.get(f"http://{settings.LG_HOST}:{settings.LG_PORT}/status")
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {"status": "Disconnected"}

def toggle_status(current_status):
    action = "resume" if current_status == "paused" else "pause"
    try:
        requests.post(f"http://{settings.LG_HOST}:{settings.LG_PORT}/control?action={action}")
    except:
        st.error("Failed to control bridge")

def render_history_table():
    st.header("Execution History")
    try:
        resp = requests.get(f"http://{settings.LG_HOST}:{settings.LG_PORT}/history")
        if resp.status_code == 200:
            data = resp.json()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.info("No history yet")
    except:
        st.warning("Could not fetch history")

def main():
    render_sidebar()
    render_history_table()

if __name__ == "__main__":
    main()
