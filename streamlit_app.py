import streamlit as st
import json, os, time, io
import pandas as pd
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v27_data.json"
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

# 這裡定義 save_data，等一下會注入到模組中
def save_data(data_to_save):
    with open(DB_FILE, "w") as f:
        json.dump(data_to_save, f)

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
        "4_VOID": """st.markdown("<div class='header-tag'>// NEURAL_VOID</div>", unsafe_allow_html=True)
m = st.slider("設定分鐘", 1, 120, 25)
if st.button("啟動專注", use_container_width=True):
    ph = st.empty()
    for i in range(m*60, -1, -1):
        mm, ss = divmod(i, 60)
        ph.markdown(f"<h1 style='text-align:center;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    data.setdefault('history', []).append({"date": today, "min": m})
    save_data(data) # 之前就是這裡報錯！
    st.success("完成")"""
    }

# --- 執行環境注入 (核心修正點) ---
# 我把 save_data 放進來了，這樣 4_VOID 就能抓到它了
exec_env = {
    "st": st, "data": data, "time": time, "today": today, 
    "pd": pd, "datetime": datetime, "divmod": divmod, 
    "save_data": save_data 
}

# =========================================================
# 【動態導航系統】
# =========================================================
st.sidebar.title("MONO // OS")

custom_pages = [k for k in st.session_state.code_store.keys() if k != "1_GLOBAL"]
system_pages = ["🛠 開發者主機", "⚙️ 系統設定"]
nav_options = custom_pages + system_pages

page = st.sidebar.radio("導航路徑", nav_options)

def run_mod(key):
    code = st.session_state.code_store.get(key, "")
    try:
        # 使用 strip() 確保不會因為空格導致語法錯誤
        exec(code.strip(), exec_env)
    except Exception as e:
        st.error(f"模組 {key} 執行失敗: {e}")

# 渲染全局樣式
run_mod("1_GLOBAL")

# --- 分頁路由 ---
if page == "🛠 開發者主機":
    st.title("🛠 DEVELOPER CONSOLE")
    
    # 新增頁面
    with st.expander("➕ 新增功能頁面"):
        new_page_id = st.text_input("頁面 ID", placeholder="例如: 5_LOG")
        if st.button("創建新分頁"):
            if new_page_id and new_page_id not in st.session_state.code_store:
                st.session_state.code_store[new_page_id] = "st.title('新分頁')\\nst.write('編輯這裡...')"
                st.rerun()

    # 編輯功能
    target = st.selectbox("選擇要編輯的模組", list(st.session_state.code_store.keys()))
    current_code = st.text_area("代碼編輯區", st.session_state.code_store[target], height=400)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 儲存並同步網站", use_container_width=True):
            st.session_state.code_store[target] = current_code
            st.success("核心同步成功！")
            time.sleep(0.5)
            st.rerun()
    with col2:
        if st.button("🗑 刪除此模組", use_container_width=True):
            if target not in ["1_GLOBAL", "4_VOID"]:
                del st.session_state.code_store[target]
                st.rerun()

elif page == "⚙️ 系統設定":
    st.title("SETTINGS")
    if st.button("🚨 重置系統數據"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.data = {"habits":[], "tasks":[], "total_xp":0, "level":1, "history":[], "dev_mode":True}
        st.rerun()

else:
    # 執行自定義分頁
    run_mod(page)
