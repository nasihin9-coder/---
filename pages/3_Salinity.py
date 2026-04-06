# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import platform

# --- 中文乱码修复 ---
def set_matplot_zh():
    plt.rcParams['axes.unicode_minus'] = False 
    system = platform.system()
    if system == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei']
    elif system == "Darwin":
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

set_matplot_zh()

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合 (倒灌场景)")

# --- 安全检查 ---
if 'df' not in st.session_state or st.session_state['df'] is None:
    st.warning("⚠️ 请先在主页上传数据。")
else:
    df = st.session_state['df']
    z_obs = df[st.session_state.get('z_col', df.columns[0])].values
    s_obs = df[st.session_state.get('s_col', df.columns[2])].values

    # --- 侧边栏：物理参数微调 ---
    st.sidebar.subheader("🛠️ 模型参数微调")
    # 获取全局参数
    dh_init = st.session_state.get('dh', 8.0e-5)
    q_init = st.session_state.get('q', 2.0e-6)

    # 定义盐度运移解析解方程 (一维对流扩散方程)
    # C(z) = C_bottom + (C_surface - C_bottom) * exp(v*z / D)
    def salinity_model(z, c_surface, v_over_d):
        c_bottom = s_obs[-1] # 假设底层盐度固定
        return c_bottom + (c_surface - c_bottom) * np.exp(-v_over_d * (z - z_obs.max()))

    # --- 自动拟合逻辑 ---
    st.sidebar.divider()
    auto_fit = st.sidebar.checkbox("开启参数自动寻优", value=True)

    if auto_fit:
        try:
            # 自动寻找最优的表层盐度和衰减系数
            popt, _ = curve_fit(salinity_model, z_obs, s_obs, p0=[s_obs[0], 2.0])
            c_surf_opt, v_d_opt = popt
            st.sidebar.success(f"最优表层盐度: {c_surf_opt:.1f}")
        except:
            c_surf_opt, v_d_opt = s_obs[0], 1.0
    else:
        c_surf_opt = st.sidebar.number_input("表层背景盐度 (mg/L)", 0, 50000, int(s_obs[0]))
        v_d_opt = st.sidebar.slider("运移强度系数", 0.1, 10.0, 2.0)

    # --- 绘图区域 ---
    if st.button("🚀 开始模型拟合", type="primary"):
        z_sim = np.linspace(z_obs.min(), z_obs.max(), 100)
        s_sim = salinity_model(z_sim, c_surf_opt, v_d_opt)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(s_obs, z_obs, color='gray', alpha=0.6, label='实测盐度数据 (Observed)')
        ax.plot(s_sim, z_sim, color='orange', linewidth=3, label='最优拟合曲线 (Fitted)')
        
        ax.set_xlabel("Salinity / 盐度 (mg/L)")
        ax.set_ylabel("Depth / 深度 (m)")
        ax.invert_yaxis()
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend()
        
        st.pyplot(fig)
        
        # 计算 R2 评价拟合质量
        from sklearn.metrics import r2_score
        s_pred = salinity_model(z_obs, c_surf_opt, v_d_opt)
        r2 = r2_score(s_obs, s_pred)
        
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("拟合度 (R²)", f"{r2:.4f}")
        col2.metric("模型衰减常数", f"{v_d_opt:.3f}")
