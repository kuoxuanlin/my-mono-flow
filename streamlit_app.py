import streamlit as st
import json, os, time, io
import pandas as pd
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v26_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【數據持久化】
# =========================================================
def load_data():
    defaults = {"habits":[], "tasks":[], "total_xp":0, "level":1, "history":[], "dev_mode":True}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return defaults
    return defaults

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(f, data)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")

# =========================================================
# 【模組倉庫】
# =========================================================
if 'code_store' not in st.session_state:
    st.session_state.code_store = {
        "1_GLOBAL": """st.markdown('<style>.stApp{background:#000;color:#fff;} .header-tag{color:#444;letter-spacing:4px;font-size:10px;}</style>', unsafe_allow_html=True)""",
        
        "4_VOID": """st.markdown("<div class='header-tag'>// NEURAL_VOID_MINIMAL</div>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 3])
with c1:
    st.caption("專注日誌")
    history = data.get('history', [])[-8:]
    for log in reversed(history):
        st.write(f"● {log['min']}m")
with c2:
    m = st.slider("設定分鐘", 1, 120, 25)
    if st.button("啟動專注序列", use_container_width=True):
        ph = st.empty()
        for i in range(m*60, -1, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<h1 style='text-align:center; font-size:100px;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        data.setdefault('history', []).append({"date": today, "min": m})
        st.success("專注完成")
        st.balloons()"""
    }

# --- 執行環境 ---
def add_xp(a): 
    data['total_xp']+=a
    data['level']=(data['total_xp']//100)+1

exec_env = {"st": st, "data": data, "time": time, "today": today, "add_xp": add_xp, "save_data": save_data, "divmod": divmod}

# =========================================================
# 【導航系統】
# =========================================================
st.sidebar.title("MONO // OS")
# 強制列出所有頁面
nav_options = ["專注空間", "開發者主機", "系統設定"]
page = st.sidebar.radio("系統導航", nav_options)

def run_mod(key):
    code = st.session_state.code_store.get(key, "")
    try:
        exec(code, exec_env)
    except Exception as e:
        st.error(f"模組 {key} 報錯: {e}")

# 渲染全局
run_mod("1_GLOBAL")

# --- 分頁邏輯 ---
if page == "專注空間":
    run_mod("4_VOID")

elif page == "開發者主機":
    st.title("🛠 DEVELOPER CONSOLE")
    target = st.selectbox("模組編輯", list(st.session_state.code_store.keys()))
    st.session_state.code_store[target] = st.text_area("編輯區", st.session_state.code_store[target], height=400)
    
    st.divider()
    if st.button("📦 穩定版導出"):
        # 數據與布林值強化處理
        d_str = str(data)
        out = [
            "import streamlit as st, json, os, time",
            f"data = {d_str}",
            "today = '" + today + "'",
            "exec_env = {'st':st, 'data':data, 'time':time, 'today':today, 'divmod':divmod}",
            "st.sidebar.title('MONO OS')",
            "p = st.sidebar.radio('NAV', ['專注空間'])"
        ]
        for k, v in st.session_state.code_store.items():
            out.append(f"code_{k} = r'''{v}'''")
            out.append(f"if p == '專注空間' or '{k}' == '1_GLOBAL': exec(code_{k}, exec_env)")
        
        st.download_button("💾 下載檔案", "\n".join(out).encode('utf-8'), "mono_final.py")

elif page == "系統設定":
    st.title("SETTINGS")
    if st.button("🚨 重置系統數據"):
        st.session_state.data = {"habits":[], "tasks":[], "total_xp":0, "level":1, "history":[], "dev_mode":True}
        st.rerun()
