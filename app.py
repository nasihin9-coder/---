# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="水盐监测系统 v1.0", layout="wide", initial_sidebar_state="expanded")

if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'dh' not in st.session_state:
    st.session_state['dh'] = 8.0e-5
if 'q' not in st.session_state:
    st.session_state['q'] = 2.0e-6

st.sidebar.header("⚙️ 全局模型参数")
st.session_state['dh'] = st.sidebar.number_input("弥散系数 (Dh)", value=st.session_state['dh'], format="%.1e")
st.session_state['q'] = st.sidebar.number_input("垂直通量 (q)", value=st.session_state['q'], format="%.1e")

st.sidebar.info("💡 操作指南:\n1. 在本页上传数据\n2. 调整左侧参数\n3. 切换子页面查看分析")

st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

if os.path.exists("model_diagram.jpg"):
    st.image("model_diagram.jpg", use_container_width=True)
else:
    st.warning("⚠️ 未检测到原理图文件 (model_diagram.jpg)，请上传至 GitHub 仓库根目录。")

st.header("📂 步骤 1：上传监测数据")

uploaded_file = st.file_uploader("选择传感器采集的 CSV 文件", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state['df'] = df
        cols = df.columns.tolist()
        st.session_state['z_col'] = cols[0]
        st.session_state['t_col'] = cols[1]
        st.session_state['s_col'] = cols[2]
        
        st.success("✅ 数据加载成功！请点击左侧菜单栏进入各个子页面进行分析。")
        st.dataframe(df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"❌ 数据解析失败，请检查 CSV 格式。错误信息: {e}")
else:
    st.info("👆 请在上方拖拽或选择文件上传。")
    
    # 动态生成测试数据，告别 FileNotFoundError
    @st.cache_data
    def generate_dummy_csv():
        dummy_df = pd.DataFrame({
            "Depth (m)": np.linspace(0, 1, 20),
            "Temp (°C)": 20 - np.linspace(0, 1, 20) * 3 + np.random.normal(0, 0.2, 20),
            "Salinity (mg/L)": 1000 + np.exp(np.linspace(0, 5, 20)) * 200
        })
        return dummy_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 下载标准测试数据",
        data=generate_dummy_csv(),
        file_name="standard_test_data.csv",
        mime="text/csv"
    )
