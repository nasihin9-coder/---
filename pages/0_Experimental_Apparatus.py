# -*- coding: utf-8 -*-
import streamlit as st
import os

# 页面配置：将其设为侧边栏第一个页面
st.set_page_config(page_title="实验装置说明", layout="wide")

st.title("🔬 室内一维水热盐运移实验装置")

# 页面导言
st.markdown("""
本反演系统的物理模型与参数标定均基于以下自主研发的实验平台。
通过模拟不同边界条件下（如恒温水浴补给、海水倒灌循环）的土壤水分运移，为软件算法提供高精度的实测验证数据。
""")

st.divider()

# 主内容区：左图右文
col_img, col_text = st.columns([3, 2])

with col_img:
    # 加载最新的装置图
    img_path = "apparatus_diagram.jpg"
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True, caption="室内一维土柱运移实验装置全景图")
    else:
        st.error(f"未找到图片文件: {img_path}。请确保图片已上传至根目录。")

with col_text:
    st.subheader("🛠️ 核心硬件构成解析")
    
    with st.expander("1. 恒温水循环动力系统", expanded=True):
        st.write("""
        - **THZ-82A 恒温水浴振荡器**：作为系统的核心温控中心，提供稳定的补给水环境。
        - **水泵 (WATER PUMP)**：通过循环管线将恒温水注入系统，模拟地下水补给或潮汐侵蚀。
        - **外部水槽**：提供大容量的恒温介质存储。
        """)

    with st.expander("2. 实验土柱与隔温结构"):
        st.write("""
        - **实验土样柱**：内置多层不同密度的盐沼土壤，模拟真实的底层剖面。
        - **顶部与底部隔温板**：有效减少环境热交换，确保系统内热传导严格遵循一维垂直运移模型。
        """)

    with st.expander("3. 自动化监测与采集"):
        st.write("""
        - **多通道温度巡检仪**：实时监控土柱各层位的温度波动，并直接输出 CSV 数据供本系统分析。
        - **土壤电导率/温度传感器对**：成对布置的探头（如 T, EC 标注所示），精准捕捉盐分前锋的运移轨迹。
        """)

st.divider()

# 底部装置关键指标 (体现专业科研背景)
st.subheader("📊 装置运行关键指标")
m1, m2, m3 = st.columns(3)
m1.metric("温控稳定性", "±0.05 °C")
m2.metric("传感器采样精度", "0.01 mm")
m3.metric("支持最大土柱高度", "120 cm")

st.info("💡 系统关联说明：本软件通过文件接口读取该装置产生的监测数据，并结合左侧侧边栏配置的“全局模型参数”进行深度反演。")
