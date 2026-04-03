# -*- coding: utf-8 -*-
import streamlit as st
import os

# 页面配置
st.set_page_config(page_title="实验装置说明", layout="wide")

st.title("🔬 室内一维水热盐运移实验装置")

# 页面导言
st.markdown("""
本反演系统的物理模型与参数标定均基于以下自主研发的实验平台。
通过模拟不同边界条件下（如恒温水浴、冻融循环）的土壤水分运移，为软件算法提供实测验证数据。
""")

st.divider()

# 主内容区
col_img, col_text = st.columns([3, 2])

with col_img:
    # 加载装置图
    img_path = "apparatus_diagram.jpg"
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True, caption="室内一维土柱运移实验装置全景图")
    else:
        st.error(f"未找到图片文件: {img_path}。请确保图片已上传至根目录。")

with col_text:
    st.subheader("🛠️ 核心硬件构成")
    
    with st.expander("1. 恒温动力系统", expanded=True):
        st.write("""
        - **THZ-82A 恒温水浴振荡器**：作为系统的热源/冷源中心，提供稳定的补给水温度。
        - **循环水泵 (Water Pump)**：通过蓝色管线将恒温水注入土柱底部隔温板，模拟地下水边界。
        """)

    with st.expander("2. 实验土柱主体"):
        st.write("""
        - **试样容器**：高透明度有机玻璃柱，便于观察土层变化。
        - **隔温盖板**：顶部与底部均设有高分子隔温材料，确保一维垂直热传导的准确性。
        """)

    with st.expander("3. 自动化采集系统"):
        st.write("""
        - **多通道温度巡检仪**：连接分布在土柱不同深度的热电偶，实现毫秒级采样。
        - **土壤电导率传感器**：与温度传感器成对布置，实时监测盐分前锋的运移位置。
        """)

st.divider()

# 底部物理指标看板 (展示装置精度)
st.subheader("📊 装置运行参数")
m1, m2, m3 = st.columns(3)
m1.metric("温控精度", "±0.1 °C")
m2.metric("有效采样深度", "1.0 m")
m3.metric("采样频率", "10 Hz")

st.info("💡 提示：本软件通过 CSV 接口读取‘多通道温度巡检仪’生成的实测数据，并进行自动化的参数重构。")
