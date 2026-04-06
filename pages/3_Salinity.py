# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from sklearn.metrics import r2_score

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合 (倒灌场景)")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_col = st.session_state.get('z_col', df.columns[0])
    s_col = st.session_state.get('s_col', df.columns[2] if len(df.columns)>2 else df.columns[-1])
    z_obs, c_obs = df[z_col].values, df[s_col].values
    dh = st.session_state.get('dh', 8.0e-5)
    
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("表层背景盐度 (mg/L)", 200, 5000, 1200)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    # 物理模型：稳态对流-弥散解析解
    z_max = z_obs.max()
    z_sim = np.linspace(0, z_max, 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_bottom = c_obs[-1]
    c_sim = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_sim))
    
    if st.button("🚀 开始模型拟合", type="primary"):
        chart_spot = st.empty()
        fig, ax = plt.subplots(figsize=(10, 6))
        for i in range(len(z_sim)-1, -1, -5):
            ax.clear()
            ax.invert_yaxis()
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
            ax.plot(c_sim[i:], z_sim[i:], color='darkorange', linestyle=styles[line_style], linewidth=3)
            chart_spot.pyplot(fig)
            time.sleep(0.01)
        st.session_state['sal_calc_done'] = True
        plt.close(fig)

    # --- 结果看板模块 ---
    if st.session_state.get('sal_calc_done'):
        st.divider()
        st.subheader("📊 拟合性能看板")
        c_theory = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_obs))
        r2 = r2_score(c_obs, c_theory)
        mae = np.mean(np.abs(c_obs - c_theory))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("拟合优度 (R²)", f"{max(0, r2):.4f}")
        col2.metric("平均残差 (MAE)", f"{mae:.2f} mg/L")
        col3.metric("弥散系数 (Dh)", f"{dh:.1e}")

        with st.expander("🧮 物理方程与原始数据"):
            st.latex(r"C(z) = C_{surf} + (C_{bottom} - C_{surf}) \cdot \exp\left(-\frac{v}{D_h} (Z_{max} - z)\right)")
            st.dataframe(pd.DataFrame({"深度": z_obs, "实测": c_obs, "预测": np.round(c_theory, 1)}))
else:
    st.warning("请先在主页上传数据")
