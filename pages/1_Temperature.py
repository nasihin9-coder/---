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

    calc_btn = st.button("🚀 开始计算", type="primary")
    chart_spot = st.empty() 

    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = min(t_obs)-1, max(t_obs)+1
        y_min, y_max = max(z_obs)+0.1, min(z_obs)-0.1 

        # 阶段1：快速渲染实测散点 (加大步长，减少卡顿)
        step_scatter = max(2, len(z_obs) // 5)
        for i in range(step_scatter, len(z_obs) + step_scatter, step_scatter):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            ax.scatter(t_obs[:i], z_obs[:i], color='darkred', edgecolors='white', label='Measured')
            chart_spot.pyplot(fig)
            time.sleep(0.01)

        # 阶段2：平滑高速拉出拟合曲线
        step_line = max(2, len(z_smooth) // 20)
        for i in range(step_line, len(z_smooth) + step_line, step_line):
            current_i = min(i, len(z_smooth))
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white', label='Measured')
            ax.plot(t_smooth[:current_i], z_smooth[:current_i], color='red', linewidth=2, label='Trend Line')
            chart_spot.pyplot(fig)
            time.sleep(0.01)
            
        st.session_state['temp_calc_done'] = True
        st.success("✨ 空间场重构计算完成！")
        plt.close(fig)
        
    elif st.session_state.get('temp_calc_done'):
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
        chart_spot.info("ℹ️ 请调整左侧参数后，点击上方【🚀 开始计算】按钮执行空间场重构与绘图。")

    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. B-Spline 多项式插值原理")
        st.latex(r"S(z) = \sum_{i=0}^{n-1} c_i B_{i, k}(z)")
        dt_dz = np.gradient(t_obs, z_obs)
        calc_df = pd.DataFrame({"观测深度 (m)": z_obs, "实测温度 (°C)": t_obs, "温度梯度 (dT/dz)": np.round(dt_dz, 4)})
        st.dataframe(calc_df.head(5), use_container_width=True)

else:
    st.warning("请先在主页上传数据")
# ... (前面导入和绘图代码保持不变)
    if st.button("🚀 开始计算", type="primary"):
        # ... (动画循环代码)
        
        # --- 页面底部结果看板 ---
        st.divider()
        st.subheader("📊 计算结果摘要")
        cols = st.columns(2)
        
        # 计算 R2 精度
        from sklearn.metrics import r2_score
        t_pred = spl(z_obs)
        r2 = r2_score(t_obs, t_pred)
        
        cols[0].metric("最大计算深度", f"{z_obs.max():.2f} m")
        cols[1].metric("拟合精度 (R²)", f"{r2:.4f}")
