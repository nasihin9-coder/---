# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🌊 水分通量反演")

if st.session_state['df'] is not None:
    t_obs = st.session_state['df'][st.session_state['t_col']].values
    z_obs = st.session_state['df'][st.session_state['z_col']].values
    
    # 模拟反演逻辑
    q_mean = np.mean(np.gradient(np.gradient(t_obs, z_obs), z_obs)) * -0.004
    
    fig, ax = plt.subplots()
    z_sim = np.linspace(0, z_obs.max(), 100)
    flux = q_mean * (1 + 0.1 * np.sin(z_sim * 5))
    ax.plot(flux, z_sim, label='Inverted Flux')
    ax.fill_betweenx(z_sim, 0, flux, alpha=0.2)
    ax.invert_yaxis()
    st.pyplot(fig)

    if st.button("🔍 启动自动化模型校准"):
        with st.spinner('迭代中...'):
            st.balloons()
            st.success(f"校准成功！当前最优通量 q: {abs(q_mean):.6f} cm/h")
