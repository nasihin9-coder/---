# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_obs = df[st.session_state['z_col']].values
    c_obs = df[st.session_state['s_col']].values
    dh = st.session_state.get('dh', 8.0e-5)
    
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("深层背景盐度 (mg/L)", 200, 2000, 500)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    z_sim = np.linspace(0, z_obs.max(), 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_sim = c_base + (c_obs[0] - c_base) * np.exp(-k_factor * z_sim)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
    ax.plot(c_sim, z_sim, color='green', linestyle=styles[line_style], linewidth=3, label='Model')
    ax.set_xlabel("Salinity")
    ax.set_ylabel("Depth (m)")
    ax.invert_yaxis()
    ax.legend()
    st.pyplot(fig)
    st.download_button("📥 导出拟合数据", df.to_csv().encode('utf-8'), "fitted_data.csv", "text/csv")
    
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. 溶质运移对流-弥散方程 (解析解)")
        st.write("基于一维稳定流场条件下的盐分衰减模型：")
        st.latex(r"C(z) = C_{base} + (C_0 - C_{base}) \cdot \exp\left(-\frac{v}{D_h} z\right)")
        
        # ⬅️ 修复了这里的 f-string 双大括号问题
        st.write(f"当前输入参数：表层初始浓度 $C_0$={c_obs[0]:.1f}, 背景浓度 $C_{{base}}$={c_base}, 动力学系数 K={k_factor:.4f}")
        
        st.markdown("#### 2. 模型拟合残差 (Residual) 对比验证表")
        c_theory = c_base + (c_obs[0] - c_base) * np.exp(-k_factor * z_obs)
        error = np.abs(c_obs - c_theory)
        
        residual_df = pd.DataFrame({
            "深度 z(m)": z_obs,
            "传感器实测值 (mg/L)": c_obs,
            "物理模型理论值 (mg/L)": np.round(c_theory, 1),
            "绝对残差 |Δ|": np.round(error, 1)
        })
        st.dataframe(residual_df.head(8), use_container_width=True)
else:
    st.warning("请先在主页上传数据")
