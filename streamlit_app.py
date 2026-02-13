import streamlit as st
import json, os, time, io
import pandas as pd
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v20_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【模組倉庫】
# =========================================================
if 'code_store' not in st.session_state:
    st.session_state.code_store = {
        "1_GLOBAL": "st.markdown('<style>.stApp{background:#000;color:#fff;} .header-tag{color:#444;letter-spacing:4px;font-size:10px;}</style>', unsafe_allow_html=True)",
        
        "4_VOID": """st.markdown("<div class='header-tag'>// NEURAL_VOID</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,2,1])
with c1:
    st.metric("等級", f"LV.{data.get('level', 1)}")
with c2:
    m = st.slider("分鐘", 1, 120, 25)
    if st.button("啟動序列", use_container_width=True):
        ph = st.empty()
        for i in range(m*60, -1, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<h1 style='text-align:center;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        add_xp(15)
        st.success("完成")"""
    }

# =========================================================
# 【核心邏輯】
# =========================================================
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: pass
    return {"habits":[], "tasks":[], "total_xp":0, "level":1, "history":[], "dev_mode":True}

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    with open(DB_FILE, "w") as f: json.dump(data, f)

exec_env = {"st": st, "data": data, "time": time, "add_xp": add_xp, "today": today, "pd": pd, "datetime": datetime, "divmod": divmod}

# --- 側邊欄 ---
with st.sidebar:
    st.title("MONO // OS")
    nav = ["專注空間", "系統設定"]
    if data.get("dev_mode"): nav.append("開發者主機")
    page = st.radio("導覽", nav)

# =========================================================
# 【渲染引擎】
# =========================================================
def run_mod(key):
    code = st.session_state.code_store.get(key, "")
    try:
        exec(code, exec_env)
    except Exception as e:
        st.error(f"模組 {key} 報錯: {e}")

run_mod("1_GLOBAL")

if page == "專注空間":
    run_mod("4_VOID")

elif page == "開發者主機":
    st.title("🛠 DEVELOPER CONSOLE")
    mod = st.selectbox("選擇模組", list(st.session_state.code_store.keys()))
    st.session_state.code_store[mod] = st.text_area("代碼編輯", st.session_state.code_store[mod], height=400)
    
    st.divider()
    if st.button("📦 執行系統導出"):
        # --- 暴力解決導出換行問題 ---
        lines = [
            "import streamlit as st",
            "import json, os, time, io",
            "import pandas as pd",
            "from datetime import datetime, timedelta",
            "",
            f"data = {json.dumps(data)}",
            ""
        ]
        for k, v in st.session_state.code_store.items():
            lines.append(f"\n# --- {k} ---")
            lines.append(v)
        
        final_code = "\n".join(lines)
        # 強制使用二進位寫入，防止任何系統層級的轉義
        st.download_button(
            label="💾 下載修正檔案 (UTF-8)", 
            data=final_code.encode('utf-8'), 
            file_name="mono_os_fixed.py", 
            mime="text/x-python"
        )

elif page == "系統設定":
    data["dev_mode"] = st.toggle("開發者模式", value=data.get("dev_mode", True))
    if st.button("儲存並重新整理"): 
        with open(DB_FILE, "w") as f: json.dump(data, f)
        st.rerun()
