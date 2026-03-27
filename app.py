# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 页面基本配置
st.set_page_config(
    page_title="水盐监测系统V1.0", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. 初始化全局数据状态
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'dh' not in st.session_state:
    st.session_state['dh'] = 8.0e-5
if 'q' not in st.session_state:
    st.session_state['q'] = 2.0e-6

# --- 3. 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ 全局模型参数")
    st.session_state['dh'] = st.number_input(
        "弥散系数 (Dh)", 
        value=st.session_state['dh'], 
        format="%.1e"
    )
    st.session_state['q'] = st.number_input(
        "垂直通量 (q)", 
        value=st.session_state['q'], 
        format="%.1e"
    )
    st.markdown("---")
    st.info("💡 操作指南：\n1. 在本页上传数据\n2. 调整左侧参数\n3. 切换子页面查看分析")

# --- 4. 主界面布局 ---
st.title("🌊 土壤热-盐耦合监测系统 - 主控台")

# A. 插入原理示意图
# 请确保文件名与 GitHub 上的文件名一致
try:
    st.image("model_diagram.jpg", 
             caption="图 1：滨海盐沼及水盐运移控制因素物理模型示意图", 
             use_container_width=True)
except:
    st.warning("⚠️ 未检测到原理图文件 (model_diagram.jpg)，请上传至 GitHub 仓库根目录。")

st.markdown("---")

# B. 数据上传模块
st.subheader("第一步：上传实验观测数据 (CSV)")
uploaded_file = st.file_uploader("选择传感器采集的 CSV 文件", type="csv")

if uploaded_file:
    # 读取数据
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]
    st.session_state['df'] = df
    
    st.success("✅ 数据上传成功！系统已激活分析模块。")
    
    # 展示数据预览
    with st.expander("点击查看原始数据预览"):
        st.dataframe(df.head(10), use_container_width=True)
    
    # 自动识别列名逻辑
    try:
        st.session_state['t_col'] = [c for c in df.columns if any(k in c.lower() for k in ['temp', '温度'])][0]
        st.session_state['s_col'] = [c for c in df.columns if any(k in c.lower() for k in ['sal', '盐度'])][0]
        st.markdown(f"📊 **自动识别结果**：已定位到温度列 `{st.session_state['t_col']}` 和盐度列 `{st.session_state['s_col']}`。")
        st.info("👈 **现在请在左侧菜单切换到【Temperature】或【Salinity】页面进行深度分析。**")
    except IndexError:
        st.error("❌ 无法自动识别列名，请确保 CSV 包含 'Temperature' 和 'Salinity' 关键词。")

else:
    st.warning("👋 请上传 CSV 数据文件以开启数值模拟与反演分析。")
    # 展示建议格式
    st.code("Depth(m),Temperature,Salinity\n0.0,25.4,32000\n0.2,23.1,28500\n0.4,21.5,24000", language="csv")

# 5. 页脚
st.markdown("---")
st.caption("© 2026 滨海盐沼水盐运移数值模拟系统 | 软件著作权申请版本")
