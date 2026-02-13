import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# --- 0. 基礎配置 ---
DB_FILE = "mono_v18_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【全頁面模組初始化】
# =========================================================

if 'code_store' not in st.session_state:
    st.session_state.code_store = {
        "1_GLOBAL": "# 全局樣式\\nstyle = '<style>.stApp { background-color: #000; color: #fff; } [data-testid=\"stSidebar\"] { background-color: #050505; } .header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; }</style>'\\nst.markdown(style, unsafe_allow_html=True)",
        
        "4_VOID": """
# --- 專注空間頁面 (神經脈衝增強版) ---
css = '<style>@keyframes glow { 0% { text-shadow: 0 0 5px #fff; opacity: 0.8; } 50% { text-shadow: 0 0 20px #fff, 0 0 30px #fff; opacity: 1; } 100% { text-shadow: 0 0 5px #fff; opacity: 0.8; } } @keyframes pulse { 0%, 100% { height: 10px; opacity: 0.3; } 50% { height: 40px; opacity: 1; } } .timer-active { font-size: 100px; font-family: monospace; text-align: center; animation: glow 2s infinite ease-in-out; margin-bottom: 0; } .neural-container { display: flex; justify-content: center; align-items: flex-end; gap: 4px; height: 50px; margin: 20px 0; } .pulse-bar { width: 3px; background: #fff; animation: pulse 1.5s infinite ease-in-out; }</style>'
st.markdown(css, unsafe_allow_html=True)
st.markdown("<div class='header-tag'>// 深度專注序列 NEURAL_VOID</div>", unsafe_allow_html=True)

quotes = ["靜默是最高級的運算。", "刪除雜訊，保留核心。", "專注是唯一的武裝。", "在代碼中尋找秩序。"]
m = st.slider("設定頻率時長 (MIN)", 5, 120, 25, 5)

if st.button("啟動專注序列", use_container_width=True):
    ph = st.empty()
    bar = st.progress(0)
    q_box = st.info(quotes[int(time.time()) % len(quotes)])
    pulse_html = "<div class='neural-container'>" + "".join([f"<div class='pulse-bar' style='animation-delay: {0.1*i}s'></div>" for i in range(20)]) + "</div>"
    st.markdown(pulse_html, unsafe_allow_html=True)
    
    total_s = m * 60
    for i in range(total_s, -1, -1):
        mm, ss = divmod(i, 60)
        ph.markdown(f"<div class='timer-active'>{mm:02}:{ss:02}</div>", unsafe_allow_html=True)
        bar.progress(1.0 - (i/total_s))
        if i % 60 == 0 and i != total_s:
             q_box.info(quotes[(i//60) % len(quotes)])
        time.sleep(1)
    
    st.success("序列完成")
    data["history"].append({"項目": f"專注序列 {m}min", "日期": today, "類型": "精神強化"})
    add_xp(15)
    st.balloons()
"""
    }

# =========================================================
# 【核心邏輯系統】
# =========================================================

def load_data():
    defaults = {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": [], "dev_mode": True}
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
    nav = ["專注空間", "系統設定"]
    if data.get("dev_mode"): nav.append("開發者主機")
    page = st.radio("導覽", nav)

# --- 執行環境 ---
exec_env = {
    "st": st, "data": data, "time": time, "save_data": save_data, 
    "today": today, "pd": pd, "px": px, "add_xp": add_xp, "datetime": datetime, "divmod": divmod
}

# =========================================================
# 【安全渲染引擎】
# =========================================================

def safe_exec(target_key):
    code = st.session_state.code_store.get(target_key, "")
    try:
        # 清理轉義字元
        clean_code = code.replace('\\"', '"').replace("\\'", "'").strip()
        exec(clean_code, exec_env)
    except Exception as e:
        st.error(f"模組 {target_key} 執行失敗: {e}")

# --- 執行頁面 ---
if page == "專注空間":
    safe_exec("4_VOID")

elif page == "開發者主機":
    st.title("🛠 MODULAR ARCHITECT")
    target = st.selectbox("選擇編輯模組", list(st.session_state.code_store.keys()))
    st.session_state.code_store[target] = st.text_area("代碼編輯區", st.session_state.code_store[target], height=500)
    
    st.divider()
    
    # 這裡就是你找好久的導出按鈕！
    st.markdown("### 📦 系統導出序列")
    
    output = io.StringIO()
    # 寫入 Header
    output.write("import streamlit as st\nimport json, os, time\nimport pandas as pd\nimport plotly.express as px\nfrom datetime import datetime, timedelta\n\n")
    
    # 寫入各個模組
    for k in sorted(st.session_state.code_store.keys()):
        output.write(f"\n# --- MODULE: {k} ---\n")
        output.write(st.session_state.code_store[k] + "\n")
    
    st.download_button(
        label="💾 執行完整導出 (.py)",
        data=output.getvalue().encode('utf-8'),
        file_name="mono_os_final.py",
        mime="text/x-python",
        use_container_width=True
    )

elif page == "系統設定":
    st.title("SETTINGS")
    data["dev_mode"] = st.toggle("開發者模式", value=data.get("dev_mode", True))
    save_data(data)
