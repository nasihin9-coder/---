# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 物理计算引擎 ---
class SoilPhysicsEngine:
    @staticmethod
    def calculate_r2(y_obs, y_sim):
        """计算决定系数 R2"""
        y_obs, y_sim = np.array(y_obs), np.array(y_sim)
        min_len = min(len(y_obs), len(y_sim))
        y_o, y_s = y_obs[:min_len], y_sim[:min_len]
        ss_res = np.sum((y_o - y_s) ** 2)
        ss_tot = np.sum((y_o - np.mean(y_o)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-12))
        return max(0.0, r2)

    @staticmethod
    def run_coupled_model(t_obs, c_start, q, dh_base, theta, dx=0.05, depth_max=1.0):
        """热-盐耦合数值模拟"""
        z = np.arange(0, depth_max + dx, dx)
        c = np.full(len(z), 500.0) 
        c[0] = c_start 
        t_avg = np.mean(t_obs) if len(t_obs) > 0 else 25.0
        dh_eff = dh_base * (t_avg / 25.0) 
        v = q / (theta + 1e-12)
        dt = 0.45 * (dx**2) / (dh_eff + abs(v)*dx + 1e-12)
        steps = min(int(86400 / dt), 600)
        for _ in range(steps):
            c_new = np.copy(c)
            for i in range(1, len(c)-1):
                diff = dh_eff * (c[i+1] - 2*c[i] + c[i-1]) / (dx**2)
                adv = -v * (c[i] - c[i-1]) / dx if v > 0 else -v * (c[i+1] - c[i]) / dx
                c_new[i] = c[i] + (diff + adv) * dt
            c = np.clip(c_new, 0, 100000)
            c[0] = c_start
        return z, c

# --- 2. 鲁棒绘图引擎 (中英双语防乱码) ---
def plot_analysis(z_sim, c_sim, t_obs, c_obs, r2):
    """解决坐标轴乱码与显示问题"""
    # 强制设置基础字体，防止系统崩溃
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    
    # 左图：温度剖面
    z_obs_mapped = np.linspace(0, 1.0, len(t_obs))
    ax1.plot(t_obs, z_obs_mapped, 'r-s', markersize=4, label='Temp Measured')
    ax1.set_xlabel("Temperature / 温度 (°C)")
    ax1.set_ylabel("Depth / 深度 (m)")
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 右图：盐度回归
    ax2.scatter(c_obs, z_obs_mapped, color='black', alpha=0.6, label='Sensor Obs')
    ax2.plot(c_sim, z_sim, 'g-', linewidth=2, label=f'Model Fit (R²={r2:.4f})')
    ax2.set_xlabel("Salinity / 含盐量 (mg/L)")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    return fig

# --- 3. UI 界面 ---
def main():
    st.set_page_config(page_title="土壤热-盐耦合监测系统 V1.0", layout="wide")
    
    st.sidebar.title("⚙️ 物理参数配置")
    dh_input = st.sidebar.number_input("弥散系数 (Dh)", value=5e-5, format="%.1e")
    q_input = st.sidebar.number_input("垂直通量 (q)", value=4.4e-6, format="%.1e")
    theta = st.sidebar.slider("土壤孔隙度", 0.1, 0.6, 0.35)
    
    st.title("🌡️ 变饱和带土壤热-盐耦合监测系统")
    st.markdown("---")

    uploaded_file = st.file_uploader("第一步：上传传感器 CSV 数据", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip() for c in df.columns] # 清洗列名
        
        t_col = [c for c in df.columns if any(k in c.lower() for k in ['temp', '温度'])]
        s_col = [c for c in df.columns if any(k in c.lower() for k in ['sal', '盐'])]
        
        if t_col and s_col:
            st.success(f"已识别：温度 -> {t_col[0]}, 盐度 -> {s_col[0]}")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("运行基础模拟", type="primary", use_container_width=True):
                    run_simulation(df, t_col[0], s_col[0], dh_input, q_input, theta)
            with col_btn2:
                if st.button("🚀 自动优化参数 (获取高 R²)", use_container_width=True):
                    optimize_parameters(df, t_col[0], s_col[0], q_input, theta)
        else:
            st.error("错误：CSV 必须包含‘温度’和‘盐度’相关列。")

def run_simulation(df, t_name, s_name, dh, q, theta):
    t_obs = df[t_name].values
    c_obs = df[s_name].values
    z_sim, c_sim = SoilPhysicsEngine.run_coupled_model(t_obs, c_obs[0], q, dh, theta)
    r2_val = SoilPhysicsEngine.calculate_r2(c_obs, c_sim)
    
    fig = plot_analysis(z_sim, c_sim, t_obs, c_obs, r2_val)
    st.pyplot(fig)
    st.metric("回归拟合精度 (R²)", f"{r2_val:.4f}")

def optimize_parameters(df, t_name, s_name, q, theta):
    t_obs = df[t_name].values
    c_obs = df[s_name].values
    best_r2 = -1.0
    best_dh = 1e-5
    
    # 在常用物理区间搜索最优 Dh
    with st.spinner("正在搜索最优拟合参数..."):
        for test_dh in np.logspace(-7, -3, 40):
            _, c_sim = SoilPhysicsEngine.run_coupled_model(t_obs, c_obs[0], q, test_dh, theta)
            r2 = SoilPhysicsEngine.calculate_r2(c_obs, c_sim)
            if r2 > best_r2:
                best_r2 = r2
                best_dh = test_dh
    
    st.info(f"自动寻优成功！推荐 Dh: {best_dh:.2e}")
    run_simulation(df, t_name, s_name, best_dh, q, theta)

if __name__ == "__main__":
    main()
