import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v7_data.json"
st.set_page_config(page_title="MONO // 自律 OS", layout="wide")

# =========================================================
# 【開發者專區：各模組原始碼節錄】
# =========================================================

def get_css_code():
    return """
/* 介面風格模組 */
<style>
.stApp { background-color: #000; color: #fff; }
[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
.habit-card {
    background: linear-gradient(145deg, #0d0d0d, #050505);
    border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; margin-bottom: 12px;
    border-left: 5px solid #fff; transition: 0.3s;
}
.task-card {
    background: #080808; border: 1px solid #151515;
    border-radius: 8px; padding: 12px; margin-bottom: 8px;
}
.xp-bar { background: #111; border-radius: 50px; height: 10px; width: 100%; margin: 15px 0; overflow: hidden; }
.xp-progress { background: #fff; height: 100%; box-shadow: 0 0 15px #fff; transition: 1s; }
.header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; }
</style>
"""

def get_dashboard_code():
    return """
# 頁面：儀錶板邏輯
xp_pct = data["total_xp"] % 100
st.markdown(f"LV.{data['level']} ...") # 渲染等級條

# 新增任務區
c1, c2, c3 = st.columns([4, 1, 1])
name = c1.text_input(...)
if c3.button("＋ 啟動"):
    # 邏輯判斷與存檔
"""

def get_analytics_code():
    return """
# 頁面：數據中心邏輯
df = pd.DataFrame(data["habits"])
fig = px.bar(df, x="streak", y="name", orientation='h', color_discrete_sequence=['#ffffff'])
st.plotly_chart(fig)
"""

# =========================================================
# 【核心系統邏輯】
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
st.markdown(get_css_code(), unsafe_allow_html=True)

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 側邊導航 ---
with st.sidebar:
    st.title("MONO // OS")
    nav = ["儀錶板", "數據中心", "專注空間", "成就檔案", "系統設定"]
    if data.get("dev_mode"): nav.append("開發者主機")
    page = st.radio("導覽指示", nav)

# ---------------------------------------------------------
# 1. 儀錶板 (DASHBOARD)
# ---------------------------------------------------------
if page == "儀錶板":
    xp_pct = data["total_xp"] % 100
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
            <span style='font-size: 45px; font-weight: 900; letter-spacing: -2px;'>LV.{data['level']}</span>
            <span style='font-family: monospace; color: #666;'>{xp_pct} / 100 XP</span>
        </div>
        <div class="xp-bar"><div class="xp-progress" style="width: {xp_pct}%;"></div></div>
    """, unsafe_allow_html=True)

    # 極簡新增區
    with st.container():
        c1, c2, c3 = st.columns([4, 1.2, 0.8])
        new_name = c1.text_input("任務名稱", placeholder="輸入新目標或習慣...", label_visibility="collapsed")
        new_type = c2.segmented_control("類別", ["習慣", "任務"], default="習慣", label_visibility="collapsed")
        if c3.button("＋ 啟動項目", use_container_width=True):
            if new_name:
                if new_type == "習慣": data["habits"].append({"name": new_name, "streak": 0, "last_done": ""})
                else: data["tasks"].append({"name": new_name})
                save_data(data); st.rerun()

    st.write(" ")
    l_col, r_col = st.columns([1.6, 1])

    with l_col:
        st.markdown("<div class='header-tag'>// 每日核心協定</div>", unsafe_allow_html=True)
        for idx, h in enumerate(data["habits"]):
            is_done = (h["last_done"] == today)
            st.markdown(f"""
                <div class="habit-card {'done-blur' if is_done else ''}">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <div style='font-size: 24px; font-weight: 800;'>{h['name']}</div>
                            <div style='font-size: 12px; color: #555; margin-top:4px;'>連勝紀錄：{h['streak']} DAY</div>
                        </div>
                        <div style='font-size: 28px; font-weight: 900; color: #1a1a1a;'>{idx:02}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if not is_done:
                if st.button(f"完成簽到", key=f"h_{idx}", use_container_width=True):
                    h["streak"] = h["streak"] + 1 if h["last_done"] == yesterday else 1
                    h["last_done"] = today
                    add_xp(25); st.rerun()

    with r_col:
        st.markdown("<div class='header-tag'>// 臨時掃描任務</div>", unsafe_allow_html=True)
        for idx, t in enumerate(data["tasks"]):
            tc1, tc2 = st.columns([4, 1])
            tc1.markdown(f'<div class="task-card">{t["name"]}</div>', unsafe_allow_html=True)
            if tc2.button("✔", key=f"t_{idx}", use_container_width=True):
                data["history"].append({"項目": t["name"], "日期": today, "類型": "任務"})
                data["tasks"].pop(idx); save_data(data); st.rerun()

# ---------------------------------------------------------
# 2. 開發者主機 (DEV WORKSTATION)
# ---------------------------------------------------------
elif page == "開發者主機":
    st.title("🛠 開發者代碼工作站")
    st.write("在此可以直接節錄各分頁程式碼，進行針對性修改後重新部署。")
    
    # 將每個部分分開展示，方便「直接修改」與複製
    dev_tabs = st.tabs(["[1] 介面風格 (CSS)", "[2] 儀錶板邏輯", "[3] 數據分析", "[4] 資料結構", "[5] 總導出"])
    
    with dev_tabs[0]:
        st.markdown("### 介面樣式 CSS")
        st.code(get_css_code(), language="css")
        
    with dev_tabs[1]:
        st.markdown("### 首頁儀錶板 Python 節錄")
        st.code(get_dashboard_code(), language="python")

    with dev_tabs[2]:
        st.markdown("### 數據中心 Python 節錄")
        st.code(get_analytics_code(), language="python")

    with dev_tabs[3]:
        st.markdown("### 當前 JSON 資料狀態")
        st.json(data)

    with dev_tabs[4]:
        st.markdown("### 📦 總程式碼備份與導出")
        # 建立一個包含所有資訊的導出
        export_text = f"#{'='*20}\n# MONO OS TOTAL EXPORT\n#{'='*20}\n"
        export_text += f"# DATE: {today}\n# DATA_COUNT: {len(data['habits'])} Habits\n\n"
        st.download_button("導出完整專案檔案 (.py)", data=export_text, file_name="mono_os_full.py", use_container_width=True)
        st.download_button("導出數據庫 (.json)", data=json.dumps(data, indent=4), file_name="mono_db.json", use_container_width=True)

# ---------------------------------------------------------
# 3. 其他頁面 (精簡呈現)
# ---------------------------------------------------------
elif page == "數據中心":
    st.title("數據可視化")
    if data["habits"]:
        df = pd.DataFrame(data["habits"])
        fig = px.bar(df, x="streak", y="name", orientation='h', color_discrete_sequence=['#ffffff'])
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("目前沒有數據可供分析。")

elif page == "專注空間":
    st.title("VOID計時器")
    m = st.number_input("設定分鐘", 1, 120, 25)
    if st.button("啟動專注序列", use_container_width=True):
        ph = st.empty()
        for i in range(m * 60, 0, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<h1 style='text-align:center; font-size:120px;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        st.balloons(); add_xp(15)

elif page == "成就檔案":
    st.title("達成紀錄庫")
    if data["history"]: st.table(pd.DataFrame(data["history"]))

elif page == "系統設定":
    st.title("系統核心設定")
    data["dev_mode"] = st.toggle("開啟開發者模式", value=data.get("dev_mode", False))
    save_data(data)
    st.divider()
    if st.button("格式化系統 (清空數據)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear(); st.rerun()
