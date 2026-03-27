# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合")

if 'df' in st.session_state and st.session_state['df'] is not None:
    df = st.session_state['df']
    z_col = st.session_state.get('z_col', 'Depth(m)')
    s_col = st.session_state.get('s_col', 'Salinity')
    
    # 获取全局参数
    dh = st.session_state.get('dh', 8.0e-5)
    
    # --- 交互组件 ---
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("深层背景盐度 (mg/L)", 200, 2000, 500)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    c_obs = df[s_col].values
    z_obs = df[z_col].values
    
    z_sim = np.linspace(0, z_obs.max(), 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_sim = c_base + (c_obs[0] - c_base) * np.exp(-k_factor * z_sim)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
    ax.plot(c_sim, z_sim, color='green', linestyle=styles[line_style], linewidth=3, label='Model')
    ax.invert_yaxis()
    ax.legend()
    st.pyplot(fig)
    
    # 增加导出交互
    st.download_button("📥 导出拟合数据", df.to_csv().encode('utf-8'), "fitted_data.csv", "text/csv")
