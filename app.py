# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os

# 页面配置
st.set_page_config(page_title="水盐监测系统 v1.0", layout="wide", initial_sidebar_state="expanded")

# 初始化全局状态
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'dh' not in st.session_state:
    st.session_state['dh'] = 8.0e-5
if 'q' not in st.session_state:
    st.session_state['q'] = 2.0e-6

# 侧边栏：全局控制
st.sidebar.header("⚙️ 全局模型参数")
st.session_state['dh'] = st.sidebar.number_input("弥散系数 (Dh)", value=st.session_state['dh'], format="%.1e")
st.session_state['q'] = st.sidebar.number_input("垂直通量 (q)", value=st.session_state['q'], format="%.1e")

st.sidebar.markdown("---")
st.sidebar.info("""
**操作指南：**
1. 在本页上传数据。
2. 调整左侧物理参数。
3. 切换子页面查看分析结果。
""")

# 主界面标题
st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

# 1. 原理图展示
img_path = "model_diagram.jpg"
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True)
else:
    st.warning(f"⚠️ 未检测到原理图文件 ({img_path})")

# 2. 优化后的科学介绍文字
st.info("""
### 🔬 系统核心概念与物理机制解析

本系统专为**滨海盐沼湿地**复杂的多场耦合环境设计，旨在模拟与反演以下核心物理过程：

* **多源补给机制**：集成降雨入渗、地表蒸发及植物蒸腾（ET）的水分交换模型。
* **水热盐耦合运移**：模拟土壤水流、热量传导与盐分溶质在多孔介质中的同步动力学过程。
* **潮汐与海水交互**：充分考虑高潮位、潮汐波动及风暴潮引起的倒灌场景，支持地下水位与海水间的双向交互反馈机制。
* **空间场重构**：通过对地下水位以下及非饱和带的监测数据进行偏微分方程逆向求解，实现水、盐通量的空间剖面重构。
""")

st.divider()

# 3. 数据上传模块
st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("选择传感器采集的标准 CSV 文件", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state['df'] = df
        # 默认前三列为 深度, 温度, 盐度
        cols = df.columns.tolist()
        st.session_state['z_col'], st.session_state['t_col'], st.session_state['s_col'] = cols[0], cols[1], cols[2]
        st.success("✅ 数据加载成功！请前往侧边栏切换分析页面。")
        st.dataframe(df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"❌ 解析失败: {e}")
else:
    # 自动生成测试数据下载链接（防止用户没有数据时报错）
    @st.cache_data
    def generate_dummy_csv():
        z = np.linspace(0, 1, 25)
        data = {
            "Depth(m)": z,
            "Temp(C)": 20 - z * 5 + np.random.normal(0, 0.2, 25),
            "Salinity(mg/L)": 1000 + np.exp(z * 3) * 500 + np.random.normal(0, 100, 25)
        }
        return pd.DataFrame(data).to_csv(index=False).encode('utf-8')

    st.markdown("💡 **没有数据？** 您可以下载示例文件进行体验：")
    st.download_button("📥 下载测试数据 (CSV)", data=generate_dummy_csv(), file_name="test_data.csv", mime="text/csv")
