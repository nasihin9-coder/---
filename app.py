# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image

# 1. 页面配置：设置标题、布局及侧边栏初始状态
st.set_page_config(
    page_title="水盐监测系统 v1.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. 初始化全局状态 (确保数据与参数在页面间持久化)
state_defaults = {
    'df': None, 
    'dh': 8.0e-5, 
    'q': 2.0e-6,
    'z_col': None,
    't_col': None,
    's_col': None,
    'temp_calc_done': False,
    'flux_calc_done': False,
    'sal_calc_done': False
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 3. 侧边栏：全局物理参数控制
with st.sidebar:
    st.header("⚙️ 全局模型参数")
    st.session_state['dh'] = st.number_input(
        "弥散系数 (Dh)", 
        value=st.session_state['dh'], 
        format="%.1e",
        help="控制溶质在多孔介质中的弥散强度"
    )
    st.session_state['q'] = st.number_input(
        "垂直通量 (q)", 
        value=st.session_state['q'], 
        format="%.1e",
        help="反映地下水补给或蒸发的垂直流速"
    )
    
    st.divider()
    st.info("""
    **🚀 操作快速入门：**
    1. **本页**：上传监测数据 CSV。
    2. **侧边栏**：根据实验条件微调参数。
    3. **子页面**：切换查看分析结果。
    """)

# 4. 主界面标题
st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

# 5. 原理图展示 (容错处理：确保 GitHub 部署不因图片缺失报错)
img_path = "model_diagram.jpg"
if os.path.exists(img_path):
    try:
        img = Image.open(img_path)
        st.image(img, use_container_width=True, caption="滨海盐沼湿地水热盐运移物理机制示意图")
    except Exception:
        st.error("⚠️ 原理图文件损坏，请尝试重新上传。")
else:
    st.warning(f"⚠️ 提示：未在根目录检测到原理图文件 ({img_path})。")

# 6. 系统科学背景解析
st.container(border=True).markdown("""
### 🔬 系统核心概念与物理机制解析

本系统专为**滨海盐沼湿地**复杂的多场耦合环境设计，通过数值模型与实测数据融合，深度解析以下过程：

* **多源补给机制**：集成降雨入渗、地表蒸发及植物蒸腾（ET）的水分交换模型。
* **水热盐耦合运移**：模拟土壤水流、热量传导与盐分溶质在多孔介质中的同步动力学过程。
* **潮汐与海水交互**：考虑高潮位波动及风暴潮引起的倒灌场景，支持地下水与海水交互反馈。
* **空间场重构**：基于监测数据进行偏微分方程逆向求解，精准重构水、盐通量的空间剖面。
""")

st.divider()

# 7. 数据上传模块
st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("请上传传感器采集的标准 CSV 监测文件", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state['df'] = df
        
        # 自动识别列名：默认前三列为 深度、温度、盐度
        cols = df.columns.tolist()
        if len(cols) >= 3:
            st.session_state['z_col'] = cols[0]
            st.session_state['t_col'] = cols[1]
            st.session_state['s_col'] = cols[2]
            
            st.success(f"✅ 数据加载成功！共计 {len(df)} 行数据。")
            st.markdown("### 📊 原始数据预览 (前 5 行)")
            st.dataframe(df.head(), use_container_width=True)
            st.info("💡 提示：现在您可以切换到侧边栏的其他页面查看分析结果。")
        else:
            st.error("❌ 数据列不足：请确保 CSV 文件至少包含三列（深度、温度、盐度）。")
            
    except Exception as e:
        st.error(f"❌ 解析失败: {e}")
else:
    # 辅助功能：提供标准测试数据下载，供用户测试环境
    @st.cache_data
    def generate_sample_csv():
        z = np.linspace(0, 1, 20)
        temp = 25 - 5 * z + np.random.normal(0, 0.2, 20)
        salt = 1000 + 500 * np.exp(3 * z) + np.random.normal(0, 50, 20)
        sample_df = pd.DataFrame({
            "Depth(m)": z,
            "Temp(C)": temp,
            "Salinity(mg/L)": salt
        })
        return sample_df.to_csv(index=False).encode('utf-8')

    st.markdown("💡 **暂无数据？** 下载下方标准示例文件进行体验：")
    st.download_button(
        label="📥 下载标准测试数据 (CSV)",
        data=generate_sample_csv(),
        file_name="sample_monitoring_data.csv",
        mime="text/csv"
    )
