import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 0. 檔案定義 ---
DB_FILE = "mono_v4_data.json"

# --- 1. 頁面配置 ---
st.set_page_config(page_title="MONO // OS", layout="wide")

# --- 2. 極致黑化與佈局 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    
    /* 任務卡片樣式 */
    .protocol-card {
        background: linear-gradient(145deg, #0a0a0a, #050505);
        border: 1px solid #1a1a1a;
        border-left: 4px solid #fff;
        border-radius: 10px; padding: 20px; margin-bottom: 15px;
    }
    .scan-card {
        background: #050505; border: 1px solid #111;
        border-radius: 10px; padding: 15px; margin-bottom: 10px;
    }
    .done-status { opacity: 0.15; filter: blur(2px); transition: 0.5s; }
    
    /* XP 條系統 */
    .xp-bar { background: #111; border-radius: 5px; height: 4px; width: 100%; margin: 10px 0; }
    .xp-progress { background: #fff; height: 100%; border-radius: 5px; transition: 0.8s; box-shadow: 0 0 10px #fff; }
    
    /* 字體與標籤 */
    .mono-label { font-family: 'Courier New', monospace; font-size: 10px; color: #444; letter-spacing: 3px; }
    .stat-val { font-size: 24px; font-weight: 900; color: #fff; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料處理中心 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                d = json.load(f)
                # 補足結構
                defaults = {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": []}
                for k, v in defaults.items():
                    if k not in d: d[k] = v
                return d
            except: pass
    return {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": []}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 4. 側邊導航 ---
st.sidebar.title("MONO // OS")
page = st.sidebar.radio("系統接口", ["FLOW // 任務流", "NEURAL // 數據中心", "VOID // 專注時空", "ARCHIVE // 檔案庫", "SYSTEM // 設定"])

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

# ---------------------------------------------------------
# PAGE: FLOW // 任務流
# ---------------------------------------------------------
if page == "FLOW // 任務流":
    # 頂部狀態
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"<div class='mono-label'>SYSTEM_LEVEL: {data['level']}</div>", unsafe_allow_html=True)
        xp_pct = data["total_xp"] % 100
        st.markdown(f"<div class='xp-bar'><div class='xp-progress' style='width: {xp_pct}%;'></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align:right' class='mono-label'>{xp_pct}/100 XP</div>", unsafe_allow_html=True)

    # 整合新增區塊 (版面設計區分)
    st.write(" ")
    new_input = st.text_input("輸入新的指令...", placeholder="例如：每日冥想 或 買牛奶", label_visibility="collapsed")
    col_a, col_b = st.columns(2)
    if col_a.button("＋ 啟動核心協定 (每日任務/有XP)", use_container_width=True):
        if new_input:
            data["habits"].append({"name": new_input, "streak": 0, "last_done": ""})
            save_data(data); st.rerun()
    if col_b.button("＋ 執行臨時掃描 (一般任務/無XP)", use_container_width=True):
        if new_input:
            data["tasks"].append({"name": new_input})
            save_data(data); st.rerun()

    st.divider()

    # 佈局分左右兩欄顯示
    left, right = st.columns(2)

    with left:
        st.markdown("<div class='mono-label'>CORE PROTOCOLS</div>", unsafe_allow_html=True)
        for idx, h in enumerate(data["habits"]):
            is_done = (h["last_done"] == today)
            st.markdown(f"""
                <div class="protocol-card {'done-status' if is_done else ''}">
                    <div style="font-size:12px; color:#444">PROTOCOL_{idx:02} // 🔥 STREAK: {h['streak']}</div>
                    <div style="font-size:20px; font-weight:700">{h['name']}</div>
                </div>
            """, unsafe_allow_html=True)
            if not is_done:
                if st.button(f"執行完成_{idx}", key=f"hbtn_{idx}", use_container_width=True):
                    h["streak"] = h["streak"] + 1 if h["last_done"] == yesterday else 1
                    h["last_done"] = today
                    add_xp(25)
                    st.rerun()

    with right:
        st.markdown("<div class='mono-label'>TEMPORAL SCANS</div>", unsafe_allow_html=True)
        for idx, t in enumerate(data["tasks"]):
            st.markdown(f"""
                <div class="scan-card">
                    <div style="font-size:12px; color:#444">SCAN_JOB_{idx:02}</div>
                    <div style="font-size:18px;">{t['name']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"消除紀錄_{idx}", key=f"tbtn_{idx}", use_container_width=True):
                data["history"].append({"name": t["name"], "date": today, "type": "Scan"})
                data["tasks"].pop(idx)
                save_data(data); st.rerun()

# ---------------------------------------------------------
# PAGE: NEURAL // 數據中心
# ---------------------------------------------------------
elif page == "NEURAL // 數據中心":
    st.markdown("<div class='mono-label'>NEURAL_NETWORK_VISUALIZATION</div>", unsafe_allow_html=True)
    if not data["habits"]:
        st.info("等待協定數據輸入...")
    else:
        # 雷達圖
        names = [h['name'] for h in data['habits']]
        streaks = [h['streak'] for h in data['habits']]
        fig = go.Figure(data=go.Scatterpolar(r=streaks, theta=names, fill='toself', line=dict(color='#fff')))
        fig.update_layout(polar=dict(bgcolor="black", radialaxis=dict(visible=False)), paper_bgcolor="black", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PAGE: VOID // 專注時空 (番茄鐘)
# ---------------------------------------------------------
elif page == "VOID // 專注時空":
    st.markdown("<div class='mono-label'>FOCUS_TIMER // 25:00</div>", unsafe_allow_html=True)
    mins = st.number_input("設定分鐘", value=25)
    if st.button("啟動專注場"):
        ph = st.empty()
        for i in range(mins * 60, 0, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<div style='font-size:100px; text-align:center; font-family:monospace;'>{mm:02}:{ss:02}</div>", unsafe_allow_html=True)
            time.sleep(1)
        st.success("專注結束。獲得 5 XP")
        add_xp(5)

# ---------------------------------------------------------
# PAGE: ARCHIVE // 檔案庫
# ---------------------------------------------------------
elif page == "ARCHIVE // 檔案庫":
    st.markdown("<div class='mono-label'>MISSION_ARCHIVE</div>", unsafe_allow_html=True)
    if not data["history"]:
        st.write("檔案庫尚無紀錄。")
    else:
        df = pd.DataFrame(data["history"])
        st.table(df)

# ---------------------------------------------------------
# PAGE: SYSTEM // 設定
# ---------------------------------------------------------
elif page == "SYSTEM // 設定":
    st.markdown("<div class='mono-label'>SYSTEM_HARD_RESET</div>", unsafe_allow_html=True)
    if st.button("格式化所有數據"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()
