# -*- coding: utf-8 -*-
"""
软件名称：变饱和带土壤热-盐耦合监测与归趋预报软件 V1.0
功能描述：通过温度场与浓度场耦合计算，实现土壤含盐量的精准反演与 R2 精度评价
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 核心计算引擎 (热-盐耦合逻辑) ---
class CoupledPhysicsEngine:
    @staticmethod
    def calculate_r2(obs, sim):
        obs, sim = np.array(obs), np.array(sim)
        res = np.sum((obs - sim) ** 2)
        tot = np.sum((obs - np.mean(obs)) ** 2)
        return max(0, 1 - (res / (tot + 1e-12)))

    @staticmethod
    def thermal_salt_model(T_obs, C0, q, Dh_base, theta, dx, depth_max=1.0):
        """
        根据温度监测值修正盐分迁移过程
        T_obs: 传感器监测到的温度数组
        """
        z = np.arange(0, depth_max + dx, dx)
        C = np.full(len(z), 500.0) 
        C[0] = C0
        
        # 温度对弥散系数的修正 (温度越高，分子扩散越活跃)
        # 简化公式：Dh = Dh_base * (T/25)
        T_avg = np.mean(T_obs) if len(T_obs) > 0 else 25.0
        Dh_corrected = Dh_base * (T_avg / 25.0)
        
        v = q / (theta + 1e-12)
        dt = 0.5 * (dx**2) / (Dh_corrected + abs(v)*dx + 1e-12)
        steps = min(int(86400 / dt), 500)
        
        for _ in range(steps):
            C_new = np.copy(C)
            for i in range(1, len(C)-1):
                diff = Dh_corrected * (C[i+1] - 2*C[i] + C[i-1]) / (dx**2)
                adv = -v * (C[i] - C[i-1]) / dx if v > 0 else -v * (C[i+1] - C[i]) / dx
                C_new[i] = C[i] + (diff + adv) * dt
            C = np.clip(C_new, 0, 100000)
            C[0] = C0
        return z, C

# --- 2. 界面绘图 (修复乱码) ---
def plot_coupled_results(z, c, t_data, r2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 左图：温度剖面 (传感器监测)
    ax1.plot(t_data, z[:len(t_data)], 'r-s', label='Temp Observed')
    ax1.set_xlabel("Temperature / 温度 (°C)")
    ax1.set_ylabel("Depth / 深度 (m)")
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 右图：盐度回归分析
    ax2.plot(c, z, 'g-', linewidth=2, label=f'Model (R²={r2:.4f})')
    ax2.set_xlabel("Salinity / 含盐量 (mg/L)")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    fig.tight_layout()
    return fig

# --- 3. 软件主体 ---
def main():
    st.set_page_config(page_title="热-盐耦合土壤监测系统", layout="wide")
    
    if 'page' not in st.session_state:
        st.session_state.page = '首页'

    # 侧边栏参数
    st.sidebar.title("🛠️ 耦合参数配置")
    Dh_base = st.sidebar.number_input("基准弥散系数 (25°C)", value=1e-7, format="%.1e")
    theta = st.sidebar.slider("土壤孔隙度", 0.1, 0.6, 0.35)
    
    if st.session_state.page == '首页':
        st.title("🌡️ 变饱和带土壤热-盐耦合监测软件")
        st.caption("版本：V1.0 | 核心算法：温度修正盐分迁移模型")
        if st.button("进入传感器数据分析中心", use_container_width=True):
            st.session_state.page = '分析页'
        
        # 封面原理图
        st.write("---")
        st.write("**热-盐耦合计算逻辑说明**")
        st.latex(r"D_h(T) = D_{base} \cdot \frac{T_{obs}}{25}")
        st.latex(r"\frac{\partial C}{\partial t} = D_h(T) \frac{\partial^2 C}{\partial z^2} - v \frac{\partial C}{\partial z}")

    elif st.session_state.page == '分析页':
        st.header("📈 传感器数据驱动分析")
        up_file = st.file_uploader("上传传感器 CSV 数据 (需包含 Temperature 和 Salinity 列)", type="csv")
        
        if up_file:
            df = pd.read_csv(up_file)
            st.dataframe(df.head(5))
            
            if st.button("开始热-盐耦合解算", type="primary"):
                # 获取温度和实测盐度
                t_obs = df['Temperature'].values if 'Temperature' in df.columns else np.full(len(df), 25.0)
                c_obs = df['Salinity'].values if 'Salinity' in df.columns else df.iloc[:, 1].values
                
                # 执行模拟
                z_sim, c_sim = CoupledPhysicsEngine.thermal_salt_model(t_obs, c_obs[0], 4.4e-6, Dh_base, theta, 0.05)
                
                # 计算 R2
                r2 = CoupledPhysicsEngine.calculate_r2(c_obs, c_sim[:len(c_obs)])
                
                # 绘图
                fig = plot_coupled_results(z_sim, c_sim, t_obs, r2)
                st.pyplot(fig)
                st.metric("耦合回归精度 R²", f"{r2:.4f}")

        if st.button("⬅️ 返回主页"): st.session_state.page = '首页'

if __name__ == "__main__":
    main()
