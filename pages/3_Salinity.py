# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_obs = df[st.session_state['z_col']].values
    c_obs = df[st.session_state['s_col']].values
    dh = st.session_state.get('dh', 8.0e-5)
    
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("深层背景盐度 (mg/L)", 200, 2000, 500)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    z_sim = np.linspace(0, z_obs.max(), 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_sim = c_base + (c_obs[0] - c_base) * np.exp(-k_factor * z_sim)
    
    chart_spot = st.empty()

    if st.button("▶️ 播放动态绘图过程 (动画)"):
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = 0, max(c_obs)*1.1
        y_min, y_max = max(z_obs)+0.1, min(z_obs)-0.1

        # 曲线生长动画
        for i in range(1, len(z_sim), 2):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            # 铺垫散点背景
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
            # 曲线逐渐延伸
            ax.plot(c_sim[:i], z_sim[:i], color='green', linestyle=styles[line_style], linewidth=3, label='Model')
            chart_spot.pyplot(fig)
            time.sleep(0.01)
            
        st.success("✨ 绘图完成！")
        
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
        ax.plot(c_sim, z_sim, color='green', linestyle=styles[line_style], linewidth=3, label='Model')
        ax.set_xlabel("Salinity (mg/L)")
        ax.set_ylabel("Depth (m)")
        ax.invert_yaxis()
        ax.legend()
        chart_spot.pyplot(fig)
else:
    st.warning("请先在主页上传数据")
