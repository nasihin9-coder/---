# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

st.set_page_config(page_title="温度剖面分析", layout="wide")
st.title("🌡️ 温度剖面动态交互分析")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_col = st.session_state['z_col']
    t_col = st.session_state['t_col']
    
    st.sidebar.subheader("📈 绘图配置")
    smooth_level = st.sidebar.slider("曲线平滑度 (Spline K)", 2, 5, 3)
    depth_range = st.sidebar.slider("观测深度范围 (m)", 0.0, float(df[z_col].max()), (0.0, 1.0))
    
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

    # --- 新增：直观计算过程展示 ---
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. B-Spline 多项式插值原理")
        st.write("系统采用 SciPy 底层算法将离散传感器点位拟合为连续物理场。平滑度 K 决定了多项式的阶数：")
        st.latex(r"S(z) = \sum_{i=0}^{n-1} c_i B_{i, k}(z)")
        
        st.markdown("#### 2. 实时地温梯度 (dT/dz) 演算矩阵")
        # 计算梯度
        dt_dz = np.gradient(t_obs, z_obs)
        calc_df = pd.DataFrame({
            "观测深度 (m)": z_obs,
            "实测温度 (°C)": t_obs,
            "温度梯度 (dT/dz)": np.round(dt_dz, 4)
        })
        st.dataframe(calc_df.head(8), use_container_width=True)
        st.info("💡 物理意义：梯度绝对值越大，代表该深度的土壤热传导交换越剧烈。")

else:
    st.warning("请先在主页上传数据")
