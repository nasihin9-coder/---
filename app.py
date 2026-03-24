import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PhysicsOptimizer:
    @staticmethod
    def run_model(t_obs, c_start, dh, q, steps=800):
        z = np.linspace(0, 1.0, 21)
        c = np.full(len(z), 500.0) # 背景值
        c[0] = c_start
        dt = 0.4 * (0.05**2) / (dh + abs(q)/0.35 + 1e-10)
        
        for _ in range(steps):
            c_new = np.copy(c)
            for i in range(1, len(z)-1):
                # 对流弥散方程实现
                diff = dh * (c[i+1] - 2*c[i] + c[i-1]) / (0.05**2)
                adv = -(q/0.35) * (c[i] - c[i-1]) / 0.05
                c_new[i] = c[i] + (diff + adv) * dt
            c = np.clip(c_new, 500, c_start)
        return z, c

def main():
    st.title("Soil Salt Transport Analysis (High R2 Version)")
    up_file = st.file_uploader("Upload CSV", type="csv")
    
    if up_file:
        df = pd.read_csv(up_file)
        t_obs = df.iloc[:, 0].values
        c_obs = df.iloc[:, 1].values
        
        if st.button("🚀 强制参数反演 (Optimize for High R2)"):
            best_r2, best_dh, best_q = -1.0, 1e-5, 1e-6
            
            # 自动在物理区间寻找最贴合散点的参数
            with st.spinner("Searching for best fit..."):
                for test_dh in np.logspace(-6, -2, 20):
                    for test_q in [1e-7, 5e-7, 1e-6, 5e-6]:
                        z_sim, c_sim = PhysicsOptimizer.run_model(t_obs, c_obs[0], test_dh, test_q)
                        # 插值对齐计算 R2
                        c_interp = np.interp(np.linspace(0, 1, len(c_obs)), np.linspace(0, 1, len(z_sim)), c_sim)
                        r2 = 1 - np.sum((c_obs - c_interp)**2) / (np.sum((c_obs - np.mean(c_obs))**2) + 1e-9)
                        if r2 > best_r2:
                            best_r2, best_dh, best_q = r2, test_dh, test_q
            
            # 绘图显示
            z_final, c_final = PhysicsOptimizer.run_model(t_obs, c_obs[0], best_dh, best_q)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(c_obs, np.linspace(0, 1, len(c_obs)), color='gray', label='Observed')
            ax.plot(c_final, z_final, 'g-', linewidth=2, label=f'Model (R2={best_r2:.4f})')
            ax.invert_yaxis()
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            ax.legend()
            st.pyplot(fig)
            st.success(f"Optimized R2: {best_r2:.4f} | Dh: {best_dh:.2e}")

if __name__ == "__main__":
    main()
