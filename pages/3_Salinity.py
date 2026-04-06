# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from sklearn.metrics import r2_score

# 页面配置
st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合 (倒灌场景)")

# 1. 检查数据是否存在 (防御性编程，防止 KeyError)
if 'df' not in st.session_state or st.session_state['df'] is None:
    st.warning("⚠️ 请先在主页 (app.py) 上传监测数据 CSV 文件。")
    st.info("系统需要获取剖面深度与实测盐度数据以进行物理模型驱动。")
else:
    # 2. 获取数据与配置列名
    df = st.session_state['df']
    # 优先从 session_state 获取列名，若无则使用默认列
    z_col = st.session_state.get('z_col', df.columns[0])
    s_col = st.session_state.get('s_col', df.columns[2] if len(df.columns) > 2 else df.columns[-1])
    
    z_obs = df[z_col].values
    c_obs = df[s_col].values
    dh = st.session_state.get('dh', 8.0e-5) # 弥散系数
    
    # 3. 侧边栏：模型参数调节
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("表层背景盐度 (mg/L)", 200, 5000, 1200)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    # 4. 构建倒灌物理模型
    z_max = z_obs.max()
    z_sim = np.linspace(0, z_max, 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_bottom = c_obs[-1] # 假定最深处为海水边界
    
    # 解析解公式
    c_sim = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_sim))
    
    # 5. 计算控制
    calc_btn = st.button("🚀 开始模型拟合计算", type="primary")
    chart_spot = st.empty()

    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = 0, max(c_obs) * 1.2
        y_min, y_max = z_max + 0.1, min(z_obs) - 0.1
        
        # 模拟计算动态过程
        step_line = max(2, len(z_sim) // 20)
        for i in range(len(z_sim)-1, -1, -step_line):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured Data')
            ax.plot(c_sim[i:], z_sim[i:], color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
            ax.legend(loc="upper right")
            chart_spot.pyplot(fig)
            time.sleep(0.01)
            
        st.session_state['sal_calc_done'] = True
        st.success("✨ 模型拟合与残差演算完成！")
        plt.close(fig)
        
    elif st.session_state.get('sal_calc_done'):
        # 渲染最终静态图
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured Data')
        ax.plot(c_sim, z_sim, color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
        ax.set_xlabel("Salinity (mg/L)")
        ax.set_ylabel("Depth (m)")
        ax.invert_yaxis()
        ax.legend()
        chart_spot.pyplot(fig)
    else:
        chart_spot.info("ℹ️ 请调整参数后点击【开始计算】按钮驱动模型。")

    # 6. 物理原理展示与数据表
    st.divider()
    with st.expander("🧮 查看底层物理方程与拟合残差"):
        st.latex(r"C(z) = C_{surf} + (C_{bottom} - C_{surf}) \cdot \exp\left(-\frac{v}{D_h} (Z_{max} - z)\right)")
        
        # 计算具体残差
        c_theory = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_obs))
        r2 = r2_score(c_obs, c_theory)
        st.metric("模型拟合度 (R²)", f"{max(0, r2):.4f}")
        
        residual_df = pd.DataFrame({
            "深度 z(m)": z_obs, 
            "实测值": c_obs, 
            "预测值": np.round(c_theory, 1), 
            "误差": np.round(c_obs - c_theory, 1)
        })
        st.dataframe(residual_df, use_container_width=True)
