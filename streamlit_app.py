import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 0. 檔案定義 ---
DB_FILE = "mono_v5_data.json"

# --- 1. 頁面配置 ---
st.set_page_config(page_title="MONO // 自律系統", layout="wide")

# --- 2. 現代黑化 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    
    /* 習慣卡片 - 重度 */
    .habit-card {
        background: #0d0d0d; border: 1px solid #222;
        border-radius: 12px; padding: 20px; margin-bottom: 12px;
        border-left: 5px solid #fff;
    }
    /* 任務卡片 - 輕度 */
    .task-card {
        background: #050505; border: 1px solid #111;
        border-radius: 8px; padding: 12px; margin-bottom: 8px;
    }
    .done-blur { opacity: 0.2; filter: blur(1.5px); transition: 0.5s; }
    
    /* 進度條 */
    .xp-bar { background: #111; border-radius: 10px; height: 8px; width: 100%; margin: 10px 0; }
    .xp-progress { background: #fff; height: 100%; border-radius: 10px; transition: 0.8s; }
    
    .section-title { font-size: 12px; color: #444; letter-spacing: 2px; margin-bottom: 15px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料處理 (自動修復 KeyError) ---
def load_data():
    defaults = {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                d = json.load(f)
                # 遍歷 defaults，如果 key 不在 d 裡面就補上去
                for key, value in defaults.items():
                    if key not in d:
                        d[key] = value
                return d
            except: return defaults
    return defaults

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 4. 側邊導航 ---
st.sidebar.title("MONO // SYSTEM")
page = st.sidebar.radio("切換功能", ["任務清單", "數據統計", "專注計時器", "成就歷史", "系統設定"])

def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

# ---------------------------------------------------------
# 1. 任務清單 (FLOW)
# ---------------------------------------------------------
if page == "任務清單":
    # 等級顯示
    xp_pct = data["total_xp"] % 100
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: flex-end;'>
            <span style='font-size: 30px; font-weight: 900;'>LEVEL {data['level']}</span>
            <span style='color: #444;'>{xp_pct} / 100 XP</span>
        </div>
        <div class="xp-bar"><div class="xp-progress" style="width: {xp_pct}%;"></div></div>
    """, unsafe_allow_html=True)

    # 收納新增功能 (減輕視覺重量)
    with st.expander("＋ 新增任務或習慣"):
        c1, c2 = st.columns([3, 1])
        new_name = c1.text_input("名稱", placeholder="想做點什麼？", label_visibility="collapsed")
        mode = c2.selectbox("類型", ["每日習慣", "臨時任務"], label_visibility="collapsed")
        if st.button("確認新增", use_container_width=True):
            if new_name:
                if mode == "每日習慣":
                    data["habits"].append({"name": new_name, "streak": 0, "last_done": ""})
                else:
                    data["tasks"].append({"name": new_name})
                save_data(data); st.rerun()

    st.write(" ")
    l_col, r_col = st.columns([2, 1])

    with l_col:
        st.markdown("<div class='section-title'>每日習慣 / HABITS</div>", unsafe_allow_html=True)
        for idx, h in enumerate(data["habits"]):
            is_done = (h["last_done"] == today)
            st.markdown(f"""
                <div class="habit-card {'done-blur' if is_done else ''}">
                    <div style='font-size: 20px; font-weight: 600;'>{h['name']}</div>
                    <div style='font-size: 12px; color: #666;'>🔥 已連續達成 {h['streak']} 天</div>
                </div>
            """, unsafe_allow_html=True)
            if not is_done:
                if st.button(f"標記完成", key=f"h_{idx}", use_container_width=True):
                    h["streak"] = h["streak"] + 1 if h["last_done"] == yesterday else 1
                    h["last_done"] = today
                    add_xp(25)
                    st.rerun()

    with r_col:
        st.markdown("<div class='section-title'>臨時任務 / TASKS</div>", unsafe_allow_html=True)
        for idx, t in enumerate(data["tasks"]):
            st.markdown(f"""
                <div class="task-card">
                    <div style='font-size: 15px;'>{t['name']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"完成", key=f"t_{idx}", use_container_width=True):
                data["history"].append({"項目": t["name"], "日期": today, "類型": "臨時任務"})
                data["tasks"].pop(idx)
                save_data(data); st.rerun()

# ---------------------------------------------------------
# 2. 數據統計 (ANALYTICS)
# ---------------------------------------------------------
elif page == "數據統計":
    st.title("數據中心")
    if not data["habits"]:
        st.warning("目前沒有數據，請先建立習慣。")
    else:
        df_h = pd.DataFrame(data["habits"])
        
        # 簡單直觀的水平長條圖
        fig = px.bar(df_h, x="streak", y="name", orientation='h',
                     title="各項習慣連勝紀錄",
                     labels={'streak':'連勝天數', 'name':'習慣名稱'},
                     color_discrete_sequence=['#ffffff'])
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        
        # 統計卡片
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("總累計 XP", data["total_xp"])
        c2.metric("當前等級", f"Lv. {data['level']}")
        c3.metric("習慣總數", len(data["habits"]))

# ---------------------------------------------------------
# 3. 專注計時器 (FOCUS)
# ---------------------------------------------------------
elif page == "專注計時器":
    st.title("VOID // 專注空間")
    st.write("設定一段時間，讓自己進入深度工作。")
    mins = st.slider("選擇分鐘", 5, 120, 25)
    
    if st.button("開始計時", use_container_width=True):
        ph = st.empty()
        bar = st.progress(0)
        total_seconds = mins * 60
        for i in range(total_seconds, 0, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<div style='font-size: 80px; text-align: center; font-family: monospace;'>{mm:02}:{ss:02}</div>", unsafe_allow_html=True)
            bar.progress((total_seconds - i) / total_seconds)
            time.sleep(1)
        st.balloons()
        st.success("專注完成！獎勵 10 XP")
        add_xp(10)

# ---------------------------------------------------------
# 4. 成就歷史 (HISTORY)
# ---------------------------------------------------------
elif page == "成就歷史":
    st.title("成就紀錄")
    if not data["history"]:
        st.info("尚無完成紀錄，去執行任務吧！")
    else:
        df_hist = pd.DataFrame(data["history"])
        st.dataframe(df_hist, use_container_width=True)

# ---------------------------------------------------------
# 5. 系統設定 (SETTINGS)
# ---------------------------------------------------------
elif page == "系統設定":
    st.title("系統管理")
    st.write("危險區域")
    if st.button("格式化所有存檔數據"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.clear()
        st.success("數據已清空，請重新整理頁面。")
        st.rerun()
