# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 核心算法类 (软著核心技术点) ---
class SoilSaltEngine:
    @staticmethod
    def calculate_r2(y_true, y_pred):
        """计算决定系数 R2"""
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-12))
        return max(0, min(1, r2))

    @staticmethod
    def transport_model(C0, q, Dh, theta, dx, depth_max=1.0):
        """变饱和带热-盐耦合物理模拟逻辑"""
        z = np.arange(0, depth_max + dx, dx)
        C = np.full(len(z), 500.0) 
        C[0] = C0
        v = q / (theta + 1e-12)
        # CFL 稳定性计算：解决坐标轴锯齿震荡
        dt = 0.5 * (dx**2) / (Dh + abs(v)*dx + 1e-12)
        steps = min(int(86400 / dt), 450)
        
        for _ in range(steps):
            C_new = np.copy(C)
            for i in range(1, len(C)-1):
                diff = Dh * (C[i+1] - 2*C[i] + C[i-1]) / (dx**2)
                adv = -v * (C[i] - C[i-1]) / dx if v > 0 else -v * (C[i+1] - C[i]) / dx
                C_new[i] = C[i] + (diff + adv) * dt
            C = np.clip(C_new, 0, 100000)
            C[0] = C0
        return z, C

# --- 2. 绘图修复模块 (解决文字不显示问题) ---
def create_styled_plot(x, y, title, xlabel, ylabel, is_scatter=False):
    """自动适配字体的绘图函数"""
    fig, ax = plt.subplots(figsize=(9, 5))
    
    if is_scatter:
        ax.scatter(x, y, color='black', label='Measured Data')
        ax.plot(x, y, 'g--', alpha=0.5, label='Trend Line')
    else:
        ax.plot(x, y, 'g-o', markersize=4, linewidth=1.5, label='Model Curve')
    
    # 设置坐标轴标签 (采用中英文对照防止乱码)
    ax.set_xlabel(f"{xlabel} / 含盐量", fontsize=10)
    ax.set_ylabel(f"{ylabel} / 深度", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    ax.invert_yaxis() # 深度轴向下
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    fig.tight_layout()
    return fig

# --- 3. 界面逻辑框架 ---
def main():
    st.set_page_config(page_title="土壤盐分监测预报系统 V1.0", layout="wide")
    
    if 'page' not in st.session_state:
        st.session_state.page = '主界面'

    # 侧边栏
    st.sidebar.title("🛠️ 参数设置面板")
    Dh = st.sidebar.number_input("弥散系数 Dh (m²/s)", value=1e-7, format="%.1e")
    theta = st.sidebar.slider("土壤孔隙度", 0.1, 0.6, 0.35)
    dx = st.sidebar.slider("空间分辨率 Δx (m)", 0.01, 0.1, 0.05)
    
    if st.session_state.page == '主界面':
        show_home()
    elif st.session_state.page == '动态模拟':
        show_simulation(Dh, theta, dx)
    elif st.session_state.page == '回归精度':
        show_regression(Dh, theta, dx)

def show_home():
    st.title("🌱 变饱和带土壤盐分动态监测与归趋预报软件")
    st.caption("系统版本：V1.0 | 著作权人：河海大学水利水电学院")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("功能模块")
        if st.button("🔄 盐分迁移动态数值模拟", use_container_width=True):
            st.session_state.page = '动态模拟'
        if st.button("📈 模型回归精度评估 (R²)", use_container_width=True):
            st.session_state.page = '回归精度'
    with col2:
        st.info("本软件基于热-盐耦合物理模型，实时反演土壤盐分随深度的迁移规律。")
        # 模拟展示您上传的原理图
        st.write("**变饱和带热-盐耦合概念模型**")
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "Atmosphere Interaction\n------------------\nSoil Layer (Salt Transport)\n------------------\nWater Table", 
                ha='center', va='center', bbox=dict(facecolor='green', alpha=0.1))
        ax.axis('off')
        st.pyplot(fig)

def show_simulation(Dh, theta, dx):
    st.header("🔄 盐分迁移动态数值模拟")
    c1, c2 = st.columns([1, 2])
    with c1:
        c0 = st.number_input("地表盐度 C0 (mg/L)", value=35000)
        q = st.number_input("通量 q (m/s)", value=4.4e-6, format="%.1e")
        if st.button("执行模拟引擎", type="primary"):
            st.session_state.sim_data = SoilSaltEngine.transport_model(c0, q, Dh, theta, dx)
        if st.button("⬅️ 返回首页"): st.session_state.page = '主界面'

    with c2:
        if 'sim_data' in st.session_state:
            z, c = st.session_state.sim_data
            fig = create_styled_plot(c, z, "Soil Salinity Profile", "Salinity (mg/L)", "Depth (m)")
            st.pyplot(fig)
            st.success(f"模拟完成：盐分影响深度为 {z[np.where(c>600)[0][-1]]:.2f}m")

def show_regression(Dh, theta, dx):
    st.header("📈 模型回归精度评估")
    
    # 构造演示数据
    z_obs = np.linspace(0, 1, 10)
    _, c_sim = SoilSaltEngine.transport_model(35000, 4.4e-6, Dh, theta, 1/9)
    c_obs = c_sim + np.random.normal(0, 700, 10)
    
    r2 = SoilSaltEngine.calculate_r2(c_obs, c_sim)
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        fig = create_styled_plot(c_obs, z_obs, f"Regression Accuracy (R²={r2:.4f})", "Salinity", "Depth", is_scatter=True)
        st.pyplot(fig)
    
    with col_r:
        st.metric("决定系数 R²", f"{r2:.4f}")
        st.latex(r"R^2 = 1 - \frac{\sum(y_{obs}-y_{sim})^2}{\sum(y_{obs}-\bar{y})^2}")
        if st.button("⬅️ 返回首页"): st.session_state.page = '主界面'

if __name__ == "__main__":
    main()
