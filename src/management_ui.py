import streamlit as st
import requests
import pandas as pd
from fancy_sheet_functions.config import settings
import os

# This is a placeholder for the UI logic described in spec 005
# In a real app, this would be a separate streamlit app file.

# Set the page configuration including the window icon (favicon)
st.set_page_config(
    page_title="TabLangGraph Management",
    page_icon="photos/Sir_Clipindale_III.png",
    layout="wide"
)

# Display the logo in the top left of the sidebar (Streamlit 1.35+)
if os.path.exists("photos/Sir_Clipindale_III.png"):
    st.logo("photos/Sir_Clipindale_III.png", icon_image="photos/Sir_Clipindale_III.png")

def render_sidebar():
    st.sidebar.image("photos/Sir_Clipindale_III.png")
    st.sidebar.title("FancySheetFunctions Management UI")
    status = get_status()
    st.sidebar.caption(f"Status: {status.get('status', 'Unknown')}")

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
    with st.expander("🕘 Execution History"):
        #st.header("Execution History")
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
            st.error("Failed to fetch history")

def render_task_manager():
    st.header("📋 Pending Tasks Manager")
    try:
        resp = requests.get(f"http://{settings.LG_HOST}:{settings.LG_PORT}/tasks")
        if resp.status_code == 200:
            tasks = resp.json()
            if not tasks:
                st.info("No tasks found.")
                return

            # Filter for active tasks (Pending/Running)
            active_tasks = [t for t in tasks if t['status'] in ['pending_approval', 'running']]
            
            if active_tasks:
                st.subheader(f"Active Tasks ({len(active_tasks)})")
                for task in active_tasks:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                        with col1:
                            st.write(f"**{task['workflow_id']}**")
                            st.caption(f"ID: {task['task_id'][:8]}...")
                        with col2:
                            st.write(task['status'])
                        with col3:
                            if task['status'] == 'pending_approval':
                                if st.button("✅ Approve & Run", key=f"run_{task['task_id']}"):
                                    requests.post(f"http://{settings.LG_HOST}:{settings.LG_PORT}/tasks/{task['task_id']}/approve")
                                    st.rerun()
                        with col4:
                            if st.button("❌ Cancel", key=f"cancel_{task['task_id']}"):
                                requests.post(f"http://{settings.LG_HOST}:{settings.LG_PORT}/tasks/{task['task_id']}/cancel")
                                st.rerun()
                        st.divider()
            
            # Completed Tasks Expander
            with st.expander("Completed / Failed Tasks"):
                done_tasks = [t for t in tasks if t['status'] not in ['pending_approval', 'running']]
                if done_tasks:
                    st.dataframe(pd.DataFrame(done_tasks))
                else:
                    st.info("No completed tasks.")

    except Exception as e:
        st.error(f"Failed to fetch tasks: {e}")

def render_tutorial():
    with st.expander("📚 How to use in LibreOffice"):
        st.markdown("""
        ### Setup
        Ensure the backend server is running and the macros are installed.

        ### Calling Functions
        Use the custom function `=FSF()` in any cell.

        **Syntax:**
        `=FSF("FunctionName", "Argument")`

        **Examples:**
        - Echo test: 
          `=FSF("Echo", "Hello World")`
        - Convert to upper case: 
          `=FSF("ToUpper", "some text")`
        
        *Note: The first argument is the Function Name string.*
        """)

def render_available_tools():
    with st.expander("🛠 Available Tools Registry"):
        try:
            resp = requests.get(f"http://{settings.LG_HOST}:{settings.LG_PORT}/workflows")
            if resp.status_code == 200:
                workflows = resp.json()
                if workflows:
                    for wf in workflows:
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.subheader(wf.get('name'))
                        with c2:
                            st.caption(wf.get('description'))
                            inputs = wf.get('inputs', [])
                            if inputs:
                                input_str = ", ".join([f"{i['name']}: {i['type']}" for i in inputs])
                                st.text(f"Inputs: {input_str}")
                        st.divider()
                else:
                    st.info("No workflows registered.")
            else:
                st.error("Failed to fetch workflows.")
        except Exception as e:
            st.error(f"Error connecting to registry: {e}")

def render_status_widget():
    with st.expander("🔄 Server Status"):
        
        status = get_status()
        status_text = status.get("status", "Unknown")
        
        # Determine color based on status
        if status_text == "active":
            color = "green"
            icon = "🟢"
        elif status_text == "paused":
            color = "orange"
            icon = "kz"
        else:
            color = "red"
            icon = "🔴"

        #c1, c2 = st.columns([3, 1])
        #with c1:
        st.caption(f"Server Status: {icon} **{status_text.upper()}**")
        if st.button("Pause/Resume", key="main_toggle"):
            toggle_status(status_text)
            st.rerun()
    #with c2:


def main():
    render_sidebar()
    
            # Visibility controls
    show_sections = st.segmented_control(
            "",
            options=["Tutorial", "Registry","Status","History"],
            selection_mode="multi",
            default=["Status", "History"]
        )


    if "Status" in show_sections:
        render_status_widget()

    if "History" in show_sections:
        render_history_table()
    

    if "Tutorial" in show_sections:
        render_tutorial()
        
    if "Registry" in show_sections:
        render_available_tools()
        
    render_task_manager()
    

if __name__ == "__main__":
    main()
