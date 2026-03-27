# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合 (倒灌场景)")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_obs = df[st.session_state['z_col']].values
    c_obs = df[st.session_state['s_col']].values
    dh = st.session_state.get('dh', 8.0e-5)
    
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("表层背景盐度 (mg/L)", 200, 2000, 1200)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    z_max = z_obs.max()
    z_sim = np.linspace(0, z_max, 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_bottom = c_obs[-1]
    c_sim = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_sim))
    
    calc_btn = st.button("🚀 开始计算", type="primary")
    chart_spot = st.empty()

    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = 0, max(c_obs)*1.1
        y_min, y_max = z_max+0.1, min(z_obs)-0.1

        # 优化动画：合并帧数，实现快速连贯的自下而上动画
        step_line = max(2, len(z_sim) // 20)
        for i in range(len(z_sim)-1, -1, -step_line):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured (Intrusion)')
            # 利用切片从当前索引画到底部
            ax.plot(c_sim[i:], z_sim[i:], color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
            
            chart_spot.pyplot(fig)
            time.sleep(0.01)
            
        st.session_state['sal_calc_done'] = True
        st.success("✨ 倒灌拟合与误差演算完成！")
        plt.close(fig)
        
    elif st.session_state.get('sal_calc_done'):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured (Intrusion)')
        ax.plot(c_sim, z_sim, color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
        ax.set_xlabel("Salinity (mg/L)")
        ax.set_ylabel("Depth (m)")
        ax.invert_yaxis()
        ax.legend()
        chart_spot.pyplot(fig)
        
    else:
        chart_spot.info("ℹ️ 请调整左侧边界参数后，点击上方【🚀 开始计算】按钮驱动物理模型运行。")

    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.latex(r"C(z) = C_{surf} + (C_{bottom} - C_{surf}) \cdot \exp\left(-\frac{v}{D_h} (Z_{max} - z)\right)")
        c_theory = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_obs))
        error = np.abs(c_obs - c_theory)
        residual_df = pd.DataFrame({"深度 z(m)": z_obs, "实测倒灌盐度": c_obs, "模型理论值": np.round(c_theory, 1), "绝对残差": np.round(error, 1)})
        st.dataframe(residual_df.head(5), use_container_width=True)

else:
    st.warning("请先在主页上传数据")
