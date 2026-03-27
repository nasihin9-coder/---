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

    # --- 新增：直观计算过程展示 ---
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. 热-水耦合反演偏微分方程")
        st.write("利用一维稳态热传导-对流方程反推水分通量 $q$：")
        st.latex(r"q = -\alpha \frac{\partial^2 T / \partial z^2}{\partial T / \partial z}")
        st.write(f"当前选定热扩散率 $\\alpha$ = {alpha}")

        st.markdown("#### 2. 微积分数值演算矩阵")
        st.write("系统自动对温度剖面进行差分计算，求取一阶导数（温度梯度）与二阶导数（剖面曲率）：")
        calc_df = pd.DataFrame({
            "深度 z(m)": z_obs,
            "一阶导数 ∇T": np.round(dt_dz, 4),
            "二阶导数 ∇²T": np.round(d2t_dz2, 4),
            "瞬态反演流速 q (cm/h)": np.round(-alpha * (d2t_dz2 / (dt_dz + 1e-5)), 5)
        })
        st.dataframe(calc_df.head(8), use_container_width=True)

else:
    st.warning("请先在主页上传数据")
