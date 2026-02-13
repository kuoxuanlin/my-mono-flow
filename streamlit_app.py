import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 頁面配置 ---
st.set_page_config(page_title="MONO // SYSTEM", layout="wide")

# --- 進階黑化 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    .habit-card {
        background: #0a0a0a; border: 1px solid #111;
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }
    .xp-bar {
        background: #111; border-radius: 10px; height: 5px; width: 100%; margin-top: 10px;
    }
    .xp-progress {
        background: #fff; height: 100%; border-radius: 10px; transition: 0.5s;
    }
    .metric-box {
        text-align: center; padding: 20px; border: 1px solid #111; border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 資料邏輯 ---
DB_FILE = "habits_v2.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"habits": [], "total_xp": 0, "level": 1}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 側邊導航 ---
st.sidebar.title("MONO // CORE")
page = st.sidebar.radio("NAVIGATE", ["FLOW", "DATA", "RANK"])

# --- 等級系統計算 ---
def add_xp(amount):
    data["total_xp"] += amount
    # 每 100 XP 升一級
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

# ---------------------------------------------------------
# PAGE: FLOW (核心追蹤)
# ---------------------------------------------------------
if page == "FLOW":
    st.title("CORE // FLOW")
    
    # 頂部狀態欄 (XP 條)
    current_xp = data["total_xp"] % 100
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; font-size: 12px; color: #444;'>
            <span>LEVEL {data['level']}</span>
            <span>{current_xp} / 100 XP</span>
        </div>
        <div class="xp-bar"><div class="xp-progress" style="width: {current_xp}%;"></div></div>
    """, unsafe_allow_html=True)

    st.write(" ")
    
    # 習慣顯示
    for idx, habit in enumerate(data["habits"]):
        is_done = (habit.get("last_done") == today)
        cols = st.columns([3, 1, 1])
        
        with cols[0]:
            st.markdown(f"""
                <div class="habit-card" style="opacity: {0.3 if is_done else 1}; filter: blur({ '2px' if is_done else '0px' });">
                    <div style="font-size: 10px; color: #444; letter-spacing: 2px;">HABIT // {idx+1:02}</div>
                    <div style="font-size: 22px; font-weight: 700;">{habit['name']}</div>
                    <div style="font-size: 10px; color: #888;">🔥 {habit['streak']} DAY STREAK</div>
                </div>
            """, unsafe_allow_html=True)
            
        with cols[1]:
            st.write(" ")
            if st.button("COMPLETE", key=f"btn_{idx}", disabled=is_done, use_container_width=True):
                # 更新連勝
                if habit["last_done"] == yesterday:
                    habit["streak"] += 1
                elif habit["last_done"] != today:
                    habit["streak"] = 1
                
                habit["last_done"] = today
                add_xp(25) # 完成一個任務得 25 XP
                st.rerun()
                
    # 快速新增
    with st.sidebar:
        st.divider()
        new_h = st.text_input("ADD NEW HABIT")
        if st.button("CONFIRM"):
            data["habits"].append({"name": new_h, "streak": 0, "last_done": ""})
            save_data(data)
            st.rerun()

# ---------------------------------------------------------
# PAGE: DATA (數據追蹤)
# ---------------------------------------------------------
elif page == "DATA":
    st.title("DATA // ANALYTICS")
    
    if not data["habits"]:
        st.info("NO DATA AVAILABLE.")
    else:
        # 轉換資料為 DataFrame
        df = pd.DataFrame(data["habits"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.metric("TOTAL XP", data["total_xp"])
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.metric("ACTIVE HABITS", len(data["habits"]))
            st.markdown("</div>", unsafe_allow_html=True)

        st.write(" ")
        # 連勝分布圖
        fig = px.bar(df, x="name", y="streak", title="STREAK DISTRIBUTION",
                     color_discrete_sequence=['#ffffff'])
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PAGE: RANK (排位系統)
# ---------------------------------------------------------
elif page == "RANK":
    st.title("RANK // STATUS")
    
    max_streak = max([h["streak"] for h in data["habits"]]) if data["habits"] else 0
    
    # 根據最高連勝給予稱號
    rank_name = "UNRANKED"
    rank_color = "#444"
    if max_streak > 30: rank_name, rank_color = "MONO TITAN", "#fff"
    elif max_streak > 14: rank_name, rank_color = "STEADY FLOW", "#aaa"
    elif max_streak > 7: rank_name, rank_color = "INITIATOR", "#666"
    
    st.markdown(f"""
        <div style="text-align: center; padding: 100px 0;">
            <div style="font-size: 12px; color: #444; letter-spacing: 5px;">CURRENT RANK</div>
            <div style="font-size: 60px; font-weight: 900; color: {rank_color}; text-shadow: 0 0 20px {rank_color}44;">
                {rank_name}
            </div>
            <div style="margin-top: 20px; color: #888;">MAX STREAK: {max_streak} DAYS</div>
        </div>
    """, unsafe_allow_html=True)
