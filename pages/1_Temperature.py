# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from sklearn.metrics import r2_score
import time

st.set_page_config(page_title="温度剖面分析", layout="wide")
st.title("🌡️ 温度剖面动态交互分析")

if st.session_state.get('df') is not None:
    df, z_col, t_col = st.session_state['df'], st.session_state['z_col'], st.session_state['t_col']
    t_obs, z_obs = df[t_col].values, df[z_col].values
    
    # 计算拟合与准确度
    z_smooth = np.linspace(z_obs.min(), z_obs.max(), 100)
    spl = make_interp_spline(z_obs, t_obs, k=3)
    t_pred_at_obs = spl(z_obs)
    r2 = r2_score(t_obs, t_pred_at_obs)

    # 结果看板
    m1, m2, m3 = st.columns(3)
    m1.metric("最大计算深度", f"{z_obs.max():.2f} m")
    m2.metric("拟合准确度 (R²)", f"{r2:.4f}")
    m3.metric("温度极值", f"{t_obs.min():.1f} - {t_obs.max():.1f} °C")
    st.divider()

    if st.button("🚀 开始计算", type="primary"):
        chart_spot = st.empty()
        fig, ax = plt.subplots(figsize=(10, 5))
        t_smooth = spl(z_smooth)
        
        for i in range(5, 105, 5):
            ax.clear()
            ax.set_xlim(t_obs.min()-1, t_obs.max()+1)
            ax.set_ylim(z_obs.max()+0.1, z_obs.min()-0.1)
            ax.scatter(t_obs, z_obs, color='darkred', alpha=0.3, label='Measured')
            ax.plot(t_smooth[:i], z_smooth[:i], color='red', linewidth=2, label='Spline Fit')
            chart_spot.pyplot(fig)
            time.sleep(0.01)
else:
    st.warning("请先在主页上传数据")
