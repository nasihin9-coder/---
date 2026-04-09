# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import platform

# --- 1. 字体环境兼容性修复 ---
def set_matplot_zh():
    plt.rcParams['axes.unicode_minus'] = False 
    system = platform.system()
    if system == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei']
    elif system == "Darwin":
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    else:
        # Streamlit Cloud 环境下回退到 DejaVu Sans，避免方框乱码
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

set_matplot_zh()

st.set_page_config(page_title="盐度运移分析", layout="wide")
st.title("🧂 盐度运移模型空间拟合 (海水倒灌)")

# --- 2. 数据安全检查 ---
if 'df' not in st.session_state or st.session_state['df'] is None:
    st.warning("⚠️ 未检测到数据。请先在主页 (app.py) 上传监测数据 CSV 文件。")
else:
    df = st.session_state['df']
    # 自动识别列名
    z_col = st.session_state.get('z_col', df.columns[0])
    s_col = st.session_state.get('s_col', df.columns[2] if len(df.columns)>2 else df.columns[-1])
    
    z_obs = df[z_col].values
    s_obs = df[s_col].values

    # --- 3. 物理模型定义：针对倒灌特征优化 ---
    # 方程逻辑：C(z) = C_surf + (C_bottom - C_surf) * exp(alpha * (z - z_max))
    def salinity_inversion_model(z, c_surf, alpha):
        z_max = z_obs.max()
        c_bottom = s_obs[-1] # 强制锚定底层实测高盐度点
        return c_surf + (c_bottom - c_surf) * np.exp(alpha * (z - z_max))

    # --- 4. 侧边栏：参数自动寻优 ---
    st.sidebar.subheader("🛠️ 模型参数优化")
    auto_fit = st.sidebar.toggle("启用参数自动寻优", value=True)
    
    if auto_fit:
        try:
            # 初始猜测：表层盐度=最小值，衰减系数=2.0
            popt, _ = curve_fit(salinity_inversion_model, z_obs, s_obs, p0=[s_obs.min(), 3.0])
            c_surf_fit, alpha_fit = popt
            st.sidebar.success(f"最优拟合完成！")
        except Exception as e:
            st.sidebar.error(f"寻优失败，请手动调节")
            c_surf_fit, alpha_fit = s_obs.min(), 1.0
    else:
        c_surf_fit = st.sidebar.number_input("手动表层盐度 (mg/L)", 0, 10000, int(s_obs.min()))
        alpha_fit = st.sidebar.slider("手动衰减常数 (alpha)", 0.1, 15.0, 2.0)

    # --- 5. 执行拟合与绘图 ---
    if st.button("🚀 执行模型拟合计算", type="primary"):
        z_sim = np.linspace(z_obs.min(), z_obs.max(), 100)
        s_sim = salinity_inversion_model(z_sim, c_surf_fit, alpha_fit)
        
        # 计算 R2 评价
        s_pred_at_obs = salinity_inversion_model(z_obs, c_surf_fit, alpha_fit)
        r2 = r2_score(s_obs, s_pred_at_obs)

        # 绘图逻辑
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.grid(True, linestyle=':', alpha=0.6)
        
        # 散点与拟合曲线
        ax.scatter(s_obs, z_obs, color='gray', alpha=0.5, s=60, label='Measured')
        ax.plot(s_sim, z_sim, color='orange', linewidth=3, label='Fitted Curve')
        
        # 标签处理（解决乱码并保证跨平台识别）
        ax.set_xlabel("Salinity /(mg/L)")
        ax.set_ylabel("Depth /(m)")
        ax.invert_yaxis() # 深度向下
        ax.legend()
        
        st.pyplot(fig)

        # --- 6. 结果评价看板 ---
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("拟合优度 (R²)", f"{r2:.4f}", delta="正常" if r2 > 0.9 else "偏低")
        m2.metric("模型衰减常数", f"{alpha_fit:.3f}")
        m3.metric("预测表层盐度", f"{c_surf_fit:.1f} mg/L")
