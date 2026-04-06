# -*- coding: utf-8 -*-
import streamlit as st
import os

# 页面基本配置
st.set_page_config(page_title="实验装置说明", layout="wide")

st.title("🔬 室内一维水热盐运移实验平台")

# 页面导言
st.markdown("""
本反演系统的核心算法（如偏微分方程解算、参数拟合）均基于以下自主研发的实验装置进行校准与验证。
该装置能够精密模拟滨海盐沼环境下的水分入渗、热量传导及盐分累积过程。
""")

st.divider()

# 主展示区：左侧展示图片，右侧详细解析
col_img, col_info = st.columns([3, 2])

with col_img:
    img_path = "apparatus_diagram.jpg"
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True, caption="室内一维土柱实验装置示意图")
    else:
        st.error(f"❌ 未检测到装置图文件：{img_path}")
        st.info("提示：请确保已将图片重命名为 apparatus_diagram.jpg 并上传至仓库根目录。")

with col_info:
    st.subheader("🛠️ 硬件系统构成")
    
    with st.expander("1. 温控动力中心", expanded=True):
        st.write("""
        - **THZ-82A 恒温水浴振荡器**：提供稳定的补给水温度环境，模拟不同季节的地下水边界。
        - **循环水泵 (WATER PUMP)**：负责将恒温介质或盐溶液精准注入土柱。
        - **补给水槽**：大容量存储，确保长时段实验的连续性。
        """)

    with st.expander("2. 实验土柱主体"):
        st.write("""
        - **有机玻璃试样筒**：内置原位采集的滨海盐沼土样。
        - **顶部/底部隔温板**：采用高分子绝热材料，确保热量仅在垂直方向传递，符合一维模拟假设。
        """)

    with st.expander("3. 自动化监测系统"):
        st.write("""
        - **多通道温度巡检仪**：实时采集并记录各深度层位的温度动态数据。
        - **原位传感器对**：集成温度与土壤电导率(EC)探头，捕捉水盐前锋的实时位置。
        """)

st.divider()

# 底部展示关键技术指标
st.subheader(" 装置运行参数")
c1, c2, c3 = st.columns(3)
c1.metric("温度控制精度", "±0.1 °C")
c2.metric("有效监测深度", "100 cm")
c3.metric("采样时间分辨率", "1 min")

st.info(" **系统关联**：本系统通过读取采集仪器输出的 CSV 文件，自动将上述硬件参数转化为数字化模型边界条件。")
