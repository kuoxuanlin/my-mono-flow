import streamlit as st
import json, os, time, io
import pandas as pd
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v25_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【核心倉庫】
# =========================================================
if 'code_store' not in st.session_state:
    st.session_state.code_store = {
        "1_GLOBAL": """st.markdown('<style>.stApp{background:#000;color:#fff;} .header-tag{color:#444;letter-spacing:4px;font-size:10px;}</style>', unsafe_allow_html=True)""",
        
        "4_VOID": """st.markdown("<div class='header-tag'>// NEURAL_VOID</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1,2,1])
with c1:
    st.metric("等級", f"LV.{data.get('level', 1)}")
with c3:
    st.metric("總經驗值", data.get('total_xp', 0))
with c2:
    m = st.slider("設定時間 (MIN)", 1, 120, 25)
    if st.button("啟動專注序列", use_container_width=True):
        ph = st.empty()
        for i in range(m*60, -1, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<h1 style='text-align:center; font-size:80px; font-family:monospace;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        if 'history' not in data: data['history'] = []
        data['history'].append({"date": today, "min": m})
        add_xp(15)
        st.success("專注序列完成")
        st.balloons()"""
    }

# =========================================================
# 【持久化邏輯】
# =========================================================
def load_data():
    defaults = {"habits":[], "tasks":[], "total_xp":0, "level":1, "history":[], "dev_mode":True}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: 
                d = json.load(f)
                for k, v in defaults.items():
                    if k not in d: d[k] = v
                return d
        except: return defaults
    return defaults

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    with open(DB_FILE, "w") as f: json.dump(data, f)

# 注入環境
exec_env = {"st": st, "data": data, "time": time, "add_xp": add_xp, "today": today, "pd": pd, "datetime": datetime, "divmod": divmod}

# --- 側邊欄 ---
st.sidebar.title("MONO // OS")
page = st.sidebar.radio("系統導航", ["專注空間", "開發者主機", "系統設定"])

# =========================================================
# 【執行引擎】
# =========================================================
def run_mod(key):
    if 'code_store' not in st.session_state: return
    code = st.session_state.code_store.get(key, "")
    try:
        # 清理可能導致錯誤的轉義，保持純淨
        exec(code.strip(), exec_env)
    except Exception as e:
        st.error(f"模組 {key} 執行失敗: {e}")

# 渲染全局樣式
run_mod("1_GLOBAL")

if page == "專注空間":
    run_mod("4_VOID")

elif page == "開發者主機":
    st.title("🛠 MODULAR ARCHITECT")
    mod = st.selectbox("模組編輯選擇", list(st.session_state.code_store.keys()))
    st.session_state.code_store[mod] = st.text_area("代碼編輯區", st.session_state.code_store[mod], height=400)
    
    st.divider()
    if st.button("📦 產生穩定導出版"):
        # 1. 數據修正 (關鍵：確保 True 為大寫)
        data_fix = str(data)
        
        # 2. 構建導出腳本內容
        raw_code = [
            "import streamlit as st, json, os, time, pandas as pd",
            "from datetime import datetime",
            "",
            f"data = {data_fix}",
            "today = datetime.now().strftime('%Y-%m-%d')",
            "def add_xp(a): data['total_xp']+=a; data['level']=(data['total_xp']//100)+1",
            "exec_env = {'st':st, 'data':data, 'time':time, 'add_xp':add_xp, 'today':today, 'divmod':divmod}",
            "",
            "st.sidebar.title('MONO // OS (STABLE)')",
            "page = st.sidebar.radio('NAV', ['HOME'])",
            ""
        ]
        
        for k, v in st.session_state.code_store.items():
            # 使用 r''' 包裹，徹底解決反斜線和換行報錯
            raw_code.append(f"\n# --- {k} ---")
            raw_code.append(f"code_{k} = r'''{v}'''")
            raw_code.append(f"if page == 'HOME' or '{k}' == '1_GLOBAL': exec(code_{k}.strip(), exec_env)")

        final_script = "\n".join(raw_code)
        
        st.download_button(
            label="💾 下載修正後 .py (UTF-8)", 
            data=final_script.encode('utf-8'), 
            file_name="mono_os_fixed.py", 
            mime="text/x-python",
            use_container_width=True
        )

elif page == "系統設定":
    st.title("SETTINGS")
    if st.button("🚨 數據清除重置"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()
