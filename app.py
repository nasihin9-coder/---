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

# 2. 初始化全局数据状态，新增深度列 z_col
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'z_col' not in st.session_state:
    st.session_state['z_col'] = None  # 深度列名
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
    st.info("💡 操作指南：\n1. 在本页上传包含 Depth 的数据\n2. 调整左侧参数\n3. 切换子页面查看分析")

# --- 4. 主界面布局 ---
st.title("🌊 土壤热-盐耦合监测系统 - 主控台")

# A. 插入原理示意图
# 根据您的仓库结构，统一使用 png 后缀
try:
    st.image("model_diagram.png", 
             caption="图 1：滨海盐沼及水盐运移控制因素物理模型示意图", 
             use_container_width=True)
except:
    st.warning("⚠️ 未检测到原理图文件 (model_diagram.png)，请确保文件已上传至 GitHub 仓库根目录。")

st.markdown("---")

# B. 数据上传模块
st.subheader("第一步：上传实验观测数据 (CSV)")
uploaded_file = st.file_uploader("选择传感器采集的 CSV 文件（需包含 Depth, Temperature, Salinity）", type="csv")

if uploaded_file:
    # 读取数据并清理列名空格
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]
    st.session_state['df'] = df
    
    st.success("✅ 数据上传成功！系统已激活深度剖面分析模块。")
    
    # 展示数据预览
    with st.expander("点击查看原始数据预览"):
        st.dataframe(df.head(10), use_container_width=True)
    
    # --- 核心更新：深度、温度、盐度列自动识别逻辑 ---
    cols = df.columns.tolist()
    try:
        # 1. 识别深度列 (匹配 depth, 深度, z)
        st.session_state['z_col'] = [c for c in cols if any(k in c.lower() for k in ['depth', '深度', 'z'])][0]
        # 2. 识别温度列 (匹配 temp, 温度)
        st.session_state['t_col'] = [c for c in cols if any(k in c.lower() for k in ['temp', '温度'])][0]
        # 3. 识别盐度列 (匹配 sal, 盐度)
        st.session_state['s_col'] = [c for c in cols if any(k in c.lower() for k in ['sal', '盐度'])][0]
        
        st.markdown(f"""
        📊 **列名自动识别成功**：
        - 📏 深度维度：`{st.session_state['z_col']}`
        - 🌡️ 温度维度：`{st.session_state['t_col']}`
        - 🧂 盐度维度：`{st.session_state['s_col']}`
        """)
        st.info("👈 **检测到深度数据，已优化绘图坐标。请切换到子页面查看实时剖面。**")
        
    except IndexError:
        st.error("❌ 无法自动识别必要列名。请确保 CSV 文件包含 'Depth', 'Temperature' 和 'Salinity'。")

else:
    st.warning("👋 请上传包含深度序列的 CSV 文件。")
    # 展示新版数据格式建议
    st.code("Depth(m),Temperature,Salinity\n0.0,25.4,35000\n0.1,24.8,32100\n0.2,23.1,28500", language="csv")

# 5. 页脚
st.markdown("---")
st.caption("© 2026 滨海盐沼水盐运移数值模拟系统 | 软著申请专用版")
