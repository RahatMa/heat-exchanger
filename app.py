import streamlit as st
import math
import numpy as np

st.title("🔧 Heat Exchanger Calculator")

# --- CONSTANTS ---
density = 998
cp = 4182
U = 1600
Area = 0.1348

# --- USER INPUT ---
st.sidebar.header("Input Parameters")

m_dottube = st.sidebar.number_input("Tube Mass Flow Rate (kg/s)", value=0.1)
m_dotshell = st.sidebar.number_input("Shell Mass Flow Rate (kg/s)", value=0.1)

T_intube = st.sidebar.number_input("Tube Inlet Temp (°C)", value=90.0)
T_inshell = st.sidebar.number_input("Shell Inlet Temp (°C)", value=30.0)

# --- CALCULATION BUTTON ---
if st.button("Calculate"):

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
        return 2 * (denominator**-1)

    effectiveness = calculate_effectiveness(ntu, c)

    # --- Heat Transfer ---
    Q_max = C_min * (T_intube - T_inshell)
    Q = effectiveness * Q_max

    # --- Outlet Temps ---
    T_outtube = T_intube - Q / C_hot
    T_outshell = T_inshell + Q / C_cold

    # --- LMTD ---
    if (T_intube - T_outshell) != 0 and (T_outtube - T_inshell) != 0:
        lmtd = (T_intube - T_outshell - T_outtube + T_inshell) / math.log(
            (T_intube - T_outshell) / (T_outtube - T_inshell)
        )
    else:
        lmtd = T_intube - T_outtube

    # --- Correction Factor ---
    def calculate_correction_factor(T1, T2, t1, t2):
        try:
            R = (T1 - T2) / (t2 - t1)
            P = (t2 - t1) / (T1 - t1)
        except ZeroDivisionError:
            return None

        if abs(R - 1.0) < 1e-6:
            sqrt2 = np.sqrt(2)
            F = (sqrt2 * (P / (1 - P))) / (
                (1 - P) * np.log((2 - P * (2 - sqrt2)) / (2 - P * (2 + sqrt2)))
            )
        else:
            sqrt_R = np.sqrt(R**2 + 1)
            numerator = sqrt_R * np.log((1 - P) / (1 - R * P))
            denominator = (R - 1) * np.log(
                (2 - P * (R + 1 - sqrt_R)) / (2 - P * (R + 1 + sqrt_R))
            )
            F = numerator / denominator

        return F

    f_factor = calculate_correction_factor(T_inshell, T_outshell, T_intube, T_outtube)

    U2 = Q / (f_factor * Area * lmtd) if f_factor else None

    # --- OUTPUT ---
    st.subheader("Results")

    st.write(f"Effectiveness: {effectiveness:.4f}")
    st.write(f"NTU: {ntu:.2f}")
    st.write(f"Heat Transfer (Q): {Q:.2f} W")
    st.write(f"LMTD: {lmtd:.2f}")
    st.write(f"Tube Outlet Temp: {T_outtube:.2f} °C")
    st.write(f"Shell Outlet Temp: {T_outshell:.2f} °C")

    if f_factor:
        st.write(f"Correction Factor (F): {f_factor:.3f}")
        st.write(f"Overall U (calculated): {U2:.2f}")
    else:
        st.write("Correction Factor could not be calculated.")
