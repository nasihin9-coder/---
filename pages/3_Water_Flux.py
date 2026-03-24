# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="水通量计算", layout="wide")
st.title("💧 土壤水分通量 (Water Flux) 数值模拟")

# 1. 核心物理参数输入 (侧边栏)
st.sidebar.header("🛠️ 达西参数设置")
k_sat = st.sidebar.slider("渗透系数 Ks (m/s)", 1e-6, 1e-3, 5e-5, format="%.1e")
gradient = st.sidebar.slider("水力梯度 (dh/dz)", 0.1, 2.0, 1.0)

# 2. 计算逻辑：达西定律 q = -Ks * i
q_calc = k_sat * gradient * 3600 * 24 # 换算成 m/day
st.session_state['q_sim'] = q_calc  # 存入 session 供参考

# 3. 模拟不同深度的水分通量分布
z = np.linspace(0, 1.0, 50)
# 模拟水分向下入渗时的衰减（由于土壤吸附）
flux_profile = q_calc * np.exp(-0.5 * z) 

# 4. 绘图模块 (专业科研风格)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(flux_profile, z, color='blue', linewidth=3, label='Estimated Water Flux')
ax.fill_betweenx(z, 0, flux_profile, color='blue', alpha=0.1) # 增加阴影美化

ax.set_xlabel("Water Flux (m/day)", fontsize=12)
ax.set_ylabel("Depth (m)", fontsize=12)
ax.set_title("Soil Water Flux Vertical Profile", fontsize=14)
ax.invert_yaxis()
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()

st.pyplot(fig)

# 5. 结果看板
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("地表入渗率 (q)", f"{q_calc:.4f} m/d")
with col2:
    st.metric("平均渗透系数", f"{k_sat:.1e}")
with col3:
    st.metric("水力稳定性", "Stable")

st.info("💡 物理说明：此界面根据达西定律计算水分通量，模拟了降雨或灌溉后水分向下的运移速率。")
