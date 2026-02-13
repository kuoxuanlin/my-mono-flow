
import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 站內編輯後的 CSS ---

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


# --- 核心邏輯與數據處理 ---

# --- 核心數據處理 ---
def load_data(): ...
def save_data(data): ...
def add_xp(amount): ...


# --- 儀錶板模塊 ---

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


# --- 數據中心模塊 ---

# --- 頁面 2: 數據中心邏輯 ---
if data["habits"]:
    df = pd.DataFrame(data["habits"])
    fig = px.bar(df, x="streak", y="name", orientation='h', color_discrete_sequence=['#ffffff'])
    fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
    st.plotly_chart(fig, use_container_width=True)


# --- 專注空間模塊 ---

# --- 頁面 3: 專注空間邏輯 (條狀調整版) ---
st.markdown("<div class='header-tag'>// 深度專注序列</div>", unsafe_allow_html=True)

# 使用滑桿取代輸入框，設定 5 分鐘為一個區間
m = st.slider("選擇專注時長 (MINUTES)", min_value=5, max_value=120, value=25, step=5)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("啟動專注序列", use_container_width=True):
        # 視覺計時容器
        ph = st.empty()
        bar = st.progress(0)
        total_seconds = m * 60
        
        for i in range(total_seconds, 0, -1):
            mm, ss = divmod(i, 60)
            # 大字級倒數顯示
            ph.markdown(f"<h1 style='text-align:center; font-size:100px; font-family:monospace;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            # 進度條隨時間減少同步更新
            bar.progress(1.0 - (i / total_seconds))
            time.sleep(1)
            
        st.success(f"序列完成：獲得 15 XP / 專注時長：{m} 分鐘")
        add_xp(15)
        st.balloons()

