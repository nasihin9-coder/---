# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image

st.set_page_config(page_title="水盐监测系统 v1.0", layout="wide")

# 初始化全局状态
for key, val in {'df': None, 'dh': 8.0e-5, 'q': 2.0e-6}.items():
    if key not in st.session_state: st.session_state[key] = val

st.sidebar.header("⚙️ 全局模型参数")
st.session_state['dh'] = st.sidebar.number_input("弥散系数 (Dh)", value=st.session_state['dh'], format="%.1e")
st.session_state['q'] = st.sidebar.number_input("垂直通量 (q)", value=st.session_state['q'], format="%.1e")

st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

# 容错处理：确保图片存在且格式正确
img_path = "model_diagram.jpg"
if os.path.exists(img_path):
    try:
        img = Image.open(img_path)
        st.image(img, use_container_width=True, caption="滨海盐沼湿地水热盐运移物理机制示意图")
    except:
        st.error("⚠️ 原理图文件损坏，请重新上传。")

st.info("""
### 🔬 系统核心概念与物理机制解析
* **多源补给机制**：集成降雨入渗、地表蒸发及植物蒸腾的水分交换模型。
* **水热盐耦合运移**：模拟土壤水流、热量传导与盐分溶质在多孔介质中的同步动力学过程。
* **潮汐与海水交互**：考虑高潮位波动及风暴潮引起的倒灌场景。
""")

st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("上传 CSV 监测文件", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state['df'] = df
    st.success("✅ 数据加载成功！")
    st.dataframe(df.head())
else:
    # 解决 FileNotFoundError：提供动态生成的示例数据
    @st.cache_data
    def get_sample():
        z = np.linspace(0, 1, 20)
        return pd.DataFrame({"Depth(m)": z, "Temp(C)": 25-5*z, "Salt(mg/L)": 1000+500*np.exp(3*z)}).to_csv(index=False).encode('utf-8')
    st.download_button("📥 下载标准测试数据", data=get_sample(), file_name="sample.csv")
