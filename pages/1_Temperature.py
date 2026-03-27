# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

st.set_page_config(page_title="温度剖面分析", layout="wide")
st.title("🌡️ 温度剖面动态交互分析")

if 'df' in st.session_state and st.session_state['df'] is not None:
    df = st.session_state['df']
    z_col = st.session_state.get('z_col', 'Depth(m)')
    t_col = st.session_state.get('t_col', 'Temperature')
    
    # --- 交互组件 ---
    st.sidebar.subheader("📈 绘图配置")
    smooth_level = st.sidebar.slider("曲线平滑度 (Spline K)", 2, 5, 3)
    depth_range = st.sidebar.slider("观测深度范围 (m)", 0.0, float(df[z_col].max()), (0.0, 1.0))
    
    # 数据筛选
    mask = (df[z_col] >= depth_range[0]) & (df[z_col] <= depth_range[1])
    df_filtered = df[mask]
    
    t_obs = df_filtered[t_col].values
    z_obs = df_filtered[z_col].values

    fig, ax = plt.subplots(figsize=(10, 6))
    if len(t_obs) > smooth_level:
        z_smooth = np.linspace(z_obs.min(), z_obs.max(), 300)
        spl = make_interp_spline(z_obs, t_obs, k=smooth_level)
        ax.plot(spl(z_smooth), z_smooth, color='red', label='Trend Line')
    
    ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white', label='Measured')
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Depth (m)")
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("请先在主页上传数据")
