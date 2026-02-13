import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v6_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# --- 1. 介面風格模塊 (CSS) ---
def get_css():
    return """
    <style>
    .stApp { background-color: #000; color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    
    /* 核心卡片設計 */
    .habit-card {
        background: linear-gradient(145deg, #0d0d0d, #050505);
        border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; margin-bottom: 12px;
        border-left: 5px solid #fff; transition: 0.3s;
    }
    .task-card {
        background: #080808; border: 1px solid #151515;
        border-radius: 8px; padding: 12px; margin-bottom: 8px;
    }
    .done-blur { opacity: 0.15; filter: grayscale(100%) blur(1px); }
    
    /* XP 進度條 */
    .xp-bar { background: #111; border-radius: 50px; height: 10px; width: 100%; margin: 15px 0; overflow: hidden; }
    .xp-progress { background: #fff; height: 100%; box-shadow: 0 0 15px #fff; transition: 1s; }
    
    /* 字體與標題 */
    .header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; }
    .stat-text { font-family: 'Courier New', monospace; }
    
    /* 極簡輸入框 */
    .stTextInput input { background-color: #0a0a0a !important; border: 1px solid #222 !important; color: white !important; }
    </style>
    """

# --- 2. 資料持久化 ---
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
st.markdown(get_css(), unsafe_allow_html=True)

# --- 3. 核心邏輯 ---
def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 4. 側邊導航 ---
with st.sidebar:
    st.title("MONO // 系統")
    nav_options = ["儀錶板", "數據中心", "專注空間", "成就檔案", "系統設定"]
    if data.get("dev_mode"):
        nav_options.append("開發者主機")
    page = st.radio("導覽", nav_options)

# ---------------------------------------------------------
# 頁面：儀錶板 (DASHBOARD)
# ---------------------------------------------------------
if page == "儀錶板":
    # 狀態列
    xp_pct = data["total_xp"] % 100
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
            <span style='font-size: 45px; font-weight: 900; letter-spacing: -2px;'>LV.{data['level']}</span>
            <span class='stat-text' style='color: #666;'>{xp_pct} / 100 XP</span>
        </div>
        <div class="xp-bar"><div class="xp-progress" style="width: {xp_pct}%;"></div></div>
    """, unsafe_allow_html=True)

    # 首頁極簡新增 (水平配置)
    with st.container():
        c1, c2, c3 = st.columns([4, 1, 1])
        new_name = c1.text_input("任務名稱", placeholder="輸入新目標...", label_visibility="collapsed")
        new_type = c2.selectbox("類型", ["每日習慣", "一般任務"], label_visibility="collapsed")
        if c3.button("＋ 啟動項目", use_container_width=True):
            if new_name:
                if new_type == "每日習慣": data["habits"].append({"name": new_name, "streak": 0, "last_done": ""})
                else: data["tasks"].append({"name": new_name})
                save_data(data); st.rerun()

    st.write(" ")
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown("<div class='header-tag'>// 核心習慣 PROTOCOLS</div>", unsafe_allow_html=True)
        for idx, h in enumerate(data["habits"]):
            is_done = (h["last_done"] == today)
            st.markdown(f"""
                <div class="habit-card {'done-blur' if is_done else ''}">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <div style='font-size: 22px; font-weight: 700;'>{h['name']}</div>
                            <div style='font-size: 11px; color: #555; margin-top:5px;'>連勝次數：{h['streak']} 天</div>
                        </div>
                        <div style='font-family: monospace; font-size: 20px; color: #444;'>#0{idx}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if not is_done:
                if st.button(f"完成紀錄", key=f"h_{idx}", use_container_width=True):
                    h["streak"] = h["streak"] + 1 if h["last_done"] == yesterday else 1
                    h["last_done"] = today
                    add_xp(25); st.rerun()

    with col_right:
        st.markdown("<div class='header-tag'>// 臨時掃描 SCANS</div>", unsafe_allow_html=True)
        for idx, t in enumerate(data["tasks"]):
            tc1, tc2 = st.columns([4, 1])
            tc1.markdown(f'<div class="task-card">{t["name"]}</div>', unsafe_allow_html=True)
            if tc2.button("✔", key=f"t_{idx}", use_container_width=True):
                data["history"].append({"項目": t["name"], "日期": today, "類型": "任務"})
                data["tasks"].pop(idx); save_data(data); st.rerun()

# ---------------------------------------------------------
# 頁面：開發者主機 (DEV CONSOLE)
# ---------------------------------------------------------
elif page == "開發者主機":
    st.title("🛠 開發者控制台")
    st.write("在此可以檢視各模塊原始碼，或導出完整專案。")
    
    # 模組化顯示程式碼
    dev_tabs = st.tabs(["樣式模塊 (CSS)", "首頁邏輯 (Home)", "數據邏輯 (Data)", "導出專案 (Export)"])
    
    with dev_tabs[0]:
        st.code(get_css(), language="css")
        
    with dev_tabs[1]:
        st.code("""
# Dashboard Logic Fragment
col_left, col_right = st.columns([1.5, 1])
with col_left:
    # Render Habits...
with col_right:
    # Render Tasks...
        """, language="python")

    with dev_tabs[2]:
        st.info("目前的資料結構 JSON")
        st.json(data)

    with dev_tabs[3]:
        st.markdown("### 📦 完整程式碼導出")
        full_code = f"""import streamlit as st\nimport json\n# ... (完整代碼)\n# 目前數據狀況: {len(data['habits'])} 習慣"""
        st.download_button("下載完整 .py 檔案", data=full_code, file_name="mono_os_export.py", use_container_width=True)
        st.download_button("下載資料庫 .json", data=json.dumps(data, indent=4), file_name="mono_db.json", use_container_width=True)

# ---------------------------------------------------------
# 頁面：數據中心
# ---------------------------------------------------------
elif page == "數據中心":
    st.title("數據可視化")
    if data["habits"]:
        df = pd.DataFrame(data["habits"])
        fig = px.bar(df, x="streak", y="name", orientation='h', 
                     color_discrete_sequence=['#ffffff'], title="習慣達成分布")
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("尚無足夠數據。")

# ---------------------------------------------------------
# 頁面：專注空間
# ---------------------------------------------------------
elif page == "專注空間":
    st.title("專注倒數")
    m = st.number_input("設定分鐘", 1, 120, 25)
    if st.button("啟動專注序列"):
        ph = st.empty()
        for i in range(m * 60, 0, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<h1 style='text-align:center;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        st.success("專注完成，獲得 15 XP")
        add_xp(15)

# ---------------------------------------------------------
# 頁面：系統設定
# ---------------------------------------------------------
elif page == "系統設定":
    st.title("系統設定")
    data["dev_mode"] = st.checkbox("開啟開發者模式", value=data.get("dev_mode", False))
    save_data(data)
    
    st.divider()
    if st.button("清空所有數據 (格式化)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear(); st.rerun()

elif page == "成就檔案":
    st.title("完成紀錄")
    if data["history"]:
        st.table(pd.DataFrame(data["history"]))
