import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# --- 0. 基礎配置 ---
DB_FILE = "mono_v15_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【全頁面模組初始化】 - 採用「無嵌套引號」結構
# =========================================================

if 'code_store' not in st.session_state:
    st.session_state.code_store = {
        "1_GLOBAL": "# 全局樣式\nstyle = '<style>.stApp { background-color: #000; color: #fff; } [data-testid=\"stSidebar\"] { background-color: #050505; } .header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; }</style>'\nst.markdown(style, unsafe_allow_html=True)",
        
        "2_DASHBOARD": "# 儀錶板邏輯\nst.markdown('### PROTOCOLS')\nl, r = st.columns([1, 1])\nwith l:\n    st.write('// 習慣序列')\n    for i, h in enumerate(data.get('habits', [])):\n        st.button(h['name'], key=f'h_{i}')\nwith r:\n    st.write('// 任務掃描')\n    for i, t in enumerate(data.get('tasks', [])):\n        st.button(t['name'], key=f't_{i}')",

        "4_VOID": "# 專注空間邏輯\nst.markdown('<div class=\"header-tag\">// NEURAL_VOID</div>', unsafe_allow_html=True)\nst.markdown('<style>@keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } } .timer-txt { font-size: 80px; text-align: center; font-family: monospace; animation: pulse 2s infinite; }</style>', unsafe_allow_html=True)\nm = st.slider('時長', 1, 120, 25)\nif st.button('啟動序列', use_container_width=True):\n    ph = st.empty()\n    for i in range(m*60, -1, -1):\n        mm, ss = divmod(i, 60)\n        ph.markdown(f'<div class=\"timer-txt\">{mm:02}:{ss:02}</div>', unsafe_allow_html=True)\n        time.sleep(1)\n    st.balloons()"
    }

# =========================================================
# 【核心系統】
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

# --- 側邊欄 ---
with st.sidebar:
    st.title("MONO // OS")
    nav = ["儀錶板", "專注空間", "系統設定"]
    if data.get("dev_mode"): nav.append("開發者主機")
    page = st.radio("導覽", nav)

# --- 執行環境配置 ---
exec_env = {
    "st": st, 
    "data": data, 
    "time": time, 
    "save_data": save_data, 
    "today": today,
    "pd": pd,
    "px": px
}

# 執行全局樣式
exec(st.session_state.code_store["1_GLOBAL"], exec_env)

# --- 路由 ---
if page == "儀錶板":
    exec(st.session_state.code_store["2_DASHBOARD"], exec_env)

elif page == "專注空間":
    # 這裡直接執行，不再使用嵌套引號
    try:
        exec(st.session_state.code_store["4_VOID"], exec_env)
    except Exception as e:
        st.error(f"模組執行失敗: {e}")

elif page == "開發者主機":
    st.title("🛠 MODULAR CONSOLE")
    target = st.selectbox("選擇模組", list(st.session_state.code_store.keys()))
    # 關鍵：這裡我們用普通的 text_area，並且在導出時確保換行
    st.session_state.code_store[target] = st.text_area("代碼編輯", st.session_state.code_store[target], height=500)
    
    st.divider()
    
    # 導出邏輯：手動構建乾淨的 Python 檔案
    py_content = "import streamlit as st\nimport json, os, time\nimport pandas as pd\nimport plotly.express as px\nfrom datetime import datetime, timedelta\n\n"
    py_content += "data = {}\n" # 導出後的預設變數
    for k in sorted(st.session_state.code_store.keys()):
        py_content += f"\n# --- {k} ---\n"
        py_content += st.session_state.code_store[k] + "\n"
        
    st.download_button("📦 下載修正後的 .py", data=py_content.encode('utf-8'), file_name="mono_fixed.py", mime="text/x-python")

elif page == "系統設定":
    st.title("SETTINGS")
    data["dev_mode"] = st.toggle("開發者模式", value=data.get("dev_mode", False))
    save_data(data)
