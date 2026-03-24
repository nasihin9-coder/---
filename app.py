# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 核心计算引擎 (热-盐耦合逻辑) ---
class SoilPhysicsEngine:
    @staticmethod
    def calculate_r2(y_obs, y_sim):
        """计算回归精度 R2"""
        y_obs, y_sim = np.array(y_obs), np.array(y_sim)
        # 核心修复：确保数据长度完全一致
        min_len = min(len(y_obs), len(y_sim))
        y_o, y_s = y_obs[:min_len], y_sim[:min_len]
        
        ss_res = np.sum((y_o - y_s) ** 2)
        ss_tot = np.sum((y_o - np.mean(y_o)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-12))
        return max(0, r2)

    @staticmethod
    def run_coupled_model(t_obs, c_start, q, dh_base, theta, dx=0.05, depth_max=1.0):
        """变饱和带热-盐耦合数值模拟"""
        z = np.arange(0, depth_max + dx, dx)
        c = np.full(len(z), 500.0) # 背景盐度
        c[0] = c_start # 自动对齐实测起点
        
        # 温度修正：温度越高，弥散系数越大
        t_avg = np.mean(t_obs) if len(t_obs) > 0 else 25.0
        dh_eff = dh_base * (t_avg / 25.0)
        
        v = q / (theta + 1e-12)
        # CFL稳定性条件：防止坐标轴锯齿
        dt = 0.45 * (dx**2) / (dh_eff + abs(v)*dx + 1e-12)
        steps = min(int(86400 / dt), 500)
        
        for _ in range(steps):
            c_new = np.copy(c)
            for i in range(1, len(c)-1):
                diffusion = dh_eff * (c[i+1] - 2*c[i] + c[i-1]) / (dx**2)
                advection = -v * (c[i] - c[i-1]) / dx if v > 0 else -v * (c[i+1] - c[i]) / dx
                c_new[i] = c[i] + (diffusion + advection) * dt
            c = np.clip(c_new, 0, 100000)
            c[0] = c_start
        return z, c

# --- 2. 鲁棒绘图函数 (解决乱码与显示问题) ---
def plot_coupled_analysis(z_sim, c_sim, t_obs, c_obs, r2):
    """双图展示：左侧温度剖面，右侧盐度回归"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 左图：温度 (Temperature Profile)
    ax1.plot(t_obs, np.linspace(0, 1.0, len(t_obs)), 'r-s', markersize=4, label='Measured Temp')
    ax1.set_xlabel("Temperature / 温度 (°C)")
    ax1.set_ylabel("Depth / 深度 (m)")
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 右图：盐度回归 (Salinity Regression)
    ax2.scatter(c_obs, np.linspace(0, 1.0, len(c_obs)), color='black', alpha=0.6, label='Sensor Data')
    ax2.plot(c_sim, z_sim, 'g-', linewidth=2, label=f'Model Fit (R²={r2:.4f})')
    ax2.set_xlabel("Salinity / 含盐量 (mg/L)")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    return fig

# --- 3. Streamlit 界面主体 ---
def main():
    st.set_page_config(page_title="土壤热-盐耦合监测系统 V1.0", layout="wide")
    
    # 侧边栏：核心参数
    st.sidebar.title("🔬 核心物理参数")
    dh_input = st.sidebar.number_input("基准弥散系数 Dh", value=5e-6, format="%.1e") # 默认值调大以增加渗透
    q_input = st.sidebar.number_input("垂直通量 q (m/s)", value=4.4e-6, format="%.1e")
    theta = st.sidebar.slider("土壤有效孔隙度", 0.1, 0.6, 0.35)
    
    st.title("🌡️ 变饱和带土壤热-盐耦合在线监测系统")
    st.info("提示：请上传包含 'Temperature' 和 'Salinity' 列的 CSV 文件。系统将自动执行 R² 回归分析。")

    # 数据上传
    uploaded_file = st.file_uploader("第一步：上传传感器数据 (CSV)", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # 自动清洗列名空格
        df.columns = [c.strip() for c in df.columns]
        
        # 模糊匹配列名
        t_col = [c for c in df.columns if any(k in c.lower() for k in ['temp', '温度'])]
        s_col = [c for c in df.columns if any(k in c.lower() for k in ['sal', '盐'])]
        
        if t_col and s_col:
            st.success(f"✅ 已成功识别：温度列 -> {t_col[0]}, 盐度列 -> {s_col[0]}")
            st.dataframe(df.head(3))
            
            if st.button("开始热-盐耦合解算", type="primary"):
                t_obs = df[t_col[0]].values
                c_obs = df[s_col[0]].values
                
                # 执行模拟：自动取实测第一个点作为起点
                z_sim, c_sim = SoilPhysicsEngine.run_coupled_model(
                    t_obs, c_obs[0], q_input, dh_input, theta
                )
                
                # 计算回归精度 R2
                r2_val = SoilPhysicsEngine.calculate_r2(c_obs, c_sim)
                
                # 绘图展示
                fig = plot_coupled_analysis(z_sim, c_sim, t_obs, c_obs, r2_val)
                st.pyplot(fig)
                
                # 结果指标
                st.metric("回归拟合精度 (R²)", f"{r2_val:.4f}")
                if r2_val < 0.1:
                    st.warning("注：R² 较低，请尝试在侧边栏调大‘弥散系数 Dh’或‘通量 q’。")
        else:
            st.error(f"❌ 错误：无法识别列名。当前列名为：{list(df.columns)}")

if __name__ == "__main__":
    main()
