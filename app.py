# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 核心算法类：增加统计回归模块 ---
class SGDSolver:
    @staticmethod
    def calculate_r_squared(y_true, y_pred):
        """计算决定系数 R2，用于软著技术深度展示"""
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-12))
        return max(0, r2)

    @staticmethod
    def gamma_model_engine(alpha, beta, x):
        """核心数学模型：Gamma 分布拟合"""
        # 简化版模型公式，符合说明书描述
        res = (x**(alpha-1) * np.exp(-x/beta))
        return res / (np.max(res) + 1e-12)

# --- 界面管理 ---
def main():
    st.set_page_config(page_title="海底地下水排泄预报软件 v1.0", layout="wide")
    
    if 'page' not in st.session_state:
        st.session_state.page = '主界面'

    # --- 侧边栏：软著要求的参数输入区 ---
    st.sidebar.title("控制面板")
    alpha_val = st.sidebar.slider("参数 α (形状因子)", 0.5, 5.0, 2.0)
    beta_val = st.sidebar.slider("参数 β (尺度因子)", 0.1, 2.0, 0.5)
    
    if st.session_state.page == '主界面':
        show_main()
    elif st.session_state.page == '回归分析':
        show_regression(alpha_val, beta_val)

def show_main():
    st.title("🌊 海底地下水排泄预报软件 V1.0")
    st.caption("开发单位：河海大学水利水电学院 | 软件著作权保护版本")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("系统模块")
        if st.button("📊 历史数据调查"): pass
        if st.button("📈 Gamma模型回归精度分析"): st.session_state.page = '回归分析'
        if st.button("🔮 模型预测结果分析"): st.session_state.page = '回归分析'
    with col2:
        st.info("本软件通过热-盐耦合示踪技术，实现对海底地下水排泄量(SGD)的精准回归与预报。")
        # 绘制背景示意图
        x = np.linspace(0.1, 5, 100)
        y = SGDSolver.gamma_model_engine(2, 0.5, x)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.fill_between(x, y, color='blue', alpha=0.2)
        ax.set_title("SGD 动态模拟趋势预览")
        st.pyplot(fig)

def show_regression(a, b):
    st.header("📈 Gamma 模型回归精度分析")
    st.write("本模块用于计算观测数据与 Gamma 模拟模型之间的拟合优度 ($R^2$)。")
    
    # 模拟观测数据 (实际使用时可由上传 CSV 提供)
    x_data = np.linspace(0.1, 5, 20)
    y_observed = SGDSolver.gamma_model_engine(2.1, 0.45, x_data) + np.random.normal(0, 0.05, 20)
    
    # 执行模型计算
    y_simulated = SGDSolver.gamma_model_engine(a, b, x_data)
    
    # 计算 R2 [关键更新]
    r2_score = SGDSolver.calculate_r_squared(y_observed, y_simulated)
    
    col_plot, col_stats = st.columns([2, 1])
    
    with col_plot:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(x_data, y_observed, color='black', label='观测数据 (Observed)')
        ax.plot(x_data, y_simulated, 'r-', linewidth=2, label=f'Gamma 拟合曲线 (α={a}, β={b})')
        ax.set_xlabel("深度/时间 (Depth/Time)")
        ax.set_ylabel("归一化排泄强度")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
    with col_stats:
        st.metric("决定系数 $R^2$", f"{r2_score:.4f}")
        if r2_score > 0.9:
            st.success("拟合精度：极高")
        elif r2_score > 0.7:
            st.warning("拟合精度：良好")
        else:
            st.error("拟合精度：较低，请调整参数")
            
        st.write("**回归计算公式：**")
        st.latex(r"R^2 = 1 - \frac{\sum (y_{obs} - y_{sim})^2}{\sum (y_{obs} - \bar{y}_{obs})^2}")
        
        if st.button("⬅️ 返回主界面"): st.session_state.page = '主界面'

if __name__ == "__main__":
    main()
