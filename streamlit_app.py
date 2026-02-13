import streamlit as st
import json
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 頁面配置 ---
st.set_page_config(page_title="MONO // 系統", layout="wide")

# --- 進階黑化 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    
    /* 卡片設計 */
    .task-card {
        background: #0a0a0a; border: 1px solid #111;
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        transition: 0.3s;
    }
    .done-task { opacity: 0.2; filter: blur(2px); }
    
    /* XP 條 */
    .xp-bar { background: #111; border-radius: 10px; height: 6px; width: 100%; margin: 10px 0; }
    .xp-progress { background: #fff; height: 100%; border-radius: 10px; transition: 0.8s; }
    
    /* 文字樣式 */
    .label { font-size: 10px; color: #444; letter-spacing: 2px; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

# --- 資料邏輯 (請將這段完整覆蓋原本的 load_data) ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                existing_data = json.load(f)
                # 這幾行是關鍵：確保新舊功能標籤都存在
                if "habits" not in existing_data: existing_data["habits"] = []
                if "tasks" not in existing_data: existing_data["tasks"] = []
                if "total_xp" not in existing_data: existing_data["total_xp"] = 0
                if "level" not in existing_data: existing_data["level"] = 1
                return existing_data
            except:
                # 如果檔案壞了，就回傳一個全新的結構
                return {"habits": [], "tasks": [], "total_xp": 0, "level": 1}
    return {"habits": [], "tasks": [], "total_xp": 0, "level": 1}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 側邊欄 ---
st.sidebar.title("MONO // 核心")
page = st.sidebar.radio("導覽", ["任務流", "數據庫", "榮譽殿堂"])

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

# ---------------------------------------------------------
# 頁面：任務流 (FLOW)
# ---------------------------------------------------------
if page == "任務流":
    st.subheader("任務控制台")
    
    # 頂部狀態欄
    current_xp = data["total_xp"] % 100
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; font-size: 12px;'>
            <span>等級 {data['level']}</span>
            <span>{current_xp} / 100 XP</span>
        </div>
        <div class="xp-bar"><div class="xp-progress" style="width: {current_xp}%;"></div></div>
    """, unsafe_allow_html=True)

    # 整合新增任務區塊
    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        new_name = c1.text_input("", placeholder="輸入任務或習慣名稱...", label_visibility="collapsed")
        is_habit = c2.selectbox("", ["每日習慣", "一般任務"], label_visibility="collapsed")
        if c3.button("新增項目", use_container_width=True):
            if new_name:
                if is_habit == "每日習慣":
                    data["habits"].append({"name": new_name, "streak": 0, "last_done": ""})
                else:
                    data["tasks"].append({"name": new_name, "status": "active"})
                save_data(data)
                st.rerun()

    st.divider()

    # 顯示每日習慣
    if data["habits"]:
        st.markdown("<div class='label'>每日習慣 // HABITS</div>", unsafe_allow_html=True)
        for idx, habit in enumerate(data["habits"]):
            is_done = (habit.get("last_done") == today)
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"""
                    <div class="task-card {'done-task' if is_done else ''}">
                        <div style="font-size: 18px; font-weight: 700;">{habit['name']}</div>
                        <div style="font-size: 10px; color: #888;">🔥 連勝: {habit['streak']} 天</div>
                    </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.write("")
                if st.button("完成", key=f"h_{idx}", disabled=is_done, use_container_width=True):
                    if habit["last_done"] == yesterday:
                        habit["streak"] += 1
                    elif habit["last_done"] != today:
                        habit["streak"] = 1
                    habit["last_done"] = today
                    add_xp(20)
                    st.rerun()

    # 顯示一般任務
    if data["tasks"]:
        st.markdown("<div class='label' style='margin-top:20px;'>一次性任務 // TASKS</div>", unsafe_allow_html=True)
        for idx, task in enumerate(data["tasks"]):
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"""<div class="task-card"><div style="font-size: 18px;">{task['name']}</div></div>""", unsafe_allow_html=True)
            with cols[1]:
                st.write("")
                if st.button("結案", key=f"t_{idx}", use_container_width=True):
                    data["tasks"].pop(idx)
                    add_xp(10)
                    save_data(data)
                    st.rerun()

# ---------------------------------------------------------
# 頁面：數據庫 (DATA)
# ---------------------------------------------------------
elif page == "數據庫":
    st.title("數據視覺化")
    
    if not data["habits"]:
        st.warning("尚無習慣數據可分析。")
    else:
        # 使用雷達圖替代長條圖
        categories = [h['name'] for h in data['habits']]
        values = [h['streak'] for h in data['habits']]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='連勝分佈',
            line=dict(color='white')
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="black",
                radialaxis=dict(visible=True, range=[0, max(values)+1 if values else 10], color="#444"),
                angularaxis=dict(color="white")
            ),
            showlegend=False,
            paper_bgcolor="black"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric("總經驗值", f"{data['total_xp']} XP")

# ---------------------------------------------------------
# 頁面：榮譽殿堂 (RANK)
# ---------------------------------------------------------
elif page == "榮譽殿堂":
    max_s = max([h["streak"] for h in data["habits"]]) if data["habits"] else 0
    rank = "初心者"
    if max_s > 30: rank = "時間領主"
    elif max_s > 14: rank = "自律職人"
    elif max_s > 7: rank = "執行者"
    
    st.markdown(f"""
        <div style="text-align: center; padding: 100px 0;">
            <div class="label">當前稱號</div>
            <div style="font-size: 70px; font-weight: 900; text-shadow: 0 0 30px rgba(255,255,255,0.2);">{rank}</div>
            <div style="color: #444; margin-top: 20px;">最高連勝紀錄：{max_s} 天</div>
        </div>
    """, unsafe_allow_html=True)

