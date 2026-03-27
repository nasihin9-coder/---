# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import time

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

    z_smooth = np.linspace(z_obs.min(), z_obs.max(), 100)
    spl = make_interp_spline(z_obs, t_obs, k=smooth_level)
    t_smooth = spl(z_smooth)

    # 1. 核心按钮：开始计算
    calc_btn = st.button("🚀 开始计算", type="primary")
    chart_spot = st.empty() 

    # 2. 状态机逻辑
    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = min(t_obs)-1, max(t_obs)+1
        y_min, y_max = max(z_obs)+0.1, min(z_obs)-0.1 

        for i in range(1, len(z_obs) + 1):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            ax.scatter(t_obs[:i], z_obs[:i], color='darkred', edgecolors='white', label='Measured')
            chart_spot.pyplot(fig)
            time.sleep(0.05)

        for i in range(1, len(z_smooth), 3):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white', label='Measured')
            ax.plot(t_smooth[:i], z_smooth[:i], color='red', linewidth=2, label='Trend Line')
            chart_spot.pyplot(fig)
            time.sleep(0.02)
            
        # 记录计算已完成的状态
        st.session_state['temp_calc_done'] = True
        st.success("✨ 空间场重构计算完成！")
        
    elif st.session_state.get('temp_calc_done'):
        # 计算完成后，保持显示最终静态图
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
        # 初始等待界面
        chart_spot.info("ℹ️ 请调整左侧参数后，点击上方【🚀 开始计算】按钮执行空间场重构与绘图。")

    # (保留您之前的计算过程和绘图过程面板代码即可...)
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. B-Spline 多项式插值原理")
        st.latex(r"S(z) = \sum_{i=0}^{n-1} c_i B_{i, k}(z)")
        dt_dz = np.gradient(t_obs, z_obs)
        calc_df = pd.DataFrame({"观测深度 (m)": z_obs, "实测温度 (°C)": t_obs, "温度梯度 (dT/dz)": np.round(dt_dz, 4)})
        st.dataframe(calc_df.head(5), use_container_width=True)

else:
    st.warning("请先在主页上传数据")
