import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(
    page_title="WMR Vapor Simulation Suite", 
    layout="wide", 
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# Custom minimal header styling
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1200px; }
    h1 { color: #5dade2; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ WMR Chemical Vapor Simulation Suite")
st.caption("Industrial Hygiene Modeling • Exponentially Decreasing Spill Evaporation Engine")
st.markdown("---")

# 2. Comprehensive Regulatory Limits Dictionary (PPM Values)
REGULATORY_LIMITS = {
    "10% Formalin": {"TWA": 0.75, "STEL": 2.0, "Action Level": 0.5},
    "Sevoflurane": {"TWA": 2.0, "STEL": 10.0, "Action Level": 1.0},
    "Desflurane": {"TWA": 2.0, "STEL": 10.0, "Action Level": 1.0},
    "Isoflurane": {"TWA": 2.0, "STEL": 10.0, "Action Level": 1.0},
    "Aniline": {"TWA": 5.0, "STEL": 15.0, "Action Level": 2.0},
    "Benzene": {"TWA": 1.0, "STEL": 5.0, "Action Level": 0.5},
    "Benzyl Chloride": {"TWA": 1.0, "STEL": 5.0, "Action Level": 0.5},
    "Butyl Alcohol": {"TWA": 20.0, "STEL": 50.0, "Action Level": 10.0},
    "Boron Trifluoride": {"TWA": 0.1, "STEL": 1.0, "Action Level": 0.05},
    "Bromine": {"TWA": 0.1, "STEL": 0.3, "Action Level": 0.05},
    "Bromoform": {"TWA": 0.5, "STEL": 2.0, "Action Level": 0.25},
    "Butyl Acetate": {"TWA": 50.0, "STEL": 150.0, "Action Level": 25.0},
    "Carbon Disulfide": {"TWA": 1.0, "STEL": 12.0, "Action Level": 0.5},
    "Carbon Tetrachloride": {"TWA": 2.0, "STEL": 10.0, "Action Level": 1.0},
    "Chlorobenzene": {"TWA": 10.0, "STEL": 40.0, "Action Level": 5.0},
    "Chloroform": {"TWA": 10.0, "STEL": 50.0, "Action Level": 5.0},
    "Chromyl Chloride": {"TWA": 0.001, "STEL": 0.005, "Action Level": 0.0005},
    "Cresol": {"TWA": 5.0, "STEL": 15.0, "Action Level": 2.5},
    "Cyclohexane": {"TWA": 100.0, "STEL": 300.0, "Action Level": 50.0},
    "Cyclohexanol": {"TWA": 50.0, "STEL": 100.0, "Action Level": 25.0},
    "Dichloroethylene": {"TWA": 200.0, "STEL": 250.0, "Action Level": 100.0},
    "Diethyl Ether": {"TWA": 400.0, "STEL": 500.0, "Action Level": 200.0},
    "Diisobutyl Ketone": {"TWA": 25.0, "STEL": 50.0, "Action Level": 12.5},
    "Dimethylhydrazine": {"TWA": 0.01, "STEL": 0.05, "Action Level": 0.005},
    "Dioxane": {"TWA": 20.0, "STEL": 60.0, "Action Level": 10.0},
    "EtO": {"TWA": 1.0, "STEL": 5.0, "Action Level": 0.5},
    "Ethanol": {"TWA": 1000.0, "STEL": 1200.0, "Action Level": 500.0},
    "Ethyl Bromide": {"TWA": 5.0, "STEL": 25.0, "Action Level": 2.5},
    "Ethyl Mercaptan": {"TWA": 0.5, "STEL": 2.0, "Action Level": 0.25},
    "Heptane": {"TWA": 85.0, "STEL": 440.0, "Action Level": 40.0},
    "Hexane": {"TWA": 50.0, "STEL": 150.0, "Action Level": 25.0},
    "Hydrazine": {"TWA": 0.01, "STEL": 0.03, "Action Level": 0.005},
    "Isopropyl Acetate": {"TWA": 100.0, "STEL": 150.0, "Action Level": 50.0},
    "Isopropyl Alcohol": {"TWA": 200.0, "STEL": 400.0, "Action Level": 100.0},
    "Isopropyl Ether": {"TWA": 250.0, "STEL": 310.0, "Action Level": 125.0},
    "MEK": {"TWA": 200.0, "STEL": 300.0, "Action Level": 100.0},
    "Methanol": {"TWA": 200.0, "STEL": 255.0, "Action Level": 100.0},
    "Methyl Acetate": {"TWA": 200.0, "STEL": 250.0, "Action Level": 100.0},
    "Methyl Cellosolve": {"TWA": 0.1, "STEL": 1.0, "Action Level": 0.05},
    "Methyl Chloroform": {"TWA": 350.0, "STEL": 450.0, "Action Level": 175.0},
    "Methyl Isocyanate": {"TWA": 0.02, "STEL": 0.06, "Action Level": 0.01},
    "Methylene chloride": {"TWA": 25.0, "STEL": 125.0, "Action Level": 12.5},
    "Morpholine": {"TWA": 20.0, "STEL": 30.0, "Action Level": 10.0},
    "Nitrobenzene": {"TWA": 1.0, "STEL": 3.0, "Action Level": 0.5},
    "Nitric Acid": {"TWA": 2.0, "STEL": 4.0, "Action Level": 1.0},
    "n-Pentane": {"TWA": 120.0, "STEL": 610.0, "Action Level": 60.0},
    "Octane": {"TWA": 75.0, "STEL": 385.0, "Action Level": 35.0},
    "Phenol": {"TWA": 5.0, "STEL": 15.0, "Action Level": 2.5},
    "Propyl Alcohol": {"TWA": 100.0, "STEL": 250.0, "Action Level": 50.0},
    "Pyridine": {"TWA": 1.0, "STEL": 5.0, "Action Level": 0.5},
    "Styrene": {"TWA": 20.0, "STEL": 40.0, "Action Level": 10.0},
    "Sulfur Pentafluoride": {"TWA": 0.01, "STEL": 0.03, "Action Level": 0.005},
    "Sulfuric Acid": {"TWA": 0.1, "STEL": 0.5, "Action Level": 0.05},
    "Tetrachloroethylene": {"TWA": 25.0, "STEL": 100.0, "Action Level": 12.5},
    "THF": {"TWA": 50.0, "STEL": 100.0, "Action Level": 25.0},
    "Toluene": {"TWA": 20.0, "STEL": 150.0, "Action Level": 10.0},
    "Trichloroethylene": {"TWA": 10.0, "STEL": 25.0, "Action Level": 5.0},
    "Xylene": {"TWA": 100.0, "STEL": 150.0, "Action Level": 50.0}
}

# 3. Load Chemical Data from 'Test App.xlsx'
@st.cache_data
def load_chemical_database():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "Test App.xlsx")
    df = pd.read_excel(file_path, sheet_name=0)
    sub_df = df.iloc[22:, [13, 14, 15, 16]].copy()
    sub_df.columns = ['Chemicals', 'Specific Gravity', 'Vapor Pressure', 'Molecular Weight']
    chem_df = sub_df.dropna(subset=['Chemicals']).copy()
    chem_df['Chemicals'] = chem_df['Chemicals'].astype(str).str.strip()
    chem_df['Specific Gravity'] = pd.to_numeric(chem_df['Specific Gravity'], errors='coerce')
    chem_df['Vapor Pressure'] = pd.to_numeric(chem_df['Vapor Pressure'], errors='coerce')
    chem_df['Molecular Weight'] = pd.to_numeric(chem_df['Molecular Weight'], errors='coerce')
    return chem_df.dropna()

chem_db = load_chemical_database()

# 4. Sidebar UI - Control Dashboard
st.sidebar.header("🕹️ Control Dashboard")

selected_chem = st.sidebar.selectbox("Target Agent / Substance", chem_db['Chemicals'].unique())
chem_info = chem_db[chem_db['Chemicals'] == selected_chem].iloc[0]

sg = float(chem_info['Specific Gravity'])
vp = float(chem_info['Vapor Pressure'])
mw = float(chem_info['Molecular Weight'])

with st.sidebar.expander("🏢 Room & Ventilation Profiles", expanded=True):
    room_volume_m3 = st.number_input("Room Volume (m³)", min_value=1.0, value=226.57, help="Total indoor space volume in cubic meters.")
    
    # --- MOVED: Manual Converter is now cleanly placed right beneath Room Volume ---
    st.markdown("<b style='font-size:13px; color:#a3e4d7;'>📐 Quick Conversion Tool</b>", unsafe_allow_html=True)
    calc_ft3 = st.number_input("Enter Volume in Cubic Feet (ft³):", min_value=0.0, value=8000.0, step=100.0, key="side_conv")
    calc_m3 = calc_ft3 / 35.31
    st.markdown(f"<small>Result: <code>{calc_m3:.2f}</code> m³ (Type this into Room Volume above if needed)</small>", unsafe_allow_html=True)
    st.markdown("---")
    
    exhaust_m3 = st.slider("Exhaust Ventilation (m³)", min_value=1.0, max_value=500.0, value=22.0, help="The active system extraction exhaust capacity.")
    air_velocity_fpm = st.slider("Room Air Velocity (fpm)", min_value=0, max_value=200, value=12, help="Ambient horizontal air velocity passing directly over spill surface.")

with st.sidebar.expander("🛢️ Spill Profile Details", expanded=True):
    spill_area_ft2 = st.slider("Spill Area (ft²)", min_value=0.1, max_value=100.0, value=1.0, step=0.5, help="Estimated layout boundaries of the liquid puddle.")
    liquid_volume_ml = st.number_input("Liquid Volume Spilled (mL)", min_value=1.0, value=120.0, help="Total volumetric amount of liquid material released.")

# 5. Regulatory Management Controls
chem_limits = REGULATORY_LIMITS.get(selected_chem, {"TWA": 10.0, "STEL": 25.0, "Action Level": 5.0})

with st.sidebar.expander("🚨 Safety Target Thresholds", expanded=False):
    use_custom = st.checkbox("Manual Target Overrides", value=False)
    if use_custom:
        action_limit = st.number_input("Custom Action Level (PPM)", value=chem_limits["Action Level"])
        twa_limit = st.number_input("Custom TWA Limit (PPM)", value=chem_limits["TWA"])
        stel_limit = st.number_input("Custom STEL Limit (PPM)", value=chem_limits["STEL"])
    else:
        action_limit = chem_limits["Action Level"]
        twa_limit = chem_limits["TWA"]
        stel_limit = chem_limits["STEL"]

# 6. Core Mathematical Engine (Verified Sync with Test App.xlsx)
spill_area_cm2 = spill_area_ft2 * 950.0  
ach = (exhaust_m3 / room_volume_m3) * 60

evap_rate_constant = 0.000524 * vp + 0.0108 * (spill_area_cm2 / liquid_volume_ml)
initial_mass = sg * liquid_volume_ml * 1000 
c_t_factor = (evap_rate_constant * initial_mass) / ((evap_rate_constant * room_volume_m3) - exhaust_m3)

# 7. Main Dashboard Area - Organized KPI Metric Layout
st.markdown("### 📋 Active Substance Characteristics")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Selected Substance", selected_chem)
kpi2.metric("Specific Gravity", f"{sg} g/cm³")
kpi3.metric("Vapor Pressure", f"{vp} mmHg")
kpi4.metric("Molecular Weight", f"{mw} g/mol")

st.markdown("### 🌀 Structural & Dynamic Outputs")
kpi5, kpi6, kpi7 = st.columns(3)
kpi5.metric("Air Exchange Rate (ACH)", f"{ach:.2f} / hr")
kpi6.metric("Evaporation Constant (ERC)", f"{evap_rate_constant:.5f}")
kpi7.metric("Initial Product Mass", f"{initial_mass:,.0f} mg")

st.markdown("---")

# 8. Run Simulation & Analytics Pipeline
time_steps = np.arange(0, 120, 1) 
mg_m3_list, ppm_list = [], []

for t in time_steps:
    if t == 0:
        mg_m3 = 0.0
    else:
        mg_m3 = c_t_factor * (np.exp((-exhaust_m3 / room_volume_m3) * t) - np.exp(-evap_rate_constant * t))
        mg_m3 = max(0.0, mg_m3)
    ppm = (mg_m3 * 24.45) / mw
    mg_m3_list.append(mg_m3)
    ppm_list.append(ppm)

sim_df = pd.DataFrame({"Time (mins)": time_steps, "mg/m³": mg_m3_list, "PPM": ppm_list})
max_ppm = sim_df["PPM"].max()
peak_time = sim_df.loc[sim_df["PPM"].idxmax(), "Time (mins)"]

# 9. Clear & Intuitive Alert Windows
st.markdown("### ⚠️ Industrial Hygiene Evaluation Summary")

if max_ppm >= stel_limit:
    st.error(
        f"🚨 **CRITICAL RISK DETECTED: SHORT-TERM EXPOSURE LIMIT BREACHED**\n\n"
        f"Concentration spikes to **{max_ppm:.2f} PPM** at minute **{peak_time}**, breaking past the permissible **{stel_limit} PPM** STEL ceiling. "
        f"Ensure immediate self-contained respirator deployment or evacuation."
    )
elif max_ppm >= twa_limit:
    st.warning(
        f"⚠️ **COMPLIANCE ALERT: TIME WEIGHTED AVERAGE THRESHOLD OUT of BOUNDS**\n\n"
        f"Vapor density peaks at **{max_ppm:.2f} PPM** at minute **{peak_time}**, passing the historical **{twa_limit} PPM** reference point. "
        f"Remediation or local emergency fan exhaust scaling required."
    )
elif max_ppm >= action_limit:
    st.info(
        f"ℹ️ **NOTICE: LEGAL ACTION LEVEL REACHED**\n\n"
        f"Vapor levels cross **{max_ppm:.2f} PPM**. This triggers standard employee administrative review and mandatory atmospheric health logging."
    )
else:
    st.success(
        f"✅ **ATMOSPHERIC EVALUATION COMPLIANT**\n\n"
        f"The peak exposure tracks safely at **{max_ppm:.2f} PPM** (minute {peak_time}), preserving structural stability below the standard risk target guidelines."
    )

st.markdown("---")

# 10. Visual Analytics Tab Matrix
tab1, tab2 = st.tabs(["📊 Interactive Modeling Graph", "📋 Minute-by-Minute Time Logs"])

with tab1:
    metric_choice = st.radio("Display Target Evaluation In:", ["PPM", "mg/m³"], horizontal=True)
    
    fig = px.line(
        sim_df, 
        x="Time (mins)", 
        y=metric_choice, 
        title=f"Gas Dispersion Decay Profile ({metric_choice})", 
        template="plotly_dark",
        labels={metric_choice: f"Concentration ({metric_choice})"}
    )
    
    if metric_choice == "PPM":
        fig.add_hline(y=stel_limit, line_dash="dot", line_color="#ef5350", annotation_text=f"STEL Target ({stel_limit} PPM)", annotation_position="top left")
        fig.add_hline(y=twa_limit, line_dash="dash", line_color="#ffb74d", annotation_text=f"TWA Ceiling ({twa_limit} PPM)", annotation_position="top left")
        fig.add_hline(y=action_limit, line_dash="dash", line_color="#4fc3f7", annotation_text=f"Action Target ({action_limit} PPM)", annotation_position="bottom left")
        
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Data Export Ledger")
    st.dataframe(
        sim_df.style.format({"mg/m³": "{:.3f}", "PPM": "{:.3f}"}), 
        use_container_width=True,
        height=350
    )