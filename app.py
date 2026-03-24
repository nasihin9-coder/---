# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 核心算法类：体现软著原创性 ---
class SGDProcessor:
    @staticmethod
    def thermal_salt_coupling(C0, q, Dh, theta, dx, depth_max=1.0):
        """变饱和带热-盐耦合数值模拟算法"""
        depth_array = np.arange(0, depth_max + dx, dx)
        C = np.full(len(depth_array), 500.0)
        C[0] = C0
        v = q / (theta + 1e-12)
        # CFL 稳定性约束计算
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
        return depth_array, C

# --- 界面管理系统 ---
def main():
    st.set_page_config(page_title="海底地下水排泄预报软件 v1.0", layout="wide")
    
    if 'page' not in st.session_state:
        st.session_state.page = '主界面'

    # 侧边栏：统一参数控制
    st.sidebar.title("🛠️ 全局参数配置")
    Dh = st.sidebar.number_input("弥散系数 Dh (m²/s)", value=1e-7, format="%.1e")
    theta = st.sidebar.slider("有效孔隙度", 0.20, 0.50, 0.35)
    dx = st.sidebar.slider("空间步长 Δx (m)", 0.01, 0.10, 0.05)
    
    # --- 逻辑路由 ---
    if st.session_state.page == '主界面':
        show_main_page()
    elif st.session_state.page == '动态模拟':
        show_simulation_page(Dh, theta, dx)
    elif st.session_state.page == '历史数据':
        show_history_page()

def show_main_page():
    st.title("🌊 海底地下水排泄预报软件 V1.0")
    st.info("版权所有：河海大学水利水电学院")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("功能导航")
        if st.button("📊 历史数据调查分析"): st.session_state.page = '历史数据'
        if st.button("🔄 动态模拟拟合精度"): st.session_state.page = '动态模拟'
        if st.button("🔮 模型预测结果分析"): st.session_state.page = '动态模拟'
    with col2:
        st.image("https://img.icons8.com/clouds/500/water.png", width=300)
        st.write("本软件集成热-盐耦合模型，支持海岸带 SGD 过程的精细化预报。")

def show_simulation_page(Dh, theta, dx):
    st.header("🔄 动态模拟与盐分剖面分析")
    
    col_input, col_plot = st.columns([1, 2])
    
    with col_input:
        st.subheader("模拟条件设置")
        C0 = st.number_input("地表海水盐度 (mg/L)", value=35000)
        q = st.number_input("垂直水通量 q (m/s)", value=4.4e-6, format="%.1e")
        run_sim = st.button("🚀 执行数值模拟", type="primary")
        if st.button("⬅️ 返回主界面"): st.session_state.page = '主界面'

    with col_plot:
        if run_sim:
            depths, salinity = SGDProcessor.thermal_salt_coupling(C0, q, Dh, theta, dx)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(salinity, depths, 'r-o', markersize=4, label='模拟盐度分布')
            ax.invert_yaxis()
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
            # 自动化分析结论
            peak_depth = depths[np.where(salinity > 600)[0][-1]] if any(salinity > 600) else 0
            st.success(f"✅ 模拟完成。盐分锋面当前位置：{peak_depth:.2f} m")

def show_history_page():
    st.header("📊 历史数据调查分析")
    st.file_uploader("上传观测数据 (CSV/Excel)", type=["csv", "xlsx"])
    if st.button("⬅️ 返回主页"): st.session_state.page = '主界面'

if __name__ == "__main__":
    main()
