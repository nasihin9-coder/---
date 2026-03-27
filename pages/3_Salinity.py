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
    
    # --- 核心修改：自下而上的倒灌物理模型 ---
    z_max = z_obs.max()
    z_sim = np.linspace(0, z_max, 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    
    # 理论解析解：底层浓度最高 c_obs[-1]，向上呈指数衰减
    c_bottom = c_obs[-1]
    c_sim = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_sim))
    
    chart_spot = st.empty()

    if st.button("▶️ 播放海水倒灌动态拟合过程"):
        fig, ax = plt.subplots(figsize=(10, 6))
        x_min, x_max = 0, max(c_obs)*1.1
        y_min, y_max = z_max+0.1, min(z_obs)-0.1

        # 动画：模拟高盐地下水从底层向上入侵的过程
        # 逆序遍历模拟深度，实现从深到浅的绘制
        for i in range(len(z_sim)-1, -1, -2):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Salinity (mg/L)")
            ax.set_ylabel("Depth (m)")
            
            # 散点背景
            ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured (Intrusion)')
            
            # 拟合曲线从底端向上方生长
            ax.plot(c_sim[i:], z_sim[i:], color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
            
            chart_spot.pyplot(fig)
            time.sleep(0.015)
            
        st.success("✨ 倒灌拟合绘图完成！")
        
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured (Intrusion)')
        ax.plot(c_sim, z_sim, color='darkorange', linestyle=styles[line_style], linewidth=3, label='Intrusion Model')
        ax.set_xlabel("Salinity (mg/L)")
        ax.set_ylabel("Depth (m)")
        ax.invert_yaxis()
        ax.legend()
        chart_spot.pyplot(fig)
        
    # 计算过程面板同步更新公式
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.markdown("#### 1. 地下水海水倒灌模型 (Bottom-up CDE)")
        st.write("基于图1物理模型推导的地下高盐水入侵解析解：")
        st.latex(r"C(z) = C_{surf} + (C_{bottom} - C_{surf}) \cdot \exp\left(-\frac{v}{D_h} (Z_{max} - z)\right)")
        st.write(f"当前输入：底层入侵浓度 $C_{{bottom}}$={c_bottom:.1f}, 表层背景 $C_{{surf}}$={c_base}, 深度边界 $Z_{{max}}$={z_max}m")
        
        c_theory = c_base + (c_bottom - c_base) * np.exp(-k_factor * (z_max - z_obs))
        error = np.abs(c_obs - c_theory)
        residual_df = pd.DataFrame({"深度 z(m)": z_obs, "实测倒灌盐度": c_obs, "模型理论值": np.round(c_theory, 1), "绝对残差": np.round(error, 1)})
        st.dataframe(residual_df.head(5), use_container_width=True)

    with st.expander("🎨 展开查看图表渲染与可视化绘制过程"):
         st.write("动画引擎采用逆向数组切片 `c_sim[i:]` 与循环，再现了高浓度盐分从底层边界向上蔓延的动力学过程。线条颜色已同步更新为警示色 `darkorange`，以体现“入侵”危害。")

else:
    st.warning("请先在主页上传数据")
