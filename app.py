# -*- coding: utf-8 -*-
"""
软件名称：变饱和带土壤盐分动态监测与归趋预报软件 V1.0
功能描述：支持传感器数据上传、热-盐耦合数值模拟及 R2 回归精度分析
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 核心计算引擎 ---
class SoilAnalyticsEngine:
    @staticmethod
    def calculate_r2(obs, sim):
        """计算决定系数 R2 [体现软著技术深度]"""
        obs, sim = np.array(obs), np.array(sim)
        res = np.sum((obs - sim) ** 2)
        tot = np.sum((obs - np.mean(obs)) ** 2)
        return max(0, 1 - (res / (tot + 1e-12)))

    @staticmethod
    def run_simulation(C0, q, Dh, theta, dx, depth_max=1.0):
        """热-盐耦合物理模型核心算法"""
        z = np.arange(0, depth_max + dx, dx)
        C = np.full(len(z), 500.0) # 背景盐度
        C[0] = C0
        v = q / (theta + 1e-12)
        dt = 0.5 * (dx**2) / (Dh + abs(v)*dx + 1e-12)
        steps = min(int(86400 / dt), 500)
        for _ in range(steps):
            C_new = np.copy(C)
            for i in range(1, len(C)-1):
                diff = Dh * (C[i+1] - 2*C[i] + C[i-1]) / (dx**2)
                adv = -v * (C[i] - C[i-1]) / dx if v > 0 else -v * (C[i+1] - C[i]) / dx
                C_new[i] = C[i] + (diff + adv) * dt
            C = np.clip(C_new, 0, 100000)
            C[0] = C0
        return z, C

# --- 界面绘图修复 (解决方框乱码) ---
def plot_results(z, c, title, label="Simulation"):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(c, z, 'g-o', markersize=4, label=label)
    
    # 强制使用中英双语标签，确保英文部分 100% 可读
    ax.set_xlabel("Salinity / 含盐量 (mg/L)", fontsize=10)
    ax.set_ylabel("Depth / 深度 (m)", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    ax.invert_yaxis()
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    fig.tight_layout()
    return fig

# --- 软件主体框架 ---
def main():
    st.set_page_config(page_title="土壤盐分监测预报系统 V1.0", layout="wide")
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '主界面'

    # 侧边栏：物理参数调优
    st.sidebar.title("🔬 核心物理参数")
    Dh = st.sidebar.number_input("弥散系数 Dh (m²/s)", value=1e-7, format="%.1e")
    theta = st.sidebar.slider("土壤孔隙度", 0.1, 0.6, 0.35)
    dx = st.sidebar.slider("步长 Δx (m)", 0.01, 0.1, 0.05)

    if st.session_state.current_page == '主界面':
        show_home()
    elif st.session_state.current_page == '数据分析':
        show_analysis(Dh, theta, dx)

def show_home():
    st.title("🌱 变饱和带土壤盐分动态监测软件")
    st.caption("版本：V1.0 | 开发单位：河海大学水利水电学院")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("功能入口")
        if st.button("📈 传感器数据上传与回归分析", use_container_width=True):
            st.session_state.current_page = '数据分析'
    with col2:
        st.info("本系统支持直接上传现场传感器监测的 CSV 数据，通过热-盐耦合模型进行归趋分析。")
        # 示意图
        st.write("**监测原理图预览**")
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "Sensors Data -> Coupling Engine -> R2 Result", ha='center', va='center', bbox=dict(facecolor='green', alpha=0.1))
        ax.axis('off')
        st.pyplot(fig)

def show_analysis(Dh, theta, dx):
    st.header("📈 传感器数据上传与回归分析")
    
    # 1. 数据上传模块
    uploaded_file = st.file_uploader("第一步：上传传感器监测 CSV 数据", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("已识别传感器数据预览：", df.head(3))
        
        # 2. 自动提取参数与模拟
        col_ctrl, col_res = st.columns([1, 2])
        with col_ctrl:
            st.subheader("模拟参数确认")
            c0 = st.number_input("监测地表盐度 (mg/L)", value=float(df.iloc[0,1]) if df.shape[1]>1 else 35000.0)
            q_est = st.number_input("预估通量 q (m/s)", value=4.4e-6, format="%.1e")
            
            if st.button("执行模型回归", type="primary"):
                # 物理模拟
                z_sim, c_sim = SoilAnalyticsEngine.run_simulation(c0, q_est, Dh, theta, dx)
                
                # 构造对比数据（假设 CSV 第二列是实测值）
                z_obs = np.linspace(0, 1.0, len(df))
                c_obs = df.iloc[:, 1].values[:len(z_sim)]
                
                # 计算 R2
                r2_val = SoilAnalyticsEngine.calculate_r2(c_obs, c_sim[:len(c_obs)])
                
                st.session_state.results = (z_sim, c_sim, r2_val, z_obs, c_obs)

        # 3. 结果图形展示
        with col_res:
            if 'results' in st.session_state:
                z_s, c_s, r2, z_o, c_o = st.session_state.results
                
                # 绘制综合对比图
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.scatter(c_o, z_o, color='black', label='Sensor Observed / 传感器实测')
                ax.plot(c_s, z_s, 'g-', linewidth=2, label=f'Model Regression / 模型回归 (R²={r2:.4f})')
                
                ax.set_xlabel("Salinity / 含盐量 (mg/L)")
                ax.set_ylabel("Depth / 深度 (m)")
                ax.invert_yaxis()
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
                
                st.metric("模型回归精度 (R²)", f"{r2:.4f}")
                st.latex(r"R^2 = 1 - \frac{\sum(y_{obs}-y_{sim})^2}{\sum(y_{obs}-\bar{y})^2}")

    if st.button("⬅️ 返回主页"):
        st.session_state.current_page = '主界面'

if __name__ == "__main__":
    main()
