# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

st.title("🌡️ 温度剖面分析")

if st.session_state['df'] is not None:
    df = st.session_state['df']
    z_obs = df[st.session_state['z_col']].values
    t_obs = df[st.session_state['t_col']].values

    # 绘图逻辑
    fig, ax = plt.subplots()
    z_smooth = np.linspace(z_obs.min(), z_obs.max(), 300)
    ax.plot(make_interp_spline(z_obs, t_obs, k=3)(z_smooth), z_smooth, color='red', label='Trend')
    ax.scatter(t_obs, z_obs, color='darkred', label='Measured')
    ax.invert_yaxis()
    st.pyplot(fig)

    # 计算操作按钮
    if st.button("🚀 执行地温梯度计算"):
        grad = np.gradient(t_obs, z_obs)
        st.line_chart(pd.DataFrame({'Gradient': grad}, index=z_obs))
        st.success("计算完成：揭示了热传导随深度的变化率。")
