import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io
import base64

# --- 0. 基礎配置 ---
DB_FILE = "mono_v16_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【全頁面模組初始化】 - 使用 Base64 避免轉義字元報錯
# =========================================================

# 預設的模組代碼（純文字）
default_codes = {
    "1_GLOBAL": """
st.markdown('<style>.stApp { background-color: #000; color: #fff; } [data-testid="stSidebar"] { background-color: #050505; } .header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; }</style>', unsafe_allow_html=True)
""",
    "2_DASHBOARD": """
st.markdown('### // PROTOCOLS')
c1, c2 = st.columns(2)
with c1:
    st.info("任務序列已就緒")
    if st.button("＋ 增加隨機 XP"):
        add_xp(10)
        st.rerun()
""",
    "4_VOID": """
st.markdown('<div class="header-tag">// NEURAL_VOID</div>', unsafe_allow_html=True)
st.markdown('<style>@keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } } .timer-txt { font-size: 80px; text-align: center; font-family: monospace; animation: pulse 2s infinite; }</style>', unsafe_allow_html=True)

m = st.slider('時長 (MIN)', 1, 120, 25)
if st.button('啟動專注序列', use_container_width=True):
    ph = st.empty()
    for i in range(m*60, -1, -1):
        mm, ss = divmod(i, 60)
        ph.markdown(f'<div class="timer-txt">{mm:02}:{ss:02}</div>', unsafe_allow_html=True)
        time.sleep(1)
    st.balloons()
"""
}

# 確保 session_state 存在
if 'code_store' not in st.session_state:
    st.session_state.code_store = default_codes

# =========================================================
# 【核心系統邏輯】
# =========================================================

def load_data():
    defaults = {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": [], "dev_mode": False}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return defaults
    return defaults

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

# --- 側邊欄 ---
with st.sidebar:
    st.title("MONO // OS")
    nav = ["儀錶板", "專注空間", "系統設定"]
    if data.get("dev_mode"): nav.append("開發者主機")
    page = st.radio("導覽", nav)

# --- 執行環境配置 ---
exec_env = {
    "st": st, "data": data, "time": time, "save_data": save_data, 
    "today": today, "pd": pd, "px": px, "add_xp": add_xp
}

# =========================================================
# 【安全執行引擎】
# =========================================================

def safe_exec(code_str):
    try:
        # 清除可能導致續行報錯的非法字元
        clean_code = code_str.strip()
        exec(clean_code, exec_env)
    except Exception as e:
        st.error(f"模組執行失敗: {e}")
        st.code(code_str, language="python") # 顯示有問題的代碼供調試

# 執行全局樣式
safe_exec(st.session_state.code_store["1_GLOBAL"])

# --- 路由分發 ---
if page == "儀錶板":
    safe_exec(st.session_state.code_store["2_DASHBOARD"])

elif page == "專注空間":
    safe_exec(st.session_state.code_store["4_VOID"])

elif page == "開發者主機":
    st.title("🛠 MODULAR ARCHITECT")
    target = st.selectbox("選擇編輯模組", list(st.session_state.code_store.keys()))
    
    # 編輯器
    new_code = st.text_area("代碼編輯區", st.session_state.code_store[target], height=500)
    st.session_state.code_store[target] = new_code
    
    st.divider()
    
    # 導出系統
    if st.button("📦 產生導出檔案"):
        output = io.StringIO()
        output.write("import streamlit as st\nimport json, os, time\nimport pandas as pd\nimport plotly.express as px\nfrom datetime import datetime, timedelta\n\n")
        output.write("data = {}\n")
        for k, v in st.session_state.code_store.items():
            output.write(f"\n# --- {k} ---\n{v}\n")
        
        st.download_button(
            label="💾 下載 .py 檔案",
            data=output.getvalue().encode('utf-8'),
            file_name="mono_os_stable.py",
            mime="text/x-python"
        )

elif page == "系統設定":
    st.title("SETTINGS")
    data["dev_mode"] = st.toggle("開發者模式", value=data.get("dev_mode", False))
    save_data(data)
