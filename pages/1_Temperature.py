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

    # 1. 计算过程面板
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. B-Spline 多项式插值原理")
        st.latex(r"S(z) = \sum_{i=0}^{n-1} c_i B_{i, k}(z)")
        
        dt_dz = np.gradient(t_obs, z_obs)
        calc_df = pd.DataFrame({"观测深度 (m)": z_obs, "实测温度 (°C)": t_obs, "温度梯度 (dT/dz)": np.round(dt_dz, 4)})
        st.dataframe(calc_df.head(5), use_container_width=True)

    # 2. 新增：可视化渲染过程面板
    with st.expander("🎨 展开查看图表渲染与可视化绘制过程"):
        st.markdown("#### 1. 多图层叠加渲染引擎 (Layered Rendering)")
        st.write("系统前端采用 Matplotlib 引擎，通过分离图层实现数据可视化重构：")
        st.markdown("- **底层 (Base Layer)**：构建 10x6 英寸画布，初始化 X轴(温度) 与 Y轴(深度)，并开启 `alpha=0.3` 的背景网格。")
        st.markdown("- **数据层 (Data Layer)**：将离散传感器矩阵映射为 `ax.scatter` 散点图，设定标记颜色为 `darkred` 并带有白色描边以增强对比度。")
        st.markdown("- **拟合层 (Trend Layer)**：将 B-Spline 生成的 300 个高分辨率插值点组装成 `ax.plot` 连续曲线。")
        st.markdown("- **坐标系变换**：执行 `ax.invert_yaxis()` 指令，将 Y 轴零点置于顶端，完美符合实际土壤地质深度的物理直觉。")
        
        st.markdown("#### 2. 核心 UI 渲染代码摘要")
        st.code('''# 前端可视化绘图指令流
fig, ax = plt.subplots(figsize=(10, 6))
# 图层 1: 绘制插值平滑曲线 (红线)
ax.plot(spl(z_smooth), z_smooth, color='red', label='Trend Line')
# 图层 2: 叠加原始实测散点 (暗红色)
ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white')
# 图层 3: 地质坐标系翻转与网格激活
ax.invert_yaxis() 
ax.grid(True, alpha=0.3)
# 推送至 Streamlit 前端渲染
st.pyplot(fig)''', language="python")

else:
    st.warning("请先在主页上传数据")
