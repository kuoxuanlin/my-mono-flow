import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 0. 基礎配置 ---
DB_FILE = "mono_v5_data.json"
st.set_page_config(page_title="MONO // MODULAR OS", layout="wide")

# --- 1. 核心組件模組 (UI Components) ---
# 將 UI 與邏輯分開，方便開發者模式調用
def inject_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #000; color: #fff; }
        [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
        
        /* 習慣卡片 - 強化質感 */
        .habit-card {
            background: #0d0d0d; border: 1px solid #222;
            border-radius: 10px; padding: 18px; margin-bottom: 12px;
            border-left: 4px solid #fff; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        /* 任務卡片 - 扁平化 */
        .task-card {
            background: #080808; border: 1px solid #151515;
            border-radius: 6px; padding: 10px 15px; margin-bottom: 8px;
        }
        .done-blur { opacity: 0.2; filter: grayscale(100%) blur(1px); }
        
        /* 進度條系統 */
        .xp-bar { background: #111; border-radius: 20px; height: 6px; width: 100%; margin-top: 10px; }
        .xp-progress { background: #fff; height: 100%; border-radius: 20px; box-shadow: 0 0 10px #fff; }
        
        /* 文字排版 */
        .section-header { font-size: 11px; color: #555; letter-spacing: 3px; font-weight: 800; margin-bottom: 15px; text-transform: uppercase; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 資料持久化模組 ---
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

# 初始化狀態
if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
inject_custom_css()

# --- 3. 側邊欄與導航 ---
with st.sidebar:
    st.title("MONO // OS")
    page = st.radio("系統接口", ["DASHBOARD", "ANALYTICS", "VOID TIME", "ARCHIVE", "SETTINGS"])
    st.divider()
    
    # 縮小後的新增按鈕區 (放入側邊欄避免佔據主視角)
    with st.expander("＋ QUICK ADD", expanded=False):
        n_name = st.text_input("NAME", key="n_name", label_visibility="collapsed")
        n_type = st.segmented_control("TYPE", ["HABIT", "TASK"], default="HABIT")
        if st.button("EXECUTE", use_container_width=True):
            if n_name:
                if n_type == "HABIT": data["habits"].append({"name": n_name, "streak": 0, "last_done": ""})
                else: data["tasks"].append({"name": n_name})
                save_data(data); st.rerun()

# --- 4. 功能邏輯模組 ---
def add_xp(amount):
    data["total_xp"] += amount
    data["level"] = (data["total_xp"] // 100) + 1
    save_data(data)

today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# ---------------------------------------------------------
# PAGE: DASHBOARD (任務清單)
# ---------------------------------------------------------
if page == "DASHBOARD":
    # 頂部狀態欄
    xp_pct = data["total_xp"] % 100
    st.markdown(f"""
        <div style='margin-bottom: 30px;'>
            <div style='display: flex; justify-content: space-between; align-items: baseline;'>
                <span style='font-size: 40px; font-weight: 900; letter-spacing: -2px;'>LV.{data['level']}</span>
                <span style='font-family: monospace; color: #444;'>{xp_pct}/100 XP</span>
            </div>
            <div class="xp-bar"><div class="xp-progress" style="width: {xp_pct}%;"></div></div>
        </div>
    """, unsafe_allow_html=True)

    col_h, col_t = st.columns([1.6, 1])

    with col_h:
        st.markdown("<div class='section-header'>// 每日習慣</div>", unsafe_allow_html=True)
        for idx, h in enumerate(data["habits"]):
            is_done = (h["last_done"] == today)
            st.markdown(f"""
                <div class="habit-card {'done-blur' if is_done else ''}">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-size: 22px; font-weight: 700;'>{h['name']}</span>
                        <span style='font-family: monospace; color: #fff;'>{h['streak']}D</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if not is_done:
                if st.button(f"COMPLETE", key=f"h_{idx}", use_container_width=True):
                    h["streak"] = h["streak"] + 1 if h["last_done"] == yesterday else 1
                    h["last_done"] = today
                    add_xp(25); st.rerun()

    with col_t:
        st.markdown("<div class='section-header'>// 臨時任務</div>", unsafe_allow_html=True)
        for idx, t in enumerate(data["tasks"]):
            c_t1, c_t2 = st.columns([4, 1])
            c_t1.markdown(f'<div class="task-card">{t["name"]}</div>', unsafe_allow_html=True)
            if c_t2.button("✔", key=f"t_{idx}", use_container_width=True):
                data["history"].append({"name": t["name"], "date": today, "type": "TASK"})
                data["tasks"].pop(idx); save_data(data); st.rerun()

# ---------------------------------------------------------
# PAGE: SETTINGS (含開發者模式)
# ---------------------------------------------------------
elif page == "SETTINGS":
    st.title("SYSTEM SETTINGS")
    
    data["dev_mode"] = st.toggle("開啟開發者模式 (Developer Mode)", value=data.get("dev_mode", False))
    save_data(data)
    
    if data["dev_mode"]:
        st.divider()
        st.markdown("<div class='section-header'>// DEVELOPER CONSOLE</div>", unsafe_allow_html=True)
        
        # 模組化展示代碼框
        tab1, tab2, tab3 = st.tabs(["UI Components", "Page Logic", "Full Export"])
        
        with tab1:
            st.code("""
# --- UI STYLES ---
.habit-card { background: #0d0d0d; border-left: 4px solid #fff; }
.task-card  { background: #080808; border: 1px solid #151515; }
.xp-progress { box-shadow: 0 0 10px #fff; }
            """, language="css")
            
        with tab2:
            st.code(f"""
# --- DATA STRUCTURE ---
Current Habits: {len(data['habits'])}
Current Tasks: {len(data['tasks'])}
Total XP: {data['total_xp']}
            """, language="python")

        with tab3:
            st.write("獲取目前版本的完整 Python 腳本（避免模型修改遺失部分內容）")
            # 這裡可以放一個下載按鈕導出目前的 .json 資料
            st.download_button("DOWNLOAD DATABASE (JSON)", 
                             data=json.dumps(data, indent=4), 
                             file_name="mono_v5_data.json")

    st.divider()
    if st.button("HARD RESET SYSTEM", type="secondary"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear(); st.rerun()

# --- 其他頁面保持精簡 (ANALYTICS, VOID, ARCHIVE 邏輯同上，僅優化 UI) ---
elif page == "ANALYTICS":
    st.title("NEURAL ANALYTICS")
    if data["habits"]:
        df = pd.DataFrame(data["habits"])
        fig = px.bar(df, x="streak", y="name", orientation='h', color_discrete_sequence=['#fff'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

elif page == "VOID TIME":
    st.title("VOID SPACE")
    m = st.slider("MINUTES", 5, 120, 25)
    if st.button("INITIATE FOCUS"):
        bar = st.progress(0)
        for i in range(100):
            time.sleep(m * 0.006) # 模擬計時
            bar.progress(i + 1)
        st.success("SEQUENCE COMPLETE +10 XP"); add_xp(10)

elif page == "ARCHIVE":
    st.title("HISTORY LOG")
    if data["history"]: st.table(pd.DataFrame(data["history"]))
