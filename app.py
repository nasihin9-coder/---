# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. 页面配置
st.set_page_config(
    page_title="水盐监测系统 v1.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. 初始化全局状态 (确保跨页面数据共享)
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'dh' not in st.session_state:
    st.session_state['dh'] = 8.0e-5
if 'q' not in st.session_state:
    st.session_state['q'] = 2.0e-6

# 3. 侧边栏：参数控制与操作指南
with st.sidebar:
    st.header("⚙️ 全局模型参数")
    st.session_state['dh'] = st.number_input("弥散系数 (Dh)", value=st.session_state['dh'], format="%.1e")
    st.session_state['q'] = st.number_input("垂直通量 (q)", value=st.session_state['q'], format="%.1e")
    
    st.markdown("---")
    st.info("""
    **🚀 操作快速入门：**
    1. **本页**：上传传感器导出的 CSV 数据。
    2. **侧边栏**：根据实验条件微调 $D_h$ 与 $q$。
    3. **导航栏**：切换至 **Temperature** 或 **Salinity** 页面查看反演看板。
    """)

# 4. 主界面标题
st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

# 5. 原理图展示与容错处理
# 注意：请确保 GitHub 仓库根目录下有 model_diagram.jpg 文件
img_path = "model_diagram.jpg"
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True, caption="滨海盐沼湿地水热盐运移物理机制示意图")
else:
    st.warning(f"⚠️ 提示：未在根目录检测到原理图文件 ({img_path})。请检查文件名是否正确。")

# 6. 科学描述看板 (优化美观度)
st.container(border=True).markdown(f"""
### 🔬 系统核心概念与物理机制解析

本系统专为**滨海盐沼湿地**复杂的多场耦合环境设计，通过数值模型与实测数据融合，深度解析以下过程：

* **多源补给机制**：集成降雨入渗、地表蒸发及植物蒸腾（ET）的水分交换模型。
* **水热盐耦合运移**：模拟土壤水流、热量传导与盐分溶质在多孔介质中的同步动力学过程。
* **潮汐与海水交互**：考虑高潮位波动及风暴潮引起的倒灌场景，支持地下水与海水间的双向反馈。
* **空间场重构**：基于监测数据进行偏微分方程逆向求解，精准重构水、盐通量的空间剖面。
""", help="说明：上述机制均在模型计算中通过参数化方案体现。")

st.divider()

# 7. 数据上传模块
st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("请上传传感器采集的标准 CSV 监测文件", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state['df'] = df
        # 自动识别列名（假设前三列为关键数据）
        cols = df.columns.tolist()
        if len(cols) >= 3:
            st.session_state['z_col'], st.session_state['t_col'], st.session_state['s_col'] = cols[0], cols[1], cols[2]
            st.success(f"✅ 成功加载 {len(df)} 行监测记录！请切换页面开始分析。")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.error("❌ 数据格式异常：请确保 CSV 至少包含深度、温度、盐度三列。")
    except Exception as e:
        st.error(f"❌ 文件解析出错: {e}")
else:
    # 提供内置测试数据下载，解决 FileNotFoundError 问题
    @st.cache_data
    def get_sample_data():
        z = np.linspace(0, 1, 20)
        temp = 25 - 5 * z + np.random.normal(0, 0.1, 20)
        salt = 1000 + 500 * np.exp(3 * z)
        return pd.DataFrame({"Depth(m)": z, "Temp(C)": temp, "Salt(mg/L)": salt}).to_csv(index=False).encode('utf-8')

    st.info("💡 暂无数据？您可以下载下方示例文件进行测试：")
    st.download_button("📥 下载标准测试数据 (CSV)", data=get_sample_data(), file_name="sample_monitor_data.csv", mime="text/csv")
