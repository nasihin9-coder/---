import streamlit as st
import pandas as pd
import numpy as np

# 设置全局页面配置
st.set_page_config(page_title="水盐监测系统 V1.0", layout="wide")

# --- 核心计算引擎 ---
class CoupledEngine:
    @staticmethod
    def solve_model(c_start, dh, q):
        # 简化版物理模型，仅用于生成示例曲线
        z = np.linspace(0, 1.0, 50)
        c = np.full(len(z), 500.0)
        c[0] = c_start
        # 模拟扩散和对流趋势
        curve = 500 + (c_start - 500) * np.exp(-(3.5 * dh * 1e4) * z)
        return z, curve

def main():
    st.sidebar.title("🛠️ 全局配置中心")
    st.title("🌡️ 变饱和带土壤热-盐耦合监测系统")
    st.markdown("---")

    # 第一步：数据上传
    uploaded_file = st.file_uploader("第一步：上传传感器数据 (CSV)", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # 将数据存储在 Session State 中，供其他页面共享
        st.session_state['df'] = df
        
        # 自动列识别
        df.columns = [c.strip() for c in df.columns]
        st.session_state['t_col'] = [c for c in df.columns if any(k in c.lower() for k in ['temp', '温度'])][0]
        st.session_state['s_col'] = [c for c in df.columns if any(k in c.lower() for k in ['sal', '盐'])][0]
        
        st.success("✅ 数据已上传并在各页面共享。")
        
    else:
        st.warning("⚠️ 请先上传数据以解锁图表页面。")

    # 第二步：侧边栏参数设置
    st.sidebar.markdown("### 模型参数微调")
    dh = st.sidebar.number_input("弥散系数 Dh", value=8.0e-5, format="%.1e")
    q = st.sidebar.number_input("垂直通量 q", value=2.0e-6, format="%.1e")
    
    # 存储参数供其他页面共享
    st.session_state['dh'] = dh
    st.session_state['q'] = q

if __name__ == "__main__":
    main()
