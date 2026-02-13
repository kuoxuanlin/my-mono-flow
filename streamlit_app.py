import streamlit as st
import json
import os
from datetime import datetime, timedelta

# --- 頁面配置 ---
st.set_page_config(page_title="MONO // HABIT-FLOW", layout="wide")

# --- 極簡黑化 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    #MainMenu, footer, header {visibility: hidden;}

    .habit-card {
        background: #0a0a0a;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        transition: all 0.5s ease;
    }
    .streak-font {
        font-family: 'Courier New', monospace;
        font-weight: 900;
        color: #fff;
    }
    .done-status {
        color: #222; /* 完成後字體變深灰色，達成低調感 */
        filter: blur(1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- 資料邏輯 ---
DB_FILE = "habits.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'habits' not in st.session_state:
    st.session_state.habits = load_data()

# --- 核心邏輯：更新連勝 ---
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def toggle_habit(idx):
    habit = st.session_state.habits[idx]
    last_date = habit.get("last_done", "")
    
    if last_date != today:
        # 計算連勝
        if last_date == yesterday:
            habit["streak"] += 1
        else:
            habit["streak"] = 1
        
        habit["last_done"] = today
        save_data(st.session_state.habits)
        st.rerun()

# --- 介面渲染 ---
st.title("MONO // HABIT TRACKER")
st.caption(f"SYSTEM_TIME: {today} // KEEP THE STREAK ALIVE")

# 新增習慣
col_in, col_btn = st.columns([4, 1])
with col_in:
    new_h = st.text_input("", placeholder="DEFINE A NEW CONSTANT...")
with col_btn:
    if st.button("+ FIX"):
        if new_h:
            st.session_state.habits.append({
                "name": new_h, 
                "streak": 0, 
                "last_done": ""
            })
            save_data(st.session_state.habits)
            st.rerun()

st.markdown("---")

# 習慣清單
for idx, habit in enumerate(st.session_state.habits):
    is_done_today = (habit["last_done"] == today)
    card_class = "done-status" if is_done_today else ""
    
    cols = st.columns([3, 1, 1])
    
    with cols[0]:
        st.markdown(f"""
            <div class="habit-card {card_class}">
                <div style="font-size: 10px; color: #444; letter-spacing: 2px;">CONSTANT // {idx+1:02}</div>
                <div style="font-size: 22px; font-weight: 700; margin-top: 5px;">{habit['name']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        # 連勝顯示
        st.markdown(f"<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:12px; color:#444;'>STREAK</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='streak-font' style='font-size:30px;'>{habit['streak']}</div>", unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)
        
    with cols[2]:
        st.write(" ")
        st.write(" ")
        btn_label = "COMPLETE" if not is_done_today else "DONE"
        if st.button(btn_label, key=f"h_{idx}", disabled=is_done_today):
            toggle_habit(idx)

# 刪除習慣（隱藏在下方）
with st.expander("SYSTEM_CLEANUP"):
    for idx, h in enumerate(st.session_state.habits):
        if st.button(f"DELETE {h['name']}", key=f"del_{idx}"):
            st.session_state.habits.pop(idx)
            save_data(st.session_state.habits)
            st.rerun()
