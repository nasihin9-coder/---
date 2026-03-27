import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="水盐监测系统 v1.0", layout="wide")

# 初始化全局参数
for key, val in {'df': None, 'dh': 8.0e-5, 'q': 2.0e-6}.items():
    if key not in st.session_state: st.session_state[key] = val

st.sidebar.header("⚙️ 全局模型参数")
st.session_state['dh'] = st.sidebar.number_input("弥散系数 (Dh)", value=st.session_state['dh'], format="%.1e")
st.session_state['q'] = st.sidebar.number_input("垂直通量 (q)", value=st.session_state['q'], format="%.1e")

st.title("🌊 滨海盐沼水热盐耦合运移反演系统")

# 检查并显示图片
if os.path.exists("model_diagram.jpg"):
    st.image("model_diagram.jpg", use_container_width=True)

st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("上传 CSV 格式监测数据", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state['df'] = df
    cols = df.columns.tolist()
    st.session_state['z_col'], st.session_state['t_col'], st.session_state['s_col'] = cols[0], cols[1], cols[2]
    st.success("✅ 数据加载成功！")
    st.dataframe(df.head())
else:
    # 动态生成测试数据避免 FileNotFoundError
    @st.cache_data
    def get_test_csv():
        z = np.linspace(0, 1, 20)
        t = 25 - z * 5 + np.random.normal(0, 0.2, 20)
        s = 1000 + np.exp(z * 3.5) * 500
        return pd.DataFrame({"Depth(m)":z, "Temp(C)":t, "Salinity(mg/L)":s}).to_csv(index=False).encode('utf-8')
    st.download_button("📥 下载标准测试数据", data=get_test_csv(), file_name="test.csv")
