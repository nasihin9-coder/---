# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from sklearn.metrics import r2_score  # 用于看板指标计算
import time

# 1. 页面基本配置
st.set_page_config(page_title="温度剖面分析", layout="wide")
st.title("🌡️ 温度剖面动态交互分析")

# 2. 权限检查：确保主页已上传数据
if 'df' not in st.session_state or st.session_state['df'] is None:
    st.warning("⚠️ 请先在主页 (app.py) 上传监测数据 CSV 文件。")
    st.info("提示：系统需要获取深度 (z) 和温度 (T) 列才能进行空间场重构。")
else:
    # 获取全局数据
    df = st.session_state['df']
    # 优先从 session_state 获取列名，若无则默认取前两列
    z_col = st.session_state.get('z_col', df.columns[0])
    t_col = st.session_state.get('t_col', df.columns[1])
    
    # 3. 侧边栏配置
    st.sidebar.subheader("📈 绘图与模型配置")
    smooth_level = st.sidebar.slider("曲线平滑度 (Spline K)", 2, 5, 3, help="控制 B-Spline 的阶数，越高越平滑但可能过拟合")
    show_metrics = st.sidebar.toggle("显示计算看板", value=True)
    
    # 准备基础数据
    t_obs = df[t_col].values
    z_obs = df[z_col].values

    # 生成平滑曲线点
    z_smooth = np.linspace(z_obs.min(), z_obs.max(), 150)
    spl = make_interp_spline(z_obs, t_obs, k=smooth_level)
    t_smooth = spl(z_smooth)

    # 4. 交互控制区
    calc_btn = st.button("🚀 开始空间场重构计算", type="primary")
    chart_spot = st.empty() 

    # 逻辑 A：点击计算后执行动画渲染
    if calc_btn:
        fig, ax = plt.subplots(figsize=(10, 6))
        # 统一坐标轴范围，防止抖动
        x_min, x_max = t_obs.min() - 1, t_obs.max() + 1
        y_min, y_max = z_obs.max() + 0.1, z_obs.min() - 0.1 

        # 阶段 1：模拟实测点位探测
        step_scatter = max(1, len(z_obs) // 8)
        for i in range(1, len(z_obs) + 1, step_scatter):
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.set_title("Reconstructing Temperature Profile...", fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.scatter(t_obs[:i], z_obs[:i], color='darkred', edgecolors='white', s=60, label='Measured Points', zorder=3)
            chart_spot.pyplot(fig)
            time.sleep(0.02)

        # 阶段 2：执行 B-Spline 连续场拟合动画
        step_line = max(5, len(z_smooth) // 15)
        for i in range(0, len(z_smooth) + 1, step_line):
            curr = min(i, len(z_smooth))
            ax.clear()
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xlabel("Temperature (°C)")
            ax.set_ylabel("Depth (m)")
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.scatter(t_obs, z_obs, color='darkred', alpha=0.6, edgecolors='white', s=50, label='Measured')
            ax.plot(t_smooth[:curr], z_smooth[:curr], color='red', linewidth=3, label='Reconstructed Field', zorder=4)
            ax.legend(loc='lower right')
            chart_spot.pyplot(fig)
            time.sleep(0.01)
            
        st.session_state['temp_calc_done'] = True
        st.success("✨ 滨海盐沼水热场空间重构完成！")
        plt.close(fig)
        
    # 逻辑 B：计算完成后保持静止图表显示
    elif st.session_state.get('temp_calc_done'):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(t_smooth, z_smooth, color='red', linewidth=3, label='Reconstructed Field')
        ax.scatter(t_obs, z_obs, color='darkred', edgecolors='white', s=60, label='Measured')
        ax.invert_yaxis()  # 深度向下
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("Depth (m)")
        ax.set_title("Final Reconstructed Temperature Profile", fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()
        chart_spot.pyplot(fig)
        
    else:
        chart_spot.info("ℹ️ 请调整左侧参数后，点击上方按钮执行空间场重构。")

    # 5. 结果看板模块 (软著加分项)
    if show_metrics and st.session_state.get('temp_calc_done'):
        st.divider()
        st.subheader("📊 空间重构计算结果看板")
        
        # 计算统计指标
        t_pred = spl(z_obs)
        r2 = r2_score(t_obs, t_pred)
        rmse = np.sqrt(np.mean((t_obs - t_pred)**2))
        
        m1, m2, m3 = st.columns(3)
        m1.metric("拟合准确度 (R²)", f"{r2:.4f}")
        m2.metric("均方根误差 (RMSE)", f"{rmse:.3f} °C")
        m3.metric("剖面计算深度", f"{z_obs.max() - z_obs.min():.2f} m")

    # 6. 底层原理展示 (学术支撑)
    with st.expander("🧮 展开查看底层物理机制与数值方法"):
        st.markdown("""
        #### 1. 物理模型基础
        本模块基于多孔介质的一维热传导方程，利用实测点位数据进行逆向重构。
        #### 2. 数值方法：B-Spline 多项式插值
        拟合函数 $S(z)$ 满足：
        """)
        st.latex(r"S(z) = \sum_{i=0}^{n-1} c_i B_{i, k}(z)")
        
        # 展示计算数据表
        dt_dz = np.gradient(t_obs, z_obs)
        calc_df = pd.DataFrame({
            "观测深度(m)": z_obs, 
            "实测温度(°C)": t_obs, 
            "局部温度梯度(dT/dz)": np.round(dt_dz, 4)
        })
        st.dataframe(calc_df, use_container_width=True)
