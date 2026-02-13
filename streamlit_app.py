import streamlit as st
import json
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 0. 檔案與環境定義 ---
DB_FILE = "mono_v3_data.json"

# --- 1. 頁面配置 ---
st.set_page_config(page_title="MONO // 系統", layout="wide")

# --- 2. 進階黑化 CSS ---
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
    .done-task { opacity: 0.2; filter: blur(3px); }
    
    /* XP 條 */
    .xp-bar { background: #111; border-radius: 10px; height: 6px; width: 100%; margin: 10px 0; }
    .xp-progress { background: #fff; height: 100%; border-radius: 10px; transition: 0.8s; }
    
    /* 文字樣式 */
    .label { font-size: 10px; color: #444; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
    
    /* 調整輸入框樣式 */
    .stTextInput > div > div > input { background-color: #0a0a0a; color: white; border: 1px solid #222; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料邏輯 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                existing_data = json.load(f)
                # 自動修復舊結構缺失的標籤
                if "habits" not in existing_data: existing_data["habits"] = []
                if "tasks" not in existing_data: existing_data["tasks"] = []
                if "total_xp" not in existing_data: existing_data["total_xp"] = 0
                if "level" not in existing_data: existing_data["level"] = 1
                return existing_data
            except:
                return {"habits": [], "tasks": [], "total_xp": 0, "level": 1}
    return {"habits": [], "tasks": [], "total_xp": 0, "level": 1}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# 初始化狀態
if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 4. 側邊欄 ---
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
    
    # 頂部狀態欄 (XP 進度條)
    current_xp = data["total_xp"] % 100
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; font-size: 12px; color: #888;'>
            <span>等級 {data['level']}</span>
            <span>{current_xp} / 100 XP</span>
        </div>
        <div class="xp-bar"><div class="xp-progress" style="width: {current_xp}%;"></div></div>
    """, unsafe_allow_html=True)

    # 整合新增項目區塊
    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        new_name = c1.text_input("項目名稱", placeholder="輸入任務或習慣...", label_visibility="collapsed")
        is_habit = c2.selectbox("類型", ["每日習慣", "一般任務"], label_visibility="collapsed")
        if c3.button("＋ 新增項目", use_container_width=True):
            if new_name:
                if is_habit == "每日習慣":
                    data["habits"].append({"name": new_name, "streak": 0, "last_done": ""})
                else:
                    data["tasks"].append({"name": new_name, "status": "active"})
                save_data(data)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 顯示每日習慣 (Habits)
    if data["habits"]:
        st.markdown("<div class='label'>每日習慣 // HABITS</div>", unsafe_allow_html=True)
        for idx, habit in enumerate(data["habits"]):
            is_done = (habit.get("last_done") == today)
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"""
                    <div class="task-card {'done-task' if is_done else ''}">
                        <div style="font-size: 18px; font-weight: 700;">{habit['name']}</div>
                        <div style="font-size: 11px; color: #555; margin-top: 5px;">🔥 連勝天數: {habit['streak']}</div>
                    </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.write("") # 垂直對齊調整
                btn_label = "已完成" if is_done else "完成"
                if st.button(btn_label, key=f"h_{idx}", disabled=is_done, use_container_width=True):
                    # 連勝判斷
                    if habit["last_done"] == yesterday:
                        habit["streak"] += 1
                    elif habit["last_done"] != today:
                        habit["streak"] = 1
                    habit["last_done"] = today
                    add_xp(20)
                    st.rerun()

    # 顯示一般任務 (Tasks)
    if data["tasks"]:
        st.markdown("<div class='label' style='margin-top:20px;'>單次任務 // TASKS</div>", unsafe_allow_html=True)
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

    # 系統清理 (隱藏在底部)
    with st.expander("進階管理"):
        if st.button("清除所有數據 (不可還原)"):
            data = {"habits": [], "tasks": [], "total_xp": 0, "level": 1}
            save_data(data)
            st.rerun()

# ---------------------------------------------------------
# 頁面：數據庫 (DATA)
# ---------------------------------------------------------
elif page == "數據庫":
    st.title("核心 // 數據分析")
    
    if not data["habits"]:
        st.info("尚無足夠數據生成雷達圖。請先新增每日習慣。")
    else:
        # 使用雷達圖呈現
        categories = [h['name'] for h in data['habits']]
        values = [h['streak'] for h in data['habits']]
        
        # 為了讓雷達圖閉合，重複第一個元素
        r_values = values + [values[0]]
        theta_cats = categories + [categories[0]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=r_values,
            theta=theta_cats,
            fill='toself',
            name='連勝分佈',
            line=dict(color='white', width=2),
            fillcolor='rgba(255, 255, 255, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, max(values)+2 if values else 10], 
                              color="#444", gridcolor="#222", showticklabels=False),
                angularaxis=dict(color="white", gridcolor="#222")
            ),
            showlegend=False,
            paper_bgcolor="black",
            plot_bgcolor="black",
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("總累計經驗", f"{data['total_xp']} XP")
        c2.metric("目前等級", f"LV. {data['level']}")

# ---------------------------------------------------------
# 頁面：榮譽殿堂 (RANK)
# ---------------------------------------------------------
elif page == "榮譽殿堂":
    max_s = max([h["streak"] for h in data["habits"]]) if data["habits"] else 0
    
    # 稱號系統
    rank = "純真初心者"
    color = "#444"
    if max_s >= 30: 
        rank, color = "無上時間領主", "#fff"
    elif max_s >= 14: 
        rank, color = "鋼鐵執行者", "#aaa"
    elif max_s >= 7: 
        rank, color = "規律生活家", "#888"
    
    st.markdown(f"""
        <div style="text-align: center; padding: 120px 0;">
            <div class="label" style="letter-spacing: 10px;">榮譽稱號 // RANK</div>
            <div style="font-size: 80px; font-weight: 900; color: {color}; 
                        text-shadow: 0 0 40px {color}44; margin: 20px 0;">
                {rank}
            </div>
            <div style="font-size: 14px; color: #444; margin-top: 10px;">
                最高連勝紀錄：{max_s} 天
            </div>
        </div>
    """, unsafe_allow_html=True)
