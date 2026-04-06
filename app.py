# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image

st.set_page_config(page_title="水盐监测系统 v1.0", layout="wide")

# 初始化全局状态，防止子页面弹出 KeyError
state_defaults = {
    'df': None, 'z_col': None, 't_col': None, 's_col': None,
    'dh': 8.0e-5, 'q': 2.0e-6,
    'temp_calc_done': False, 'flux_calc_done': False, 'sal_calc_done': False
}
for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

# 修复图片加载逻辑
img_path = "model_diagram.jpg"
if os.path.exists(img_path):
    try:
        img = Image.open(img_path)
        st.image(img, use_container_width=True, caption="滨海盐沼湿地水热盐运移物理机制示意图")
    except Exception:
        st.error("⚠️ 原理图文件格式不兼容，请确保它是标准的 JPG 格式。")

st.info("""
### 🔬 系统核心物理机制
* **水热盐耦合**：同步模拟多孔介质中的水分流动、热量传导与盐分扩散。
* **边界动力学**：考虑降雨、蒸腾以及潮汐引起的倒灌场景。
""")

st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("上传 CSV 监测文件", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state['df'] = df
    cols = df.columns.tolist()
    if len(cols) >= 3:
        # 默认分配：第一列深度，第二列温度，第三列盐度
        st.session_state['z_col'], st.session_state['t_col'], st.session_state['s_col'] = cols[0], cols[1], cols[2]
        st.success("✅ 数据加载成功！请点击侧边栏进入分析页面。")
        st.dataframe(df.head())
