# -*- coding: utf-8 -*-
import streamlit as st
import os

# 1. 配置页面 (作为软著体现：系统架构清晰，功能模块化)
st.set_page_config(page_title="实验装置介绍", layout="wide")

st.title("🔬 一维冻融循环土柱实验装置 (硬件基础)")

# 2. 描述性文字 (软著体现：软件是基于真实的、特定的硬件实验平台开发的)
st.markdown("""
> 本软件所采用的数据反演算法与物理模型，均基于下图所示的“一维冻融循环土柱实验装置”开发。
> 该装置通过精密控制土柱顶部的制冷与加热，模拟野外环境的季节性冻融过程，并实时采集土柱内部的水分、温度、电导率等多物理场数据，为软件提供高精度的校准源数据。
""")

st.divider()

# 3. 核心图像展示与交互 (视图视图 V)
# 软著体现：系统具备完善的硬件原理解析功能。
col_img, col_desc = st.columns([2, 1])

with col_img:
    # 假设您的实验装置图文件名为 'experiment_setup.png' 且位于仓库根目录
    # 为了保证代码健壮性，使用 os.path.exists 检查文件是否存在
    image_path = "experiment_setup.png" # 请将您的 图14 重命名为此文件名并上传
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True, caption="图9 一维冻融循环土柱实验装置示意图")
    else:
        # 如果文件缺失，提供一个友好的提示（同时也方便您测试）
        st.error(f"❌ 未检测到实验装置图文件 ({image_path})。请将硬件原理解析图重命名为该文件名并上传至 GitHub 仓库根目录。")
        st.info("提示：您可以将图14上传为 'experiment_setup.png'。")

with col_desc:
    st.subheader("🛠️ 装置核心系统解析")
    
    # 采用 Expanders 折叠面板，展示“硬件-软件”的数据流向
    # 软著体现：软件具备对复杂硬件系统进行原理解析和数据管理的逻辑能力。
    
    with st.expander("❄️ 1. 温控与冻融模拟系统", expanded=True):
        st.markdown("""
        - **顶部/底部制冷系统**：通过循环冷却液，精密控制土柱两端的边界温度（可降至-30°C）。
        - **软硬关联**：该系统产生的温度边界数据，是软件“温度剖面分析”模块的输入条件。
        """)

    with st.expander("📊 2. 数据采集与传感器系统"):
        st.markdown("""
        - **马氏瓶/水位线**：维持恒定水头边界。
        - **多参数传感器**：实时采集不同深度的**土壤水分、温度、电导率**（图上箭头所示的6排探头）。
        - **软硬关联**：这是软件最核心的数据源。传感器通过 CR1000X 采集的数据 CSV，将直接上传至软件主页。
        """)

    with st.expander("💻 3. 数据处理与界面展示系统"):
        st.markdown("""
        - **多通道温度巡检仪 & CR1000X series**：将模拟信号转换为数字信号，进行初步存储。
        - **电脑 (终端界面)**：即本软件的运行环境，负责数据的进一步反演计算、可视化展示与存储。
        """)

# 4. 底部声明 (增强专业性)
st.divider()
st.caption("注：软件系统中的算法逻辑（如偏微分方程求解、B-Spline插值）均需结合该硬件装置的特定物理参数（如试样容器材质、热扩散率）进行校准。")
