import streamlit as st
import pandas as pd

st.set_page_config(page_title="水盐监测系统V1.0", layout="wide")

st.title("🌊 土壤热-盐耦合监测系统 - 主控台")
st.sidebar.success("请在上方选择功能页面")

# 初始化全局参数
if 'dh' not in st.session_state:
    st.session_state['dh'] = 8.0e-5
if 'q' not in st.session_state:
    st.session_state['q'] = 2.0e-6

# 侧边栏公共设置
st.sidebar.header("⚙️ 全局参数微调")
st.session_state['dh'] = st.sidebar.number_input("弥散系数 (Dh)", value=st.session_state['dh'], format="%.1e")
st.session_state['q'] = st.sidebar.number_input("垂直通量 (q)", value=st.session_state['q'], format="%.1e")

# 数据上传逻辑
uploaded_file = st.file_uploader("第一步：上传实验数据 (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state['df'] = df  # 关键：将数据存入 session_state
    st.success("✅ 数据上传成功！请点击左侧菜单查看分析图表。")
else:
    st.info("👋 请先上传 CSV 数据文件以开启分析模块。")
