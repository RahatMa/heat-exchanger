import streamlit as st
import math
import numpy as np


st.title("🔧 Heat Exchanger Calculator")

# --- CONSTANTS ---
density = 998
viscosity = 0.001003
T1 = 350
T2 = 305
P = 101325  # Pressure in Pa
cp = 4182
k = 0.6
Pr_tube = 2.3246
Pr_shell = 5.1928
t = 1.27e-3
k_copper = 390

A_tube = 1.03e-04
A_shell = 5.07e-04
D_tube = 0.0114
D_shell = 0.0126


# --- USER INPUT ---
st.sidebar.header("Input Parameters")

V_tube = st.sidebar.number_input("Tube Velocity (m/s)", value=0.5)
V_shell = st.sidebar.number_input("Shell Velocity (m/s)", value=0.5)

Area = st.sidebar.number_input("Heat Exchanger Area (m²)", value=0.1348)


T_intube = st.sidebar.number_input("Tube Inlet Temp (°C)", value=90.0)
T_inshell = st.sidebar.number_input("Shell Inlet Temp (°C)", value=30.0)

# --- CALCULATION BUTTON ---
if st.button("Calculate"):

    m_dottube = density * V_tube * A_tube
    m_dotshell = density * V_shell * A_shell

    Re = density * V_tube * D_tube / viscosity
    Nu = 0.023 * Re ** (4 / 5) * Pr_tube ** (0.3)
    h_tube = Nu * k / D_tube

    Re_shell = density * V_shell * D_shell / viscosity
    Nu = 0.36 * Re_shell ** (0.55) * Pr_shell ** (1 / 3)
    h_shell = Nu * k / D_shell

    U = 1 / (1 / h_tube + t / k_copper + 1 / h_shell)

    # Capacity rates
    C_hot = m_dottube * cp
    C_cold = m_dotshell * cp

    C_min = min(C_hot, C_cold)
    C_max = max(C_hot, C_cold)

    c = C_min / C_max

    ntu = Area * U / C_min

    # --- Effectiveness ---
    def calculate_effectiveness(ntu, c):
        sqrt_term = math.sqrt(1 + c**2)

        exponent = math.exp(-ntu * sqrt_term)

        fraction = (1 + exponent) / (1 - exponent)

        denominator = 1 + c + (sqrt_term * fraction)
        epsilon = 2 * (denominator**-1)

        return epsilon

    effectiveness = calculate_effectiveness(ntu, c)

    Q_max = C_min * (T_intube - T_inshell)
    Q = effectiveness * Q_max

    T_outtube = T_intube - Q / C_hot
    T_outshell = T_inshell + Q / C_cold

    lmtd = (T_intube - T_outshell - T_outtube + T_inshell) / math.log(
        (T_intube - T_outshell) / (T_outtube - T_inshell)
    )

    # --- OUTPUT ---
    st.subheader("Results")

    st.write(f"Effectiveness: {effectiveness:.4f}")
    st.write(f"NTU: {ntu:.2f}")
    st.write(f"Heat Transfer (Q): {Q:.2f} W")
    st.write(f"LMTD: {lmtd:.2f}")
    st.write(f"Tube Outlet Temp: {T_outtube:.2f} °C")
    st.write(f"Shell Outlet Temp: {T_outshell:.2f} °C")
    st.write(f"Reynolds Number (Tube): {Re:.2f}")
    st.write(f"Reynolds Number (Shell): {Re_shell:.2f}")
