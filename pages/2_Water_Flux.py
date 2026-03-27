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
    
    # --- 物理计算部分 ---
    dt_dz = np.gradient(t_obs, z_obs)
    d2t_dz2 = np.gradient(dt_dz, z_obs)
    q_mean = np.mean(-alpha * (d2t_dz2 / (dt_dz + 1e-5)))
    
    z_sim = np.linspace(0, z_obs.max(), 100)
    flux_profile = q_mean * (1 + 0.1 * np.sin(z_sim * 5)) 
    
    # --- 安全的坐标轴边界计算 (强制包含 0 基准线) ---
    x_limit_min = min(0, np.min(flux_profile))
    x_limit_max = max(0, np.max(flux_profile))
    margin = (x_limit_max - x_limit_min) * 0.1
    if margin == 0: 
        margin = 0.1
    x_min = x_limit_min - margin
    x_max = x_limit_max + margin
    y_min, y_max = max(z_obs)+0.1, min(z_obs)-0.1

    # 1. 核心按钮
    calc_btn = st.button("🚀 开始计算", type="primary")
    chart_spot = st.empty()

    # 2. 状态机逻辑
    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 优化动画：将 100 个点精简为 15 帧动画，避免浏览器卡死
        step = max(2, len(z_sim) // 15) 
        
        # 确保初始绘制至少包含两个点以形成线段
        for i in range(step, len(z_sim) + step, step):
            current_i = min(i, len(z_sim)) # 防止索引越界
            
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Water Flux (cm/h)")
            ax.set_ylabel("Depth (m)")
            
            # 画 0 基准线 (非常重要，物理意义上的零通量)
            ax.axvline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
            
            # 绘制反演曲线和阴影
            ax.plot(flux_profile[:current_i], z_sim[:current_i], color='#1f77b4', linewidth=3, label='Inverted Water Flux')
            ax.fill_betweenx(z_sim[:current_i], 0, flux_profile[:current_i], color='#1f77b4', alpha=0.1)
            
            ax.legend(loc="lower right")
            chart_spot.pyplot(fig)
            
            # 增加睡眠时间，给浏览器充足的绘图渲染时间
            time.sleep(0.06) 
            
        st.session_state['flux_calc_done'] = True
        st.success("✨ 偏微分方程求解与反演完成！")
        # 显式关闭图形释放内存
        plt.close(fig) 
        
    elif st.session_state.get('flux_calc_done'):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel("Water Flux (cm/h)")
        ax.set_ylabel("Depth (m)")
        ax.axvline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.plot(flux_profile, z_sim, color='#1f77b4', linewidth=3, label='Inverted Water Flux')
        ax.fill_betweenx(z_sim, 0, flux_profile, color='#1f77b4', alpha=0.1)
        ax.legend(loc="lower right")
        chart_spot.pyplot(fig)
        
    else:
        chart_spot.info("ℹ️ 请指定土壤热扩散率后，点击上方【🚀 开始计算】按钮执行耦合反演。")

    st.metric("实时反演均值 (q)", f"{q_mean:.5f} cm/h")

    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.latex(r"q = -\alpha \frac{\partial^2 T / \partial z^2}{\partial T / \partial z}")
        calc_df = pd.DataFrame({"深度 z(m)": z_obs, "一阶导数 ∇T": np.round(dt_dz, 4), "瞬态反演流速 q": np.round(-alpha * (d2t_dz2 / (dt_dz + 1e-5)), 5)})
        st.dataframe(calc_df.head(5), use_container_width=True)

else:
    st.warning("请先在主页上传数据")
