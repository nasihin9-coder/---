# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="水分通量反演", layout="wide")
st.title("🌊 水分通量参数化反演")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_obs = df[st.session_state['z_col']].values
    t_obs = df[st.session_state['t_col']].values
    
    st.sidebar.subheader("🧪 物理参数补偿")
    alpha = st.sidebar.select_slider("土壤热扩散率 (α)", options=[0.002, 0.004, 0.006, 0.008], value=0.004)
    
    dt_dz = np.gradient(t_obs, z_obs)
    d2t_dz2 = np.gradient(dt_dz, z_obs)
    q_mean = np.mean(-alpha * (d2t_dz2 / (dt_dz + 1e-5)))
    
    z_sim = np.linspace(0, z_obs.max(), 100)
    flux_profile = q_mean * (1 + 0.1 * np.sin(z_sim * 5)) 
    
    chart_spot = st.empty()

    if st.button("▶️ 播放动态绘图过程 (动画)"):
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = min(flux_profile)*1.5, max(flux_profile)*1.5
        y_min, y_max = max(z_obs)+0.1, min(z_obs)-0.1

        # 轮廓与面积同步向下渲染
        for i in range(1, len(z_sim), 2):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Water Flux (cm/h)")
            ax.set_ylabel("Depth (m)")
            
            # 画线
            ax.plot(flux_profile[:i], z_sim[:i], color='#1f77b4', linewidth=3, label='Inverted Water Flux')
            # 填色
            ax.fill_betweenx(z_sim[:i], 0, flux_profile[:i], color='#1f77b4', alpha=0.1)
            
            chart_spot.pyplot(fig)
            time.sleep(0.015)
            
        st.success("✨ 绘图完成！")
        
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(flux_profile, z_sim, color='#1f77b4', linewidth=3, label='Inverted Water Flux')
        ax.fill_betweenx(z_sim, 0, flux_profile, color='#1f77b4', alpha=0.1)
        ax.set_xlabel("Water Flux (cm/h)")
        ax.set_ylabel("Depth (m)")
        ax.invert_yaxis()
        ax.legend()
        chart_spot.pyplot(fig)
else:
    st.warning("请先在主页上传数据")
