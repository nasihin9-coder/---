import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import time

st.title("🧂 盐度运移拟合")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z, s = df.iloc[:,0].values, df.iloc[:,2].values
    c_base = st.sidebar.number_input("背景盐度", 200, 2000, 1000)
    
    # 物理模型计算与 R2
    k = 3.5 * (st.session_state['dh'] / 8.0e-5)
    s_pred = c_base + (s[-1] - c_base) * np.exp(-k * (z.max() - z))
    r2 = r2_score(s, s_pred)

    # 结果看板
    c1, c2 = st.columns(2)
    c1.metric("模拟有效深度", f"{z.max():.2f} m")
    c2.metric("模型匹配度 (R²)", f"{max(0, r2):.4f}")
    st.divider()

    if st.button("🚀 开始计算"):
        fig, ax = plt.subplots()
        z_sim = np.linspace(0, z.max(), 100)
        s_sim = c_base + (s[-1] - c_base) * np.exp(-k * (z.max() - z_sim))
        plot_area = st.empty()
        for i in range(len(z_sim)-1, -1, -5):
            ax.clear()
            ax.invert_yaxis()
            ax.scatter(s, z, color='gray', alpha=0.5)
            ax.plot(s_sim[i:], z_sim[i:], color='orange', linewidth=3)
            plot_area.pyplot(fig)
            time.sleep(0.05)
else:
    st.warning("请先在主页上传数据")
