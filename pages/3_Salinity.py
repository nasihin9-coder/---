# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score # 用于结果看板的精度计算
import time

# 1. 页面配置
st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合 (倒灌场景)")

# 2. 权限与数据检查 (防止未上传数据直接访问报错)
if 'df' not in st.session_state or st.session_state['df'] is None:
    st.warning("⚠️ 请先在主页 (app.py) 上传监测数据。")
    st.info("提示：系统需要利用深度 (z) 和盐度 (S) 列来模拟海水倒灌动力学过程。")
else:
    # 获取全局共享数据
    df = st.session_state['df']
    z_col = st.session_state.get('z_col', df.columns[0])
    s_col = st.session_state.get('s_col', df.columns[2] if len(df.columns)>2 else df.columns[-1])
    
    z_obs = df[z_col].values
    c_obs = df[s_col].values
    dh = st.session_state.get('dh', 8.0e-5) # 获取主页设置的弥散系数
    
    # 3. 侧边栏：模型微调
    st.sidebar.subheader("🛠️ 模型物理参数微调")
    c_base = st.sidebar.number_input("表层背景盐度 (mg/L)", 200, 5000, 1200, help="模拟降雨或淡水补给后的表层起始盐度")
    line_style = st.sidebar.selectbox("拟合曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    # 4. 建立倒灌解析模型
    # 模型假设：底部受海水高压驱动，盐分向上对流弥散
    z_max = z_obs.max()
    z_sim = np.linspace(0, z_max, 100)
    
    # 比例因子 k 结合了流速 v 和弥散系数 Dh
    k_factor = 3.5 * (dh / 8.0e-5)
    c_bottom = c_obs[-1] # 假定观测最深处为海水边界
    
    # 指数衰减模型（典型的倒灌稳态分布）
    c_sim = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_sim))
    
    # 5. 交互控制与图表占位
    calc_btn = st.button("🚀 开始模型拟合计算", type="primary")
    chart_spot = st.empty()

    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        # 自动计算坐标轴范围
        x_min, x_max = 0, max(c_obs) * 1.2
        y_min, y_max = z_max + 0.1, min(z_obs) - 0.1

        # 阶段 1：模拟实测传感器数据载入
        step_scatter = max(2, len(z_obs) // 6)
        for i in range(step_scatter, len(z_obs) + step_scatter, step_scatter):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Salinity (mg/L)", fontsize=10)
            ax.set_ylabel("Depth (m)", fontsize=10)
            ax.set_title("Loading Measured Salinity Profile...", fontsize=12)
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.scatter(c_obs[:i], z_obs[:i], color='gray', alpha=0.6, s=50, label='Measured (Intrusion)')
            chart_spot.pyplot(fig)
            time.sleep(0.02)

        # 阶段 2：驱动倒灌物理模型（从底部向上拟合）
        step_line = max(2, len(z_sim) // 20)
        for i in range(len(z_sim)-1, -1, -step_line):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.4, s=50, label='Measured Data')
            ax.plot(c_sim[i:], z_sim[i:], color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model Line')
            ax.legend(loc='upper right')
            chart_spot.pyplot(fig)
            time.sleep(0.01)
            
        st.session_state['sal_calc_done'] = True
        st.success("✨ 盐度倒灌模型拟合与残差演算完成！")
        plt.close(fig)
        
    elif st.session_state.get('sal_calc_done'):
        # 静态图表展示
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(c_obs, z_obs, color='gray', alpha=0.6, s=50, label='Measured Data')
        ax.plot(c_sim, z_sim, color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
        ax.set_xlabel("Salinity (mg/L)")
        ax.set_ylabel("Depth (m)")
        ax.set_title("Steady-state Salinity Intrusion Profile", fontsize=14)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)
        ax.legend()
        chart_spot.pyplot(fig)
        
    else:
        chart_spot.info("ℹ️ 请在左侧调整边界参数后，点击上方按钮驱动物理模型运行。")

    # 6. --- 页面底部结果看板 (加在 calc_btn 逻辑或 sal_calc_done 之后) ---
    if st.session_state.get('sal_calc_done'):
        st.divider()
        st.subheader("📊 盐度拟合性能看板")
        cols = st.columns(3)
        
        # 计算拟合指标
        c_theory_at_obs = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_obs))
        r2 = r2_score(c_obs, c_theory_at_obs)
        avg_error = np.mean(np.abs(c_obs - c_theory_at_obs))
        
        cols[0].metric("拟合优度 (R²)", f"{max(0, r2):.4f}")
        cols[1].metric("平均绝对残差", f"{avg_error:.1f} mg/L")
        cols[2].metric("倒灌影响深度", f"{z_max:.2f} m")

    # 7. 物理模型原理解析
    with st.expander("🧮 展开查看底层物理模型与残差计算"):
        st.markdown("#### 1. 稳态对流-弥散解析解")
        st.latex(r"C(z) = C_{surf} + (C_{bottom} - C_{surf}) \cdot \exp\left(-\frac{v}{D_h} (Z_{max} - z)\right)")
        
        # 详细残差数据表
        c_theory = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_obs))
        error = np.abs(c_obs - c_theory)
        residual_df = pd.DataFrame({
            "深度 z(m)": z_obs, 
            "实测倒灌盐度": c_obs, 
            "模型预测值": np.round(c_theory, 1), 
            "计算残差": np.round(error, 1)
        })
        st.dataframe(residual_df, use_container_width=True)
        st.caption("注：残差反映了模型对实际潮汐倒灌强度估算的偏差。")

else:
    st.warning("请先在主页上传数据")
