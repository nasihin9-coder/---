# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import time

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_obs, c_obs = df[st.session_state['z_col']].values, df[st.session_state['s_col']].values
    c_base = st.sidebar.number_input("背景盐度", 200, 2000, 1000)
    
    # 物理模型计算
    k_factor = 3.5 * (st.session_state['dh'] / 8.0e-5)
    c_pred = c_base + (c_obs[-1] - c_base) * np.exp(-k_factor * (z_obs.max() - z_obs))
    r2 = r2_score(c_obs, c_pred)

    # 结果看板
    m1, m2, m3 = st.columns(3)
    m1.metric("监测深度跨度", f"{z_obs.max():.2f} m")
    m2.metric("模型匹配度 (R²)", f"{max(0, r2):.4f}")
    m3.metric("扩散系数 (K)", f"{k_factor:.4f}")
    st.divider()

    if st.button("🚀 开始动态拟合", type="primary"):
        chart_spot = st.empty()
        fig, ax = plt.subplots(figsize=(10, 5))
        z_sim = np.linspace(0, z_obs.max(), 100)
        c_sim = c_base + (c_obs[-1] - c_base) * np.exp(-k_factor * (z_obs.max() - z_sim))
        
        for i in range(len(z_sim)-1, -1, -5):
            ax.clear()
            ax.set_xlim(0, c_obs.max()*1.1)
            ax.set_ylim(z_obs.max()+0.1, 0)
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.5)
            ax.plot(c_sim[i:], z_sim[i:], color='darkorange', linewidth=3)
            chart_spot.pyplot(fig)
            time.sleep(0.01)
else:
    st.warning("请先在主页上传数据")
