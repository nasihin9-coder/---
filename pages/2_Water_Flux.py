# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
    
    fig, ax = plt.subplots(figsize=(10, 6))
    z_sim = np.linspace(0, z_obs.max(), 100)
    flux_profile = q_mean * (1 + 0.1 * np.sin(z_sim * 5)) 
    
    ax.plot(flux_profile, z_sim, color='#1f77b4', linewidth=3, label='Inverted Water Flux')
    ax.fill_betweenx(z_sim, 0, flux_profile, color='#1f77b4', alpha=0.1)
    ax.set_xlabel("Water Flux (cm/h)")
    ax.set_ylabel("Depth (m)")
    ax.invert_yaxis()
    ax.legend()
    st.pyplot(fig)
    
    st.metric("实时反演均值 (q)", f"{abs(q_mean):.5f} cm/h")

    # 1. 计算过程面板
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.latex(r"q = -\alpha \frac{\partial^2 T / \partial z^2}{\partial T / \partial z}")
        calc_df = pd.DataFrame({"深度 z(m)": z_obs, "一阶导数 ∇T": np.round(dt_dz, 4), "瞬态反演流速 q": np.round(-alpha * (d2t_dz2 / (dt_dz + 1e-5)), 5)})
        st.dataframe(calc_df.head(5), use_container_width=True)

    # 2. 新增：可视化渲染过程面板
    with st.expander("🎨 展开查看图表渲染与可视化绘制过程"):
        st.markdown("#### 1. 矢量阴影与多边形闭合填充算法")
        st.write("为了直观展示水分通量的体积规模与方向，本页面的视图渲染引入了区域填充技术：")
        st.markdown("- **扰动包络线**：首先，系统通过正弦函数 `0.1 * sin(z_sim * 5)` 为通量均值增加空间微扰，绘制出具有动态美感的主曲线 (`ax.plot`)。")
        st.markdown("- **面积积分可视化**：调用 `fill_betweenx` 算法。引擎以 $X=0$ (零通量中轴线) 为边界，以当前通量曲线为包络面，生成一个闭合多边形，并注入淡蓝色（`alpha=0.1`）进行矢量填充。")
        st.markdown("- 这种渲染方式让单调的线条转化为具有“实体感”的水流通量带，极大地增强了物理现象的视觉表现力。")
        
        st.markdown("#### 2. 面积填充区域渲染指令")
        st.code('''# 生成带有空间波动的通量特征线
flux_profile = q_mean * (1 + 0.1 * np.sin(z_sim * 5)) 

# 渲染主特征线 (深蓝色线条)
ax.plot(flux_profile, z_sim, color='#1f77b4', linewidth=3)

# 核心渲染: 绘制 X=0 到 flux_profile 之间的半透明面积阴影
ax.fill_betweenx(z_sim, 0, flux_profile, color='#1f77b4', alpha=0.1)
''', language="python")

else:
    st.warning("请先在主页上传数据")
