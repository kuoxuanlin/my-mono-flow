import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# --- 0. 基礎配置 ---
DB_FILE = "mono_v14_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【全頁面模組初始化】 - 修正引號轉義問題
# =========================================================

if 'code_store' not in st.session_state:
    st.session_state.code_store = {
        "1_GLOBAL": """
st.markdown('<style>.stApp { background-color: #000; color: #fff; } [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; } .header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; } .xp-bar { background: #111; border-radius: 50px; height: 10px; width: 100%; margin: 15px 0; overflow: hidden; } .xp-progress { background: #fff; height: 100%; box-shadow: 0 0 15px #fff; transition: 1s; }</style>', unsafe_allow_html=True)
""",
        "2_DASHBOARD": """
st.markdown('<style>.habit-card { background: linear-gradient(145deg, #0d0d0d, #050505); border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; margin-bottom: 12px; border-left: 5px solid #fff; } .task-card { background: #080808; border: 1px solid #151515; border-radius: 8px; padding: 12px; margin-bottom: 8px; } .done-blur { opacity: 0.3; filter: grayscale(100%); }</style>', unsafe_allow_html=True)
xp_pct = data['total_xp'] % 100
st.markdown(f"### LV.{data['level']} <span style='float:right; color:#666;'>{xp_pct}/100 XP</span>", unsafe_allow_html=True)
st.markdown(f'<div class="xp-bar"><div class="xp-progress" style="width:{xp_pct}%"></div></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns([4, 1.2, 0.8])
n_name = c1.text_input("任務", placeholder="輸入...", key="new_task", label_visibility="collapsed")
n_type = c2.segmented_control("類型", ["習慣", "任務"], default="習慣", label_visibility="collapsed")
if c3.button("＋啟動", use_container_width=True) and n_name:
    if n_type == "習慣": data["habits"].append({"name": n_name, "streak": 0, "last_done": ""})
    else: data["tasks"].append({"name": n_name})
    save_data(data); st.rerun()
l, r = st.columns([1.6, 1])
with l:
    st.markdown("<div class='header-tag'>// Protocols</div>", unsafe_allow_html=True)
    for idx, h in enumerate(data["habits"]):
        done = (h["last_done"] == today)
        st.markdown(f'<div class="habit-card {"done-blur" if done else ""}">{h["name"]} (Streak: {h["streak"]})</div>', unsafe_allow_html=True)
        if not done and st.button(f"簽到", key=f"h_{idx}"):
            h["streak"] = h["streak"] + 1 if h["last_done"] == yesterday else 1
            h["last_done"] = today
            add_xp(25); st.rerun()
with r:
    st.markdown("<div class='header-tag'>// Scans</div>", unsafe_allow_html=True)
    for idx, t in enumerate(data["tasks"]):
        st.markdown(f'<div class="task-card">{t["name"]}</div>', unsafe_allow_html=True)
        if st.button("✔", key=f"t_{idx}"):
            data["history"].append({"項目": t["name"], "日期": today, "類型": "任務"})
            data["tasks"].pop(idx); save_data(data); st.rerun()
""",
        "4_VOID": """
st.markdown('<style>@keyframes glow { 0% { text-shadow: 0 0 5px #fff; opacity: 0.8; } 50% { text-shadow: 0 0 20px #fff, 0 0 30px #fff; opacity: 1; } 100% { text-shadow: 0 0 5px #fff; opacity: 0.8; } } @keyframes pulse { 0%, 100% { height: 10px; opacity: 0.3; } 50% { height: 40px; opacity: 1; } } .timer-active { font-size: 100px; font-family: monospace; text-align: center; animation: glow 2s infinite ease-in-out; margin-bottom: 0; } .neural-container { display: flex; justify-content: center; align-items: flex-end; gap: 4px; height: 50px; margin: 20px 0; } .pulse-bar { width: 3px; background: #fff; animation: pulse 1.5s infinite ease-in-out; }</style>', unsafe_allow_html=True)
st.markdown("<div class='header-tag'>// 深度專注序列 NEURAL_VOID</div>", unsafe_allow_html=True)
quotes = ["靜默是最高級的運算。", "刪除雜訊，保留核心。", "專注是唯一的武裝。", "在代碼中尋找秩序。"]
m = st.slider("設定頻率時長 (MIN)", 5, 120, 25, 5)
if st.button("啟動專注序列", use_container_width=True):
    ph = st.empty(); bar = st.progress(0)
    q_box = st.info(quotes[int(time.time()) % len(quotes)])
    pulse_html = "<div class='neural-container'>" + "".join([f"<div class='pulse-bar' style='animation-delay: {0.1*i}s'></div>" for i in range(20)]) + "</div>"
    st.markdown(pulse_html, unsafe_allow_html=True)
    for i in range(m*60, -1, -1):
        mm, ss = divmod(i, 60)
        ph.markdown(f"<div class='timer-active'>{mm:02}:{ss:02}</div>", unsafe_allow_html=True)
        bar.progress(1.0 - (i/(m*60)))
        if i % 60 == 0 and i != 0: q_box.info(quotes[(i//60) % len(quotes)])
        time.sleep(1)
    st.success("完成"); add_xp(15); st.balloons()
"""
    }

# =========================================================
# 【核心邏輯系統】
# =========================================================

def load_data():
    defaults = {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": [], "dev_mode": False}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                d = json.load(f)
                for k, v in defaults.items():
                    if k not in d: d[k] = v
                return d
            except: return defaults
    return defaults

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 側邊欄 ---
with st.sidebar:
    st.title("MONO // OS")
    nav = ["儀錶板", "專注空間", "系統設定"]
    if data.get("dev_mode"): nav.append("開發者主機")
    page = st.radio("導覽", nav)

# --- 路由與全局樣式執行 ---
# 顯式傳遞全域變數給 exec
exec_globals = {"st": st, "data": data, "save_data": save_data, "add_xp": add_xp, "time": time, "today": today, "yesterday": yesterday}

# 執行全局樣式
if "1_GLOBAL" in st.session_state.code_store:
    exec(st.session_state.code_store["1_GLOBAL"], exec_globals)

if page == "儀錶板":
    exec(st.session_state.code_store["2_DASHBOARD"], exec_globals)

elif page == "專注空間":
    exec(st.session_state.code_store["4_VOID"], exec_globals)

elif page == "開發者主機":
    st.title("🛠 MODULAR ARCHITECT")
    target = st.selectbox("選擇模組", list(st.session_state.code_store.keys()))
    st.session_state.code_store[target] = st.text_area("代碼編輯", st.session_state.code_store[target], height=500)
    
    st.divider()
    
    # 導出邏輯
    output = io.StringIO()
    output.write("import streamlit as st\nimport json, os, time\nimport pandas as pd\nimport plotly.express as px\nfrom datetime import datetime, timedelta\n\n")
    for k in sorted(st.session_state.code_store.keys()):
        output.write(f"\n# --- MODULE: {k} ---\n")
        output.write(st.session_state.code_store[k] + "\n")
    
    st.download_button("📦 導出完整專案", data=output.getvalue().encode('utf-8'), file_name="mono_os_v14.py", mime="text/x-python")

elif page == "系統設定":
    st.title("SETTINGS")
    data["dev_mode"] = st.toggle("開發者模式", value=data.get("dev_mode", False))
    save_data(data)
