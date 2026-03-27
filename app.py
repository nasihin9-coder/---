# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="水热盐耦合反演系统", layout="wide", page_icon="🌍")

st.title("🌍 滨海盐沼水热盐耦合运移反演系统")

st.markdown("""
> **欢迎使用！** 本系统专为研究滨海盐沼湿地地下水与土壤热量、盐分的多场耦合运移机制而设计。
> 支持正向物理模拟与偏微分方程逆向反演，兼容自上而下（蒸发型）与自下而上（海水倒灌型）双向运移场景。
""")

st.divider()

st.header("📂 步骤 1：上传监测数据")
uploaded_file = st.file_uploader("请上传标准的 CSV 格式文件", type=['csv'])

if uploaded_file is not None:
    try:
        # 尝试读取数据
        df = pd.read_csv(uploaded_file)
        
        # 💥 容错拦截 1：文件是否为空
        if df.empty:
            st.error("❌ 读取失败：上传的文件为空，请检查文件内容。")
            st.stop() # 终止后续代码运行
            
        st.success("✅ 文件读取成功！")
        
        # 💥 容错拦截 2：交互式列名映射 (防止列名写错导致崩溃)
        st.subheader("⚙️ 步骤 2：数据列匹配")
        st.info("💡 系统已尝试自动识别列名。如果识别错误，请在下方手动指定数据对应的列。")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # 智能猜测：寻找包含 'Depth' 的列名，找不到则默认选第0列
            z_guess = next((col for col in df.columns if 'Depth' in col or '深度' in col), df.columns[0])
            z_idx = list(df.columns).index(z_guess)
            z_col = st.selectbox("📌 指定【深度】列", df.columns, index=z_idx)
            
        with col2:
            t_guess = next((col for col in df.columns if 'Temp' in col or '温度' in col), df.columns[min(1, len(df.columns)-1)])
            t_idx = list(df.columns).index(t_guess)
            t_col = st.selectbox("🌡️ 指定【温度】列", df.columns, index=t_idx)
            
        with col3:
            s_guess = next((col for col in df.columns if 'Sal' in col or '盐度' in col), df.columns[min(2, len(df.columns)-1)])
            s_idx = list(df.columns).index(s_guess)
            s_col = st.selectbox("🧂 指定【盐度】列", df.columns, index=s_idx)

        # 💥 容错拦截 3：数据类型严格校验 (防止把带有文本的列拿去进行微积分运算)
        if not pd.api.types.is_numeric_dtype(df[z_col]) or \
           not pd.api.types.is_numeric_dtype(df[t_col]) or \
           not pd.api.types.is_numeric_dtype(df[s_col]):
            st.error(f"❌ 数据类型错误：您选择的列中包含非数字类型（可能是包含单位的文本，如'15m'，或存在空值）。请清理成纯数字后再试。")
            st.dataframe(df.head()) # 展示前几行让用户看看哪里错了
            st.stop()

        # 💥 容错拦截 4：数据量验证
        if len(df) < 5:
            st.warning("⚠️ 警告：数据点少于5个，可能会导致偏微分求解和曲线平滑插值失败，建议补充数据点。")

        st.divider()
        
        # 确认按钮
        if st.button("🚀 验证无误，加载数据并进入系统", type="primary", use_container_width=True):
            # 将安全的数据存入全局状态
            st.session_state['df'] = df
            st.session_state['z_col'] = z_col
            st.session_state['t_col'] = t_col
            st.session_state['s_col'] = s_col
            
            # 清除之前可能的计算状态缓存，防止换数据后残留旧图
            st.session_state['temp_calc_done'] = False
            st.session_state['sal_calc_done'] = False
            st.session_state['flux_calc_done'] = False
            
            st.balloons() # 放个气球庆祝一下
            st.success("🎉 数据加载完毕！请点击左侧边栏（如：温度剖面分析、盐度拟合分析）开始您的科研反演工作。")
            
    # 💥 容错拦截 5：捕获底层解析异常
    except pd.errors.EmptyDataError:
        st.error("❌ 解析失败：CSV文件没有包含任何有效数据。")
    except pd.errors.ParserError:
        st.error("❌ 解析失败：CSV文件格式损坏或分隔符不正确。")
    except Exception as e:
        st.error(f"❌ 发生未知系统错误：{str(e)}")

else:
    st.info("👈 请在上方拖拽或选择文件上传。")
    
    # 为了方便测试，提供快速生成测试数据的按钮
    if st.button("生成一份标准的海水倒灌测试数据 (CSV)"):
        import numpy as np
        depths = np.linspace(0, 1.0, 30)
        temp_signal = 22.0 + 6.5 * np.exp(-2.8 * depths) 
        temperature = np.round(temp_signal + np.random.normal(0, 0.12, 30), 2)
        salt_signal = 1200 + 33800 * np.exp(-4.5 * (1.0 - depths)) 
        salinity = np.round(salt_signal + np.random.normal(0, 350, 30), 1)
        salinity[-1] = 35000.0 
        test_df = pd.DataFrame({'Depth(m)': depths, 'Temperature(C)': temperature, 'Salinity(mg/L)': salinity})
        
        st.download_button(
            label="📥 下载测试数据",
            data=test_df.to_csv(index=False).encode('utf-8'),
            file_name='test_intrusion_data.csv',
            mime='text/csv',
            type="primary"
        )
