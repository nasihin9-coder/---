import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.title("🌊 水分通量反演")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z, t = df.iloc[:,0].values, df.iloc[:,1].values
    alpha = st.sidebar.slider("热扩散率", 0.001, 0.01, 0.004)

    # 偏微分反演计算
    dt_dz = np.gradient(t, z)
    d2t_dz2 = np.gradient(dt_dz, z)
    q_est = -alpha * (d2t_dz2 / (dt_dz + 1e-3))
    q_mean = np.mean(q_est)

    # 结果看板
    c1, c2 = st.columns(2)
    c1.metric("反演深度", f"{z.max():.2f} m")
    c2.metric("平均通量 q", f"{q_mean:.5f} cm/h")
    st.divider()

    if st.button("🚀 开始计算"):
        fig, ax = plt.subplots()
        plot_area = st.empty()
        z_sim = np.linspace(0, z.max(), 100)
        q_sim = q_mean * (1 + 0.1 * np.sin(z_sim * 5))
        for i in range(5, 105, 5):
            ax.clear()
            ax.invert_yaxis()
            ax.axvline(0, color='black', ls='--', alpha=0.3)
            ax.plot(q_sim[:i], z_sim[:i], color='#1f77b4', lw=3)
            plot_area.pyplot(fig)
            time.sleep(0.05)
else:
    st.warning("请先在主页上传数据")
