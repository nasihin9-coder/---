# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 核心计算引擎 ---
class CoupledPhysicsEngine:
    @staticmethod
    def calculate_r2(obs, sim):
        obs, sim = np.array(obs), np.array(sim)
        res = np.sum((obs - sim) ** 2)
        tot = np.sum((obs - np.mean(obs)) ** 2)
        return max(0, 1 - (res / (tot + 1e-12)))

    @staticmethod
    def thermal_salt_model(T_obs, C0, q, Dh_base, theta, dx, depth_max=1.0):
        z = np.arange(0, depth_max + dx, dx)
        C = np.full(len(z), 500.0) 
        C[0] = C0
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

# --- 2. 超级鲁棒：列名自动修复与绘图函数 ---
def robust_plot(z, c_sim, t_obs, c_obs, r2):
    """解决乱码及坐标轴显示问题的鲁棒函数"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 左图：温度 (使用中英对照标签，防止方框)
    ax1.plot(t_obs, z[:len(t_obs)], 'r-s', markersize=4, label='Measured Temp')
    ax1.set_xlabel("Temperature / 温度 (°C)")
    ax1.set_ylabel("Depth / 深度 (m)")
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 右图：盐度回归
    ax2.scatter(c_obs, z[:len(c_obs)], color='black', alpha=0.6, label='Sensor Obs')
    ax2.plot(c_sim, z, 'g-', linewidth=2, label=f'Model Regression (R²={r2:.4f})')
    ax2.set_xlabel("Salinity / 含盐量 (mg/L)")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    fig.tight_layout()
    return fig

# --- 3. 界面逻辑 ---
def main():
    st.set_page_config(page_title="热-盐耦合监测系统", layout="wide")
    
    # 侧边栏
    st.sidebar.title("🛠️ 模型参数微调")
    Dh_base = st.sidebar.number_input("弥散系数 Dh", value=1e-7, format="%.1e")
    theta = st.sidebar.slider("孔隙度", 0.1, 0.6, 0.35)
    
    st.title("🌡️ 土壤热-盐耦合监测分析中心")
    st.info("说明：支持模糊列名识别。请上传包含‘温度’和‘盐度’字样的 CSV 文件。")

    up_file = st.file_uploader("上传传感器 CSV 数据", type="csv")
    
    if up_file:
        df = pd.read_csv(up_file)
        # --- 鲁棒性处理核心：自动识别列名 ---
        cols = list(df.columns)
        # 清洗：去除首尾空格
        df.columns = [c.strip() for c in df.columns]
        
        # 关键词模糊匹配
        t_col = [c for c in df.columns if any(k in c.lower() for k in ['temp', '温度', 't'])]
        s_col = [c for c in df.columns if any(k in c.lower() for k in ['sal', '盐', 's', 'salt'])]
        d_col = [c for c in df.columns if any(k in c.lower() for k in ['depth', '深', 'z'])]

        if t_col and s_col:
            st.success(f"✅ 自动匹配成功：温度 -> [{t_col[0]}], 盐度 -> [{s_col[0]}]")
            st.dataframe(df.head(3))
            
            if st.button("开始热-盐耦合分析", type="primary"):
                t_obs = df[t_col[0]].values
                c_obs = df[s_col[0]].values
                
                # 执行模拟
                z_sim, c_sim = CoupledPhysicsEngine.thermal_salt_model(t_obs, c_obs[0], 4.4e-6, Dh_base, theta, 0.05)
                r2 = CoupledPhysicsEngine.calculate_r2(c_obs, c_sim[:len(c_obs)])
                
                # 绘图
                fig = robust_plot(z_sim, c_sim, t_obs, c_obs, r2)
                st.pyplot(fig)
                st.metric("回归精度 R²", f"{r2:.4f}")
        else:
            st.error(f"❌ 无法识别列名。当前列名：{cols}。请确保包含 'Temperature' 和 'Salinity'。")

if __name__ == "__main__":
    main()
