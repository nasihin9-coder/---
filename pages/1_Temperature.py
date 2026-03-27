import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from sklearn.metrics import r2_score
import time

st.title("🌡️ 温度剖面分析")

if st.session_state.get('df') is not None:
    df = st.session_state['df']
    z, t = df.iloc[:,0].values, df.iloc[:,1].values
    
    # 计算拟合准确度
    spl = make_interp_spline(z, t, k=3)
    t_pred = spl(z)
    r2 = r2_score(t, t_pred)

    # 结果看板
    c1, c2 = st.columns(2)
    c1.metric("最大计算深度", f"{z.max():.2f} m")
    c2.metric("拟合准确度 (R²)", f"{r2:.4f}")
    st.divider()

    if st.button("🚀 开始计算", type="primary"):
        fig, ax = plt.subplots()
        z_new = np.linspace(z.min(), z.max(), 100)
        t_new = spl(z_new)
        plot_area = st.empty()
        for i in range(5, 105, 5):
            ax.clear()
            ax.invert_yaxis()
            ax.scatter(t, z, color='gray', alpha=0.5)
            ax.plot(t_new[:i], z_new[:i], color='red', linewidth=2)
            plot_area.pyplot(fig)
            time.sleep(0.05)
else:
    st.warning("请先在主页上传数据")
