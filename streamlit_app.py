import streamlit as st
import json, os, time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


# --- MODULE: 1_GLOBAL ---
# 全局樣式\nstyle = '<style>.stApp { background-color: #000; color: #fff; } [data-testid="stSidebar"] { background-color: #050505; } .header-tag { font-size: 10px; color: #444; letter-spacing: 4px; font-weight: 800; }</style>'\nst.markdown(style, unsafe_allow_html=True)

# --- MODULE: 4_VOID ---
# --- 專注空間：控制終端版面 (V2) ---
css = '<style>@keyframes glow { 0% { text-shadow: 0 0 5px #fff; opacity: 0.8; } 50% { text-shadow: 0 0 20px #fff, 0 0 30px #fff; opacity: 1; } 100% { text-shadow: 0 0 5px #fff; opacity: 0.8; } } @keyframes pulse { 0%, 100% { height: 10px; opacity: 0.3; } 50% { height: 40px; opacity: 1; } } .timer-active { font-size: 80px; font-family: monospace; text-align: center; animation: glow 2s infinite ease-in-out; margin: 20px 0; } .neural-container { display: flex; justify-content: center; align-items: flex-end; gap: 4px; height: 40px; } .pulse-bar { width: 3px; background: #fff; animation: pulse 1.5s infinite ease-in-out; } .terminal-card { border: 1px solid #222; padding: 15px; border-radius: 4px; background: rgba(5,5,5,0.5); }</style>'
st.markdown(css, unsafe_allow_html=True)

st.markdown("<div class='header-tag'>// NEURAL_VOID_OS_TERMINAL</div>", unsafe_allow_html=True)

# 建立三欄佈局
left_col, mid_col, right_col = st.columns([1, 2, 1])

with left_col:
    st.markdown("<div class='terminal-card'><b>[ 系統指標 ]</b><br><small>LV. " + str(data.get('level', 1)) + "</small><br><small>XP: " + str(data.get('total_xp', 0)) + "</small></div>", unsafe_allow_html=True)
    st.write("")
    st.write("// 預計序列增益")
    st.code("+15 XP\n+穩定度", language="text")

with right_col:
    st.markdown("<div class='terminal-card'><b>[ 環境參數 ]</b></div>", unsafe_allow_html=True)
    sound_on = st.checkbox("虛擬音效模擬", value=True)
    if sound_on:
        st.caption(">> 已同步神經頻率")
    st.divider()
    st.write("// 當前共振格言")
    quotes = ["靜默是最高級的運算。", "刪除雜訊，保留核心。", "專注是唯一的武裝。", "在代碼中尋找秩序。"]
    q_box = st.empty()
    q_box.info(quotes[int(time.time()) % len(quotes)])

with mid_col:
    m = st.slider("調整序列時長 (MIN)", 5, 120, 25, 5)
    
    if st.button("啟動專注序列", use_container_width=True):
        ph = st.empty()
        bar = st.progress(0)
        
        # 波形顯示區
        pulse_ph = st.empty()
        pulse_html = "<div class='neural-container'>" + "".join([f"<div class='pulse-bar' style='animation-delay: {0.1*i}s'></div>" for i in range(15)]) + "</div>"
        pulse_ph.markdown(pulse_html, unsafe_allow_html=True)
        
        total_s = m * 60
        for i in range(total_s, -1, -1):
            mm, ss = divmod(i, 60)
            ph.markdown(f"<div class='timer-active'>{mm:02}:{ss:02}</div>", unsafe_allow_html=True)
            bar.progress(1.0 - (i/total_s))
            
            if i % 60 == 0 and i != total_s:
                 q_box.info(quotes[(i//60) % len(quotes)])
            time.sleep(1)
            
        st.success("序列完成")
        data["history"].append({"項目": f"終端專注 {m}min", "日期": today, "類型": "精神強化"})
        add_xp(15)
        st.balloons()
