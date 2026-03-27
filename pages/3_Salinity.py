# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="盐度拟合分析", layout="wide")
st.title("🧂 盐度运移模型交互拟合")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z_obs = df[st.session_state['z_col']].values
    c_obs = df[st.session_state['s_col']].values
    dh = st.session_state.get('dh', 8.0e-5)
    
    st.sidebar.subheader("🛠️ 模型微调")
    c_base = st.sidebar.number_input("深层背景盐度 (mg/L)", 200, 2000, 500)
    line_style = st.sidebar.selectbox("曲线样式", ["实线", "虚线", "点划线"])
    styles = {"实线": "-", "虚线": "--", "点划线": "-."}
    
    z_sim = np.linspace(0, z_obs.max(), 100)
    k_factor = 3.5 * (dh / 8.0e-5)
    c_sim = c_base + (c_obs[0] - c_base) * np.exp(-k_factor * z_sim)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
    ax.plot(c_sim, z_sim, color='green', linestyle=styles[line_style], linewidth=3, label='Model')
    ax.set_xlabel("Salinity")
    ax.set_ylabel("Depth (m)")
    ax.invert_yaxis()
    ax.legend()
    st.pyplot(fig)
    st.download_button("📥 导出拟合数据", df.to_csv().encode('utf-8'), "fitted_data.csv", "text/csv")
    
    # 1. 计算过程面板
    with st.expander("🧮 展开查看底层物理与计算过程"):
        st.latex(r"C(z) = C_{base} + (C_0 - C_{base}) \cdot \exp\left(-\frac{v}{D_h} z\right)")
        st.write(f"当前输入参数：表层初始浓度 $C_0$={c_obs[0]:.1f}, 背景浓度 $C_{{base}}$={c_base}, 动力学系数 K={k_factor:.4f}")
        c_theory = c_base + (c_obs[0] - c_base) * np.exp(-k_factor * z_obs)
        residual_df = pd.DataFrame({"深度 z(m)": z_obs, "传感器实测值": c_obs, "模型理论值": np.round(c_theory, 1)})
        st.dataframe(residual_df.head(5), use_container_width=True)

    # 2. 新增：可视化渲染过程面板
    with st.expander("🎨 展开查看图表渲染与可视化绘制过程"):
        st.markdown("#### 1. UI 控件与图形属性的动态绑定")
        st.write("本页面的绘图过程实现了**状态驱动渲染（State-driven Rendering）**。当用户在左侧边栏调整参数时，视图引擎的响应流如下：")
        st.markdown("- **数据总线**：侧边栏获取的 `c_base`（背景盐度）实时注入数学模型，生成新的 X 轴数组 `c_sim`。")
        st.markdown("- **样式映射**：侧边栏的下拉框选择被映射为字典 `styles = {'实线': '-', '虚线': '--', ...}`，并动态作为 `linestyle` 参数传递给绘图函数。")
        st.markdown("- **透明度控制**：为避免实测散点遮挡拟合曲线，系统对散点图层设置了 `alpha=0.5` 的半透明通道，实现视觉上的主次分离。")
        
        st.markdown("#### 2. 样式响应式绘图指令")
        st.code('''# 获取用户选择的线条样式
user_style = styles[line_style] 

# 渲染图层：实测数据使用灰色半透明，拟合数据使用绿色自定义线型
ax.scatter(c_obs, z_obs, color='gray', alpha=0.5, label='Measured')
ax.plot(c_sim, z_sim, color='green', linestyle=user_style, linewidth=3)
''', language="python")

else:
    st.warning("请先在主页上传数据")
