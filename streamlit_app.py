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
        "4_VOID": """st.title("專注空間")\\nst.write("這是預設頁面，請在開發者主機修改內容。")"""
    }

# --- 執行環境注入 ---
exec_env = {
    "st": st, "data": data, "time": time, "today": today, 
    "pd": pd, "datetime": datetime, "divmod": divmod
}

# =========================================================
# 【動態導航系統】
# =========================================================
st.sidebar.title("MONO // OS")

# 1. 取得所有自定義模組（排除 GLOBAL 樣式）
custom_pages = [k for k in st.session_state.code_store.keys() if k != "1_GLOBAL"]
# 2. 合併系統內建頁面
system_pages = ["🛠 開發者主機", "⚙️ 系統設定"]
nav_options = custom_pages + system_pages

page = st.sidebar.radio("導航路徑", nav_options)

def run_mod(key):
    code = st.session_state.code_store.get(key, "")
    try:
        exec(code, exec_env)
    except Exception as e:
        st.error(f"模組 {key} 執行失敗: {e}")

# 渲染全局樣式
run_mod("1_GLOBAL")

# --- 分頁路由 ---
if page == "🛠 開發者主機":
    st.title("🛠 DEVELOPER CONSOLE")
    
    # 新增頁面功能
    with st.expander("➕ 新增功能頁面"):
        new_page_id = st.text_input("頁面 ID (例如: 5_TASK, 6_DATA)", placeholder="不要有空格")
        if st.button("創建新分頁"):
            if new_page_id and new_page_id not in st.session_state.code_store:
                st.session_state.code_store[new_page_id] = "# 新頁面模板\\nst.title('新分頁')\\nst.write('開始編輯吧！')"
                st.rerun()

    # 編輯功能
    target = st.selectbox("選擇要編輯的模組", list(st.session_state.code_store.keys()))
    current_code = st.text_area("代碼編輯區", st.session_state.code_store[target], height=400)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 儲存並立即更新網站", use_container_width=True):
            st.session_state.code_store[target] = current_code
            st.success("核心已同步！")
            time.sleep(0.5)
            st.rerun()
    with col2:
        if st.button("🗑 刪除此模組", use_container_width=True):
            if target not in ["1_GLOBAL", "4_VOID"]:
                del st.session_state.code_store[target]
                st.rerun()

    st.divider()
    # 導出邏輯
    if st.button("📦 產生穩定版導出"):
        d_str = str(data)
        out = ["import streamlit as st, json, os, time", f"data = {d_str}", "today = '" + today + "'", "exec_env = {'st':st, 'data':data, 'time':time, 'today':today, 'divmod':divmod}"]
        for k, v in st.session_state.code_store.items():
            out.append(f"code_{k} = r'''{v}'''")
            out.append(f"exec(code_{k}, exec_env)")
        st.download_button("💾 下載檔案", "\n".join(out).encode('utf-8'), "mono_final.py")

elif page == "⚙️ 系統設定":
    st.title("SETTINGS")
    if st.button("🚨 重置系統數據"):
        st.session_state.data = {"habits":[], "tasks":[], "total_xp":0, "level":1, "history":[], "dev_mode":True}
        st.rerun()

else:
    # 只要選到的是 code_store 裡的 key，就直接執行
    run_mod(page)
