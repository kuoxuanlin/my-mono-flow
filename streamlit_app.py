import streamlit as st\nimport json, os, time, io\nimport pandas as pd\nfrom datetime import datetime, timedelta\n\ndata = {"habits": [], "tasks": [], "total_xp": 0, "level": 1, "history": [], "dev_mode": true}\n\n# --- 1_GLOBAL ---\nst.markdown('<style>.stApp{background:#000;color:#fff;} .header-tag{color:#444;letter-spacing:4px;font-size:10px;}</style>', unsafe_allow_html=True)\n\n# --- 4_VOID ---\nst.markdown("<div class='header-tag'>// NEURAL_VOID_PRO_V2</div>", unsafe_allow_html=True)

# 頂部狀態欄
c1, c2, c3 = st.columns([1,2,1])
with c1:
    st.metric("當前等級", f"LV.{data.get('level', 1)}")
with c3:
    st.metric("總經驗值", data.get('total_xp', 0))

with c2:
    m = st.slider("設定序列分鐘", 1, 120, 25)
    
    # 這裡新增一個模式選擇
    mode = st.segmented_control("專注模式", ["普通", "深度", "極限"], default="普通")
    
    if st.button("啟動序列", use_container_width=True):
        ph = st.empty()
        # 新增一個同步視覺效果的占位符
        sync_ph = st.empty()
        
        total_s = m * 60
        for i in range(total_s, -1, -1):
            mm, ss = divmod(i, 60)
            
            # 計時器大字
            ph.markdown(f"<h1 style='text-align:center; font-family:monospace; color:#fff;'>{mm:02}:{ss:02}</h1>", unsafe_allow_html=True)
            
            # 模擬神經同步波形 (隨機符號模擬)
            sync_bar = "".join(["|" if (i+j)%5==0 else "." for j in range(20)])
            sync_ph.markdown(f"<p style='text-align:center; color:#444; font-family:monospace;'>SYNC: [{sync_bar}]</p>", unsafe_allow_html=True)
            
            time.sleep(1)
            
        # 根據模式給予不同的 XP
        xp_gain = {"普通": 15, "深度": 25, "極限": 40}[mode]
        add_xp(xp_gain)
        
        # 紀錄到歷史
        new_log = {"項目": f"專注({mode})", "日期": today, "XP": xp_gain}
        data.get("history", []).append(new_log)
        
        st.success(f"序列完成：獲得 {xp_gain} XP")
        st.balloons()

st.divider()
# 下方顯示最近三次的紀錄
st.markdown("<p style='font-size:10px; color:#666;'>[ 最近掃描紀錄 ]</p>", unsafe_allow_html=True)
history = data.get("history", [])[-3:]
for log in reversed(history):
    st.text(f"> {log['日期']} | {log['項目']} | +{log['XP']}XP")\n
