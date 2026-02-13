import streamlit as st, json, os, time, pandas as pd
from datetime import datetime

data = {'habits': [], 'tasks': [], 'total_xp': 0, 'level': 1, 'history': [], 'dev_mode': True}
today = datetime.now().strftime('%Y-%m-%d')
def add_xp(a): data['total_xp']+=a; data['level']=(data['total_xp']//100)+1
exec_env = {'st':st, 'data':data, 'time':time, 'add_xp':add_xp, 'today':today, 'divmod':divmod}

st.sidebar.title('MONO // OS (STABLE)')
page = st.sidebar.radio('NAV', ['HOME'])


# --- 1_GLOBAL ---
code_1_GLOBAL = r'''st.markdown('<style>.stApp{background:#000;color:#fff;} .header-tag{color:#444;letter-spacing:4px;font-size:10px;}</style>', unsafe_allow_html=True)'''
if page == 'HOME' or '1_GLOBAL' == '1_GLOBAL': exec(code_1_GLOBAL.strip(), exec_env)

# --- 4_VOID ---
code_4_VOID = r'''st.markdown("<div class='header-tag'>// NEURAL_VOID_MINIMAL</div>", unsafe_allow_html=True)

# 簡化版面：只保留歷史紀錄與計時主區
c1, c2 = st.columns([1, 3])

with c1:
    st.caption("專注日誌")
    history = data.get('history', [])[-8:]
    if history:
        for log in reversed(history):
            st.write(f"● {log['min']}m")
    else:
        st.write("尚無數據")

with c2:
    m = st.slider("設定專注時長 (MIN)", 1, 120, 25)
    
    if st.button("啟動專注序列", use_container_width=True):
        ph = st.empty()
        
        total_s = m * 60
        for i in range(total_s, -1, -1):
            mm, ss = divmod(i, 60)
            # 渲染計時器
            ph.markdown(f"<h1 style='text-align:center; font-size:100px; font-family:monospace;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        
        # 僅儲存歷史紀錄，不再計算 XP
        if 'history' not in data: 
            data['history'] = []
        data['history'].append({"date": today, "min": m})
        
        # 儲存變動後的 data 字典
        save_data(data)
        
        st.success("專注完成")
        st.balloons()'''
if page == 'HOME' or '4_VOID' == '1_GLOBAL': exec(code_4_VOID.strip(), exec_env)
