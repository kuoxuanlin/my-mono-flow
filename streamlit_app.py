import streamlit as st
import json, os, time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 站內編輯後的 CSS ---
st.markdown("""
/* 介面風格模塊 */
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
""", unsafe_allow_html=True)

# --- 核心邏輯節錄 ---

# --- 頁面 1: 儀錶板邏輯 ---
# 渲染等級與 XP 條
xp_pct = data["total_xp"] % 100
st.markdown(f"LV.{data['level']} ...")

# 橫向任務新增區
c1, c2, c3 = st.columns([4, 1.2, 0.8])
name = c1.text_input("任務名稱", ...)

# 習慣與任務卡片渲染邏輯
l_col, r_col = st.columns([1.6, 1])
with l_col: # 渲染 Habits
with r_col: # 渲染 Tasks


# --- 專注空間節錄 ---

# --- 頁面 3: 專注空間邏輯 (動畫強化版) ---
import streamlit_lottie as st_lottie # 確保環境有安裝或直接用內建 CSS 動畫

# 1. 注入局部 CSS 動畫 (呼吸燈效果)
st.markdown("""
<style>
@keyframes glow {
    0% { text-shadow: 0 0 5px #fff; opacity: 0.8; }
    50% { text-shadow: 0 0 20px #fff, 0 0 30px #fff; opacity: 1; }
    100% { text-shadow: 0 0 5px #fff; opacity: 0.8; }
}
.timer-active {
    font-size: 120px; 
    font-family: 'Courier New', monospace; 
    text-align: center; 
    color: #fff;
    animation: glow 2s infinite ease-in-out;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-tag'>// 深度專注序列 ACTIVATING...</div>", unsafe_allow_html=True)

# 2. 佈局設定
m = st.slider("選擇專注時長 (MINUTES)", min_value=5, max_value=120, value=25, step=5)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    start_btn = st.button("啟動專注序列", use_container_width=True)
    
    if start_btn:
        # 建立動畫與計時容器
        placeholder = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_seconds = m * 60
        
        for i in range(total_seconds, -1, -1):
            mm, ss = divmod(i, 60)
            
            # 使用 CSS 動畫類名計時
            placeholder.markdown(f"<div class='timer-active'>{mm:02}:{ss:02}</div>", unsafe_allow_html=True)
            
            # 進度條平滑更新
            pct = 1.0 - (i / total_seconds)
            progress_bar.progress(pct)
            
            # 狀態文字閃爍
            status_text.markdown(f"<p style='text-align:center; color:#444;'>系統運行中 - 剩餘 {i} 秒...</p>", unsafe_allow_html=True)
            
            time.sleep(1)
            
        # 完成後的動畫與獎勵
        placeholder.balloons()
        st.success(f"序列完成：獲得 15 XP")
        add_xp(15)

# (此處僅為展示，導出時會根據你修改的內容組合)
