import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.title("🌡️ Soil Temperature Profile Analysis")

if 'df' in st.session_state:
    df = st.session_state['df']
    t_col = [c for c in df.columns if 'temp' in c.lower() or '温度' in c][0]
    t_obs = df[t_col].values
    z_obs = np.linspace(0, 1.0, len(t_obs))

    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t_obs, z_obs, 'r-o', label='Measured Temperature')
    ax.set_xlabel("Temperature (degC)")
    ax.set_ylabel("Depth (m)")
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("Please upload data on the Home page first.")
