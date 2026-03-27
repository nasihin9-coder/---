# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import time  # 必须导入 time 模块控制动画速度

st.set_page_config(page_title="温度剖面分析", layout="wide")
st.title("🌡️ 温度剖面动态交互分析")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_col = st.session_state['z_col']
    t_col = st.session_state['t_col']
    
    st.sidebar.subheader("📈 绘图配置")
    smooth_level = st.sidebar.slider("曲线平滑度 (Spline K)", 2, 5, 3)
    
    t_obs = df[t_col].values
    z_obs = df[z_col].values

    # 准备高分辨率插值数据
    z_smooth = np.linspace(z_obs.min(), z_obs.max(), 100)
    spl = make_interp_spline(z_obs, t_obs, k=smooth_level)
    t_smooth = spl(z_smooth)

    # 预留动画画布位置
    chart_spot = st.empty() 

    # 点击按钮触发动画绘图
    if st.button("▶️ 播放动态绘图过程 (动画)"):
        fig, ax = plt.subplots(figsize=(10, 6))
        # 固定坐标轴范围，防止动画时画面跳动
        x_min, x_max = min(t_obs)-1, max(t_obs)+1
        y_min, y_max = max(z_obs)+0.1, min(z_obs)-0.1 

        # 阶段 1：逐个打上实测散点
        for i in range(1, len(z_obs) + 1):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            # 画前 i 个点
            ax.scatter(t_obs[:i], z_obs[:i], color='darkred', edgecolors='white', label='Measured')
            chart_spot.pyplot(fig)
            time.sleep(0.05) # 控制打点速度

        # 阶段 2：曲线逐渐延伸
        for i in range(1, len(z_smooth), 3):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            # 保持所有散点
            ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white', label='Measured')
            # 画前 i 段曲线
            ax.plot(t_smooth[:i], z_smooth[:i], color='red', linewidth=2, label='Trend Line')
            chart_spot.pyplot(fig)
            time.sleep(0.02) # 控制曲线生长速度
            
        st.success("✨ 绘图完成！")
        
    else:
        # 默认显示完整静态图
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(t_smooth, z_smooth, color='red', linewidth=2, label='Trend Line')
        ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white', label='Measured')
        ax.invert_yaxis()
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("Depth (m)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        chart_spot.pyplot(fig)
else:
    st.warning("请先在主页上传数据")
