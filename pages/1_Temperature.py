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
    df, z_col, t_col = st.session_state['df'], st.session_state['z_col'], st.session_state['t_col']
    t_obs, z_obs = df[t_col].values, df[z_col].values
    
    # 看板
    m1, m2, m3 = st.columns(3)
    m1.metric("计算深度跨度", f"{z_obs.min()} - {z_obs.max()} m")
    m2.metric("最高温度", f"{t_obs.max():.1f} °C")
    m3.metric("最低温度", f"{t_obs.min():.1f} °C")
    st.divider()

    z_smooth = np.linspace(z_obs.min(), z_obs.max(), 100)
    spl = make_interp_spline(z_obs, t_obs, k=3)
    t_smooth = spl(z_smooth)

    if st.button("🚀 开始计算", type="primary"):
        chart_spot = st.empty()
        fig, ax = plt.subplots(figsize=(10, 5))
        xlims, ylims = (t_obs.min()-1, t_obs.max()+1), (z_obs.max()+0.1, z_obs.min()-0.1)

        for i in range(2, len(z_obs)+2, 3): # 快速打点
            ax.clear()
            ax.set_xlim(xlims); ax.set_ylim(ylims)
            ax.scatter(t_obs[:i], z_obs[:i], color='darkred', label='Measured')
            chart_spot.pyplot(fig); time.sleep(0.01)

        for i in range(5, 105, 5): # 平滑拉线
            ax.clear()
            ax.set_xlim(xlims); ax.set_ylim(ylims)
            ax.scatter(t_obs, z_obs, color='darkred', alpha=0.3)
            ax.plot(t_smooth[:i], z_smooth[:i], color='red', linewidth=2)
            chart_spot.pyplot(fig); time.sleep(0.01)
        st.session_state['t_done'] = True
else:
    st.warning("请先在主页上传数据")
