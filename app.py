# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# 1. 基础配置：必须是 Streamlit 命令的第一行
st.set_page_config(
    page_title="水盐监测系统V1.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. 初始化全局 Session State（防止切换页面时数据丢失）
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'dh' not in st.session_state:
    st.session_state['dh'] = 8.0e-5
if 'q' not in st.session_state:
    st.session_state['q'] = 2.0e-6

# 3. 侧边栏：全局参数配置
with st.sidebar:
    st.header("⚙️ 全局参数微调")
    st.session_state['dh'] = st.number_input(
        "弥散系数 (Dh)", 
        value=st.session_state['dh'], 
        format="%.1e",
        help="调整该参数将改变盐度拟合曲线的斜率"
    )
    st.session_state['q'] = st.number_input(
        "垂直通量 (q)", 
        value=st.session_state['q'], 
        format="%.1e"
    )
    st.markdown("---")
    st.info("💡 提示：在下方或左侧菜单切换功能页面。")

# 4. 主界面内容
st.title("🌊 土壤热-盐耦合监测系统 - 主控台")
st.markdown("---")

# 数据上传模块
uploaded_file = st.file_uploader("第一步：上传实验数据 (CSV)", type="csv")

if uploaded_file:
    # 读取并存入 session_state
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns] # 清理列名空格
    st.session_state['df'] = df
    
    st.success("✅ 数据上传成功！")
    
    # 自动识别关键列，方便子页面调用
    try:
        st.session_state['t_col'] = [c for c in df.columns if any(k in c.lower() for k in ['temp', '温度'])][0]
        st.session_state['s_col'] = [c for c in df.columns if any(k in c.lower() for k in ['sal', '盐度'])][0]
        st.info(f"🔍 识别成功：温度[{st.session_state['t_col']}], 盐度[{st.session_state['s_col']}]")
        st.markdown("### 👈 现在请点击左侧菜单查看【温度】或【盐度】分析图表")
    except IndexError:
        st.error("❌ 未能在 CSV 中识别到 'Temperature' 或 'Salinity' 列，请检查文件格式。")

else:
    st.warning("👋 欢迎使用！请先上传传感器采集的 CSV 数据文件以开启分析模块。")
    # 展示数据格式建议
    with st.expander("查看建议的 CSV 数据格式"):
        st.code("Temperature,Salinity\n28.5,35000\n27.2,24000\n26.1,18500\n...")

# 底部页脚
st.markdown("---")
st.caption("© 2026 土壤水盐运移监测数值模拟系统 | 软著申请专用版本")
