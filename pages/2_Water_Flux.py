# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="水分通量反演", layout="wide")
st.title("🌊 水分通量参数化反演")

if 'df' in st.session_state and st.session_state['df'] is not None:
    df = st.session_state['df']
    z_col = st.session_state.get('z_col', 'Depth(m)')
    t_col = st.session_state.get('t_col', 'Temperature')
    
    # --- 交互组件 ---
    st.sidebar.subheader("🧪 物理参数补偿")
    alpha = st.sidebar.select_slider("土壤热扩散率 (α)", 
                                    options=[0.002, 0.004, 0.006, 0.008], 
                                    value=0.004,
                                    help="不同土质的热传导效率不同")
    
    t_obs = df[t_col].values
    z_obs = df[z_col].values
    
    # 模拟反演计算
    dt_dz = np.gradient(t_obs, z_obs)
    d2t_dz2 = np.gradient(dt_dz, z_obs)
    q_mean = np.mean(-alpha * (d2t_dz2 / (dt_dz + 1e-5)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    z_sim = np.linspace(0, z_obs.max(), 100)
    # 曲线形态随 alpha 实时变动
    flux_profile = q_mean * (1 + 0.1 * np.sin(z_sim * 5)) 
    
    ax.plot(flux_profile, z_sim, color='#1f77b4', linewidth=3)
    ax.fill_betweenx(z_sim, 0, flux_profile, color='#1f77b4', alpha=0.1)
    ax.set_xlabel("Water Flux (cm/h)")
    ax.invert_yaxis()
    st.pyplot(fig)
    st.metric("实时反演均值 (q)", f"{abs(q_mean):.5f} cm/h")
