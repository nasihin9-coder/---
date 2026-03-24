# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 核心物理引擎 (增强版) ---
class SoilPhysicsEngine:
    @staticmethod
    def calculate_r2(y_obs, y_sim):
        y_obs, y_sim = np.array(y_obs), np.array(y_sim)
        min_len = min(len(y_obs), len(y_sim))
        y_o, y_s = y_obs[:min_len], y_sim[:min_len]
        ss_res = np.sum((y_o - y_s) ** 2)
        ss_tot = np.sum((y_o - np.mean(y_o)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-12))
        return max(0.0, r2)

    @staticmethod
    def run_coupled_model(t_obs, c_start, q, dh_base, theta, dx=0.05, depth_max=1.0):
        z = np.arange(0, depth_max + dx, dx)
        c = np.full(len(z), 500.0) 
        c[0] = c_start 
        t_avg = np.mean(t_obs) if len(t_obs) > 0 else 25.0
        # 增强物理敏感度
        dh_eff = dh_base * (t_avg / 25.0) 
        v = q / (theta + 1e-12)
        
        # 增加迭代稳定性与深度
        dt = 0.4 * (dx**2) / (dh_eff + abs(v)*dx + 1e-12)
        steps = 1000 # 强制增加步数确保渗透
        
        for _ in range(steps):
            c_new = np.copy(c)
            for i in range(1, len(c)-1):
                diff = dh_eff * (c[i+1] - 2*c[i] + c[i-1]) / (dx**2)
                adv = -v * (c[i] - c[i-1]) / dx if v > 0 else -v * (c[i+1] - c[i]) / dx
                c_new[i] = c[i] + (diff + adv) * dt
            c = np.clip(c_new, 500, c_start)
            c[0] = c_start
        return z, c

# --- 2. 纯净绘图引擎 (解决方框乱码) ---
def plot_clean(z_sim, c_sim, t_obs, c_obs, r2):
    plt.rcParams['font.sans-serif'] = ['Arial', 'sans-serif']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    
    # 左图: Temperature
    z_obs_mapped = np.linspace(0, 1.0, len(t_obs))
    ax1.plot(t_obs, z_obs_mapped, 'r-o', markersize=4, label='Measured Temp')
    ax1.set_xlabel("Temperature (degC)")
    ax1.set_ylabel("Depth (m)")
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 右图: Salinity Fit
    ax2.scatter(c_obs, z_obs_mapped, color='gray', alpha=0.6, label='Sensor Data')
    ax2.plot(c_sim, z_sim, 'g-', linewidth=2, label=f'Model (R2={r2:.4f})')
    ax2.set_xlabel("Salinity (mg/L)")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    return fig

# --- 3. 界面逻辑 ---
def main():
    st.set_page_config(page_title="Soil Monitoring System", layout="wide")
    st.sidebar.title("Parameters")
    dh_input = st.sidebar.number_input("Dh", value=1e-4, format="%.1e")
    q_input = st.sidebar.number_input("q", value=1e-6, format="%.1e")
    
    st.title("🌡️ Soil Heat-Salt Coupling Monitor")
    up_file = st.file_uploader("Upload CSV", type="csv")
    
    if up_file:
        df = pd.read_csv(up_file)
        df.columns = [c.strip() for c in df.columns]
        t_col = [c for c in df.columns if 'temp' in c.lower()][0]
        s_col = [c for c in df.columns if 'sal' in c.lower()][0]
        
        st.success(f"Columns Matched: {t_col}, {s_col}")
        
        if st.button("🚀 Run Auto-Optimization (Get High R2)", type="primary"):
            best_r2, best_dh = -1.0, 1e-4
            t_obs, c_obs = df[t_col].values, df[s_col].values
            
            # 暴力寻优：扩大搜索范围
            for test_dh in np.logspace(-6, -1, 50): 
                _, c_sim = SoilPhysicsEngine.run_coupled_model(t_obs, c_obs[0], 1e-6, test_dh, 0.35)
                r2 = SoilPhysicsEngine.calculate_r2(c_obs, c_sim)
                if r2 > best_r2:
                    best_r2, best_dh = r2, test_dh
            
            z_sim, c_sim = SoilPhysicsEngine.run_coupled_model(t_obs, c_obs[0], 1e-6, best_dh, 0.35)
            fig = plot_clean(z_sim, c_sim, t_obs, c_obs, best_r2)
            st.pyplot(fig)
            st.metric("Final Accuracy R2", f"{best_r2:.4f}")
            st.info(f"Optimization Success! Best Dh: {best_dh:.2e}")

if __name__ == "__main__":
    main()
