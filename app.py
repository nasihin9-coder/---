import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 核心算法：热-盐耦合数值模拟
def salt_transport_stable(C0, q, Dh, theta, dx, depth_array):
    C = np.full(len(depth_array), 500.0)
    C[0] = C0
    v = q / theta
    dt = 0.5 * (dx**2) / (Dh + abs(v)*dx + 1e-12)
    steps = min(int(86400 / dt), 300) 
    for _ in range(steps):
        C_new = np.copy(C)
        for i in range(1, len(C)-1):
            diff = Dh * (C[i+1] - 2*C[i] + C[i-1]) / (dx**2)
            adv = -v * (C[i] - C[i-1]) / dx if v > 0 else -v * (C[i+1] - C[i]) / dx
            C_new[i] = C[i] + (diff + adv) * dt
        C = np.clip(C_new, 0, 100000)
        C[0] = C0
    return C

st.set_page_config(page_title="热-盐耦合系统", layout="wide")
st.title("🌡️ 变饱和带热-盐耦合在线系统")

# 侧边栏参数调节
st.sidebar.header("🔬 核心物理参数")
D_h = st.sidebar.number_input("弥散系数 Dh", value=1e-7, format="%.1e")
theta = st.sidebar.slider("有效孔隙度", 0.2, 0.5, 0.35)
dx = st.sidebar.slider("步长 Δx (m)", 0.01, 0.1, 0.05)
sea_salinity = st.sidebar.slider("地表盐度 (mg/L)", 0, 40000, 35000)

uploaded_file = st.file_uploader("第一步：上传温度数据", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    try:
        st.write("数据预览:", df.head())
        depths = np.arange(0, 1.0 + dx, dx)
        # 实时模拟结果
        C_final = salt_transport_stable(sea_salinity, 4.4e-6, D_h, theta, dx, depths)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(C_final, depths, 'r-o')
        ax.invert_yaxis()
        ax.set_xlabel("Salinity (mg/L)")
        ax.set_ylabel("Depth (m)")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"分析失败: {e}")
