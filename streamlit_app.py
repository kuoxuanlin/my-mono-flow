import streamlit as st
import json
import os

# --- 頁面配置 ---
st.set_page_config(page_title="MONO // FLOW", layout="wide")

# --- 極簡黑化 CSS ---
st.markdown("""
    <style>
    /* 全域背景黑化 */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* 隱藏 Streamlit 預設元件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 任務卡片樣式 */
    .task-card {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        filter: blur(0px);
    }
    
    /* 空間感：未被選中的內容模擬模糊效果 */
    .stTextInput > div > div > input {
        background-color: #0a0a0a;
        color: white;
        border: 1px solid #222;
    }

    /* 刪除時的模糊動畫類 (透過 JS 觸發或狀態控制) */
    .blur-out {
        filter: blur(20px);
        opacity: 0;
        transform: scale(0.9);
    }
    </style>
""", unsafe_allow_html=True)

# --- 資料邏輯 ---
DB_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return []

def save_tasks(tasks):
    with open(DB_FILE, "w") as f: json.dump(tasks, f)

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()

# --- 介面渲染 ---
st.title("INTERFACE // TASK FLOW")
st.caption("SYSTEM_STATUS: OPERATIONAL // NO_TIME_LIMIT")

# 頂部控制欄
col1, col2 = st.columns([4, 1])
with col1:
    new_task = st.text_input("", placeholder="ENTER NEW TASK...")
with col2:
    if st.button("+ ADD"):
        if new_task:
            st.session_state.tasks.append({"content": new_task, "status": "active"})
            save_tasks(st.session_state.tasks)
            st.rerun()

st.markdown("---")

# 任務流展示 (增加間距以提升空間感)
for idx, task in enumerate(st.session_state.tasks):
    with st.container():
        # 這裡模擬卡片
        cols = st.columns([0.1, 4, 1])
        with cols[1]:
            st.markdown(f"""
                <div class="task-card">
                    <div style="font-size: 10px; color: #444; letter-spacing: 2px;">TASK // {idx+1:02}</div>
                    <div style="font-size: 20px; font-weight: 700; margin-top: 10px;">{task['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.write(" ") # 調整按鈕垂直位置
            st.write(" ")
            if st.button("DONE", key=f"del_{idx}"):
                # 這裡目前 streamlit 無法做完美的局部 blur 動畫
                # 但我們可以透過 session_state 標記來達成邏輯上的淡出
                st.session_state.tasks.pop(idx)
                save_tasks(st.session_state.tasks)
                st.rerun()