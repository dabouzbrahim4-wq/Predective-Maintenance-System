import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import time
import plotly.graph_objects as go
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
import numpy as np
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_autorefresh import st_autorefresh
from firebase_config import root 

st_autorefresh(
    interval=5000,
    key="dashboard_refresh"
)
data = root.child("current_data").get()

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Overview",
        "Machine Dashboard",
        "Analytics",
        "Reports"
    ]
)
machine = st.selectbox(
    "Select Machine",
    [
        "Motor A",
        "Motor B",
        "Motor C"
    ]
)


# ==================================

# ==========================================
# AUTO REFRESH
# ==========================================

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    layout="wide"
)

# ==========================================
# FAULT DATABASE
# ==========================================

fault_info = {

    "Normal":{
        "severity":"Low",
        "location":"Healthy Machine",
        "recommendation":"No action required",
        "score":100,
        "rul":180
    },

    "Misalign_01":{
        "severity":"Medium",
        "location":"Coupling",
        "recommendation":"Check shaft alignment",
        "score":80,
        "rul":120
    },

    "Misalign_03":{
        "severity":"Medium",
        "location":"Coupling",
        "recommendation":"Realign shafts",
        "score":65,
        "rul":90
    },

    "Misalign_05":{
        "severity":"High",
        "location":"Coupling",
        "recommendation":"Immediate alignment required",
        "score":50,
        "rul":60
    },

    "BPFI_03":{
        "severity":"Medium",
        "location":"Inner Race Bearing",
        "recommendation":"Inspect bearing",
        "score":70,
        "rul":90
    },

    "BPFI_10":{
        "severity":"High",
        "location":"Inner Race Bearing",
        "recommendation":"Bearing replacement planned",
        "score":45,
        "rul":45
    },

    "BPFI_30":{
        "severity":"Critical",
        "location":"Inner Race Bearing",
        "recommendation":"Replace bearing immediately",
        "score":20,
        "rul":15
    },

    "BPFO_03":{
        "severity":"Medium",
        "location":"Outer Race Bearing",
        "recommendation":"Inspect bearing",
        "score":70,
        "rul":90
    },

    "BPFO_10":{
        "severity":"High",
        "location":"Outer Race Bearing",
        "recommendation":"Bearing replacement planned",
        "score":45,
        "rul":45
    },

    "BPFO_30":{
        "severity":"Critical",
        "location":"Outer Race Bearing",
        "recommendation":"Replace bearing immediately",
        "score":20,
        "rul":15
    },

    "Unbalance_0583mg":{
        "severity":"Low",
        "location":"Rotor",
        "recommendation":"Monitor vibration level",
        "score":90,
        "rul":150
    },

    "Unbalance_1169mg":{
        "severity":"Medium",
        "location":"Rotor",
        "recommendation":"Rotor balancing recommended",
        "score":75,
        "rul":120
    },

    "Unbalance_1751mg":{
        "severity":"Medium",
        "location":"Rotor",
        "recommendation":"Check balancing",
        "score":65,
        "rul":90
    },

    "Unbalance_2239mg":{
        "severity":"High",
        "location":"Rotor",
        "recommendation":"Balance rotor urgently",
        "score":45,
        "rul":45
    },

    "Unbalance_3318mg":{
        "severity":"Critical",
        "location":"Rotor",
        "recommendation":"Immediate balancing required",
        "score":20,
        "rul":15
    }

}


# ==========================================
# TITLE
# ==========================================

st.title("🔧 Predictive Maintenance Dashboard")
st.caption("AI-Based Predictive Maintenance System")

st.markdown("---")
machine_id = "MTR-001"
machine_name = "Industrial Motor"
st.info(
    f"""
    Machine ID : {machine_id}
    
    Equipment : {machine_name}
    
    
    """
)
data = root.child("current_data").get()
if not data:
    st.warning("Waiting for Firebase Data...")
    st.stop()

# ==========================================
# MONITORING POINTS
# ==========================================

st.markdown("## 🏭 Monitoring Points")

AX = data.get("x_direction_housing_A", {})
AY = data.get("y_direction_housing_A", {})
BX = data.get("x_direction_housing_B", {})
BY = data.get("y_direction_housing_B", {})
# البحث عن أول Fault موجود في نقاط القياس

fault = "Normal"

for point in [AX, AY, BX, BY]:

    current_fault = str(point.get("Fault", "Normal")).strip()
    current_condition = str(point.get("Condition", "Healthy")).strip()

    if current_fault != "Normal":
        fault = current_fault
        break

    if current_condition not in ["Healthy", "Normal"]:
        fault = current_condition
        break


# تحويل أسماء الأعطال القادمة من Firebase إلى أسماء موجودة في fault_info

if "BPFI" in fault:
    fault = "BPFI_10"

elif "BPFO" in fault:
    fault = "BPFO_10"

elif "Misalign" in fault:
    fault = "Misalign_03"

elif "Unbalance" in fault:
    fault = "Unbalance_1169mg"


if fault not in fault_info:
    fault = "Normal"


severity = fault_info[fault]["severity"]
location = fault_info[fault]["location"]
recommendation = fault_info[fault]["recommendation"]
health_score = fault_info[fault]["score"]
rul = fault_info[fault]["rul"]
if health_score >= 80:
    priority = "Low"

elif health_score >= 50:
    priority = "Medium"

else:
    priority = "High"
colA, colB = st.columns(2)

with colA:

    st.subheader("📍 Housing A")

    if AX:

        if AX["Fault"] == "Normal":
            st.success("🟢 A-X Healthy")
        else:
            st.error(f"🔴 A-X : {AX['Fault']}")

        st.write("RMS :", round(float(AX["RMS"]),2))
        st.write("Severity :", AX["Severity"])

    st.markdown("---")

    if AY:

        if AY["Fault"] == "Normal":
            st.success("🟢 A-Y Healthy")
        else:
            st.error(f"🔴 A-Y : {AY['Fault']}")

        st.write("RMS :", round(float(AY["RMS"]),2))
        st.write("Severity :", AY["Severity"])

with colB:

    st.subheader("📍 Housing B")

    if BX:

        if BX["Fault"] == "Normal":
            st.success("🟢 B-X Healthy")
        else:
            st.error(f"🔴 B-X : {BX['Fault']}")

        st.write("RMS :", round(float(BX["RMS"]),2))
        st.write("Severity :", BX["Severity"])

    st.markdown("---")

    if BY:

        if BY["Fault"] == "Normal":
            st.success("🟢 B-Y Healthy")
        else:
            st.error(f"🔴 B-Y : {BY['Fault']}")

        st.write("RMS :", round(float(BY["RMS"]),2))
        st.write("Severity :", BY["Severity"])
        # ==========================================
# FAULT LOCALIZATION
# ==========================================

st.markdown("## 🎯 Fault Localization")

for point_name, point in {

    "A-X": AX,
    "A-Y": AY,
    "B-X": BX,
    "B-Y": BY

}.items():

    if point and point["Fault"] != "Normal":

        st.error(
            f"""
            Point : {point_name}

            Fault : {point['Fault']}

            Location : {point['Condition']}

            Severity : {point['Severity']}
            """
        )
        # ==========================================
# MAINTENANCE ACTIONS
# ==========================================

st.markdown("## 🔧 Recommended Actions")

for point_name, point in {

    "A-X": AX,
    "A-Y": AY,
    "B-X": BX,
    "B-Y": BY

}.items():

    if point and point["Fault"] != "Normal":

        st.warning(
            f"""
            {point_name}

            Recommendation :

            Inspect machine immediately

            Verify lubrication

            Check bearing condition

            Schedule maintenance
            """
        )

# ==========================================
# KPI DASHBOARD
# ==========================================

st.markdown("## 📈 Key Performance Indicators")

avg_rms = (
    float(AX.get("RMS",0)) +
    float(AY.get("RMS",0)) +
    float(BX.get("RMS",0)) +
    float(BY.get("RMS",0))
) / 4
velocity_rms = avg_rms * 4.5
health_score = max(
    0,
    min(
        100,
        100 - avg_rms * 5
    )
)

critical_faults = sum([
    AX.get("Fault","Normal") != "Normal",
    AY.get("Fault","Normal") != "Normal",
    BX.get("Fault","Normal") != "Normal",
    BY.get("Fault","Normal") != "Normal"
])

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "🏥 Health Score",
        f"{health_score:.0f}%"
    )

with col2:
    st.metric(
        "📍 Active Points",
        "4"
    )

with col3:
    st.metric(
        "🚨 Faulty Points",
        critical_faults
    )

with col4:
    st.metric(
        "⚙ Average RMS",
        round(avg_rms, 2)
    )

with col5:
    st.metric(
        "⚡ Acceleration",
        f"{avg_rms:.2f} g"
    )

with col6:
    st.metric(
        "🚀 Velocity RMS",
        f"{velocity_rms:.2f} mm/s"
    )

st.markdown("---")

col7, col8, col9, col10 = st.columns(4)

with col7:
    st.metric(
        "📊 Max RMS",
        round(
            max(
                AX.get("RMS", 0),
                AY.get("RMS", 0),
                BX.get("RMS", 0),
                BY.get("RMS", 0)
            ),
            2
        )
    )

with col8:
    st.metric(
        "🔍 Monitoring Points",
        "A-X | A-Y | B-X | B-Y"
    )

with col9:
    st.metric(
        "⏳ Estimated RUL",
        "120 h"
    )

with col10:

    status = "Healthy"

    if critical_faults >= 2:
        status = "Critical"
    elif critical_faults == 1:
        status = "Warning"

    st.metric(
        "🚦 Machine Status",
        status
    )
st.markdown("---")


st.markdown("---")

col11, col12 = st.columns(2)

with col11:
    st.metric(
        "⏳ Remaining Useful Life",
        f"{rul} Days"
    )

with col12:

    st.markdown("### 🔧 Recommendation")

    if fault == "Normal":
        st.success(recommendation)
    else:
        st.warning(recommendation)
# ==========================================
# CURRENT FEATURES
# ==========================================

st.markdown("## 📊 Current Features")

features_df = pd.DataFrame({

    "Feature": [
        "RMS",
        "Kurtosis",
        "Skewness",
        "Crest Factor",
        "Peak Amplitude",
        "Peak Frequency (Hz)"
    ],

    "A-X": [
        round(float(AX.get("RMS",0)),2),
        round(float(AX.get("Kurtosis",0)),2),
        round(float(AX.get("Skewness",0)),2),
        round(float(AX.get("CrestFactor",0)),2),
        round(float(AX.get("PeakAmp",0)),2),
        round(float(AX.get("PeakFreq_Hz",0)),2)
    ],

    "A-Y": [
        round(float(AY.get("RMS",0)),2),
        round(float(AY.get("Kurtosis",0)),2),
        round(float(AY.get("Skewness",0)),2),
        round(float(AY.get("CrestFactor",0)),2),
        round(float(AY.get("PeakAmp",0)),2),
        round(float(AY.get("PeakFreq_Hz",0)),2)
    ],

    "B-X": [
        round(float(BX.get("RMS",0)),2),
        round(float(BX.get("Kurtosis",0)),2),
        round(float(BX.get("Skewness",0)),2),
        round(float(BX.get("CrestFactor",0)),2),
        round(float(BX.get("PeakAmp",0)),2),
        round(float(BX.get("PeakFreq_Hz",0)),2)
    ],

    "B-Y": [
        round(float(BY.get("RMS",0)),2),
        round(float(BY.get("Kurtosis",0)),2),
        round(float(BY.get("Skewness",0)),2),
        round(float(BY.get("CrestFactor",0)),2),
        round(float(BY.get("PeakAmp",0)),2),
        round(float(BY.get("PeakFreq_Hz",0)),2)
    ]

})

st.dataframe(
    features_df,
    use_container_width=True,
    hide_index=True
)

# ==================================
# HEALTH HISTORY VISUALIZATION
# ==================================

try:
    health_history = pd.read_csv(
        "health_history.csv"
    )

except:
    health_history = pd.DataFrame(
        columns=["Time", "HealthScore"]
    )

new_health = pd.DataFrame({
    "Time": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "HealthScore": [health_score]
})

health_history = pd.concat(
    [health_history, new_health],
    ignore_index=True
)

health_history.to_csv(
    "health_history.csv",
    index=False
)

st.subheader("📈 Machine Health Evolution")

history_plot = health_history.tail(50)

fig_health = px.line(
    history_plot,
    x="Time",
    y="HealthScore",
    markers=True,
    title="Machine Health Trend"
)

fig_health.update_layout(
    yaxis_range=[0, 100],
    height=500
)

fig_health.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="Healthy Zone"
)

fig_health.add_hline(
    y=50,
    line_dash="dash",
    annotation_text="Warning Zone"
)

st.plotly_chart(
    fig_health,
    use_container_width=True
)

# ==================================
# HEALTH KPIs
# ==================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🏥 Current Health",
        f"{health_score:.1f}%"
    )

with col2:

    best_health = health_history["HealthScore"].max()

    st.metric(
        "📈 Best Health",
        f"{best_health:.1f}%"
    )

with col3:

    worst_health = health_history["HealthScore"].min()

    st.metric(
        "📉 Lowest Health",
        f"{worst_health:.1f}%"
    )

st.markdown("---")

# ==================================
# RMS TREND PER POINT
# ==================================

st.subheader("📈 RMS Trend Per Monitoring Point")

for key in ["AX", "AY", "BX", "BY"]:
    if key not in st.session_state:
        st.session_state[key] = []

st.session_state["AX"].append(float(AX.get("RMS", 0)))
st.session_state["AY"].append(float(AY.get("RMS", 0)))
st.session_state["BX"].append(float(BX.get("RMS", 0)))
st.session_state["BY"].append(float(BY.get("RMS", 0)))

for key in ["AX", "AY", "BX", "BY"]:
    if len(st.session_state[key]) > 50:
        st.session_state[key].pop(0)

trend_df = pd.DataFrame({
    "AX": st.session_state["AX"],
    "AY": st.session_state["AY"],
    "BX": st.session_state["BX"],
    "BY": st.session_state["BY"]
})

fig_rms = px.line(
    trend_df,
    title="Monitoring Points RMS Evolution"
)

st.plotly_chart(
    fig_rms,
    use_container_width=True
)

# ==================================
# VIBRATION SIGNAL
# ==================================

st.subheader("📡 Vibration Signal")

signal = [
    float(AX.get("RMS", 0)),
    float(AY.get("RMS", 0)),
    float(BX.get("RMS", 0)),
    float(BY.get("RMS", 0))
]

fig_signal = go.Figure()

fig_signal.add_trace(
    go.Scatter(
        x=["A-X", "A-Y", "B-X", "B-Y"],
        y=signal,
        mode="lines+markers",
        name="Vibration"
    )
)

fig_signal.update_layout(
    title="Vibration Signal",
    xaxis_title="Monitoring Point",
    yaxis_title="Amplitude"
)

st.plotly_chart(
    fig_signal,
    use_container_width=True
)

# ==================================
# FFT SPECTRUM
# ==================================

st.subheader("📊 FFT Spectrum")

freq = [
    AX.get("PeakFreq_Hz", 0),
    AY.get("PeakFreq_Hz", 0),
    BX.get("PeakFreq_Hz", 0),
    BY.get("PeakFreq_Hz", 0)
]

amp = [
    AX.get("PeakAmp", 0),
    AY.get("PeakAmp", 0),
    BX.get("PeakAmp", 0),
    BY.get("PeakAmp", 0)
]

fig_fft = go.Figure()

fig_fft.add_trace(
    go.Bar(
        x=freq,
        y=amp,
        name="Amplitude"
    )
)

fig_fft.update_layout(
    title="Frequency Spectrum",
    xaxis_title="Frequency (Hz)",
    yaxis_title="Amplitude"
)

st.plotly_chart(
    fig_fft,
    use_container_width=True
)

# =====================================
# HEALTH TREND
# =====================================

st.subheader("📈 Monitoring Points Health")

health_df = pd.DataFrame({
    "Point": ["A-X", "A-Y", "B-X", "B-Y"],
    "Health Score": [
        AX.get("HealthScore", 0),
        AY.get("HealthScore", 0),
        BX.get("HealthScore", 0),
        BY.get("HealthScore", 0)
    ]
})

fig_health_points = px.line(
    health_df,
    x="Point",
    y="Health Score",
    markers=True,
    title="Health Index Distribution"
)

fig_health_points.update_layout(
    yaxis_range=[0, 100]
)

st.plotly_chart(
    fig_health_points,
    use_container_width=True
)
st.subheader("📄 Generate Maintenance Report")

report_text = f"""
==================================================
PREDICTIVE MAINTENANCE REPORT
==================================================

Date :
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Machine ID :
{machine_id}

Machine Name :
{machine_name}

==================================================
GLOBAL MACHINE STATUS
==================================================

Health Score : {health_score:.1f} %
Priority     : {priority}
Severity     : {severity}
Machine State: {status}

Detected Fault : {fault}
Fault Location : {location}

Remaining Useful Life (RUL) :
{rul} Days
==================================================
VIBRATION ANALYSIS
==================================================

Average RMS          : {avg_rms:.2f}
Acceleration RMS     : {avg_rms:.2f} g
Velocity RMS         : {velocity_rms:.2f} mm/s

Maximum RMS Value    :
{max(
    AX.get("RMS",0),
    AY.get("RMS",0),
    BX.get("RMS",0),
    BY.get("RMS",0)
):.2f}

==================================================
FFT SPECTRUM ANALYSIS
==================================================

A-X
Peak Frequency : {AX.get('PeakFreq_Hz',0)} Hz
Peak Amplitude : {AX.get('PeakAmp',0)}

A-Y
Peak Frequency : {AY.get('PeakFreq_Hz',0)} Hz
Peak Amplitude : {AY.get('PeakAmp',0)}

B-X
Peak Frequency : {BX.get('PeakFreq_Hz',0)} Hz
Peak Amplitude : {BX.get('PeakAmp',0)}

B-Y
Peak Frequency : {BY.get('PeakFreq_Hz',0)} Hz
Peak Amplitude : {BY.get('PeakAmp',0)}

==================================================
MONITORING POINTS DETAILS
==================================================

A-X

Fault      : {AX.get('Fault','Normal')}
Condition  : {AX.get('Condition','Healthy')}
Severity   : {AX.get('Severity','Low')}

RMS        : {AX.get('RMS',0)}
Kurtosis   : {AX.get('Kurtosis',0)}
Skewness   : {AX.get('Skewness',0)}
CrestFactor: {AX.get('CrestFactor',0)}

--------------------------------------------------

A-Y

Fault      : {AY.get('Fault','Normal')}
Condition  : {AY.get('Condition','Healthy')}
Severity   : {AY.get('Severity','Low')}

RMS        : {AY.get('RMS',0)}
Kurtosis   : {AY.get('Kurtosis',0)}
Skewness   : {AY.get('Skewness',0)}
CrestFactor: {AY.get('CrestFactor',0)}

--------------------------------------------------

B-X

Fault      : {BX.get('Fault','Normal')}
Condition  : {BX.get('Condition','Healthy')}
Severity   : {BX.get('Severity','Low')}

RMS        : {BX.get('RMS',0)}
Kurtosis   : {BX.get('Kurtosis',0)}
Skewness   : {BX.get('Skewness',0)}
CrestFactor: {BX.get('CrestFactor',0)}

--------------------------------------------------

B-Y

Fault      : {BY.get('Fault','Normal')}
Condition  : {BY.get('Condition','Healthy')}
Severity   : {BY.get('Severity','Low')}

RMS        : {BY.get('RMS',0)}
Kurtosis   : {BY.get('Kurtosis',0)}
Skewness   : {BY.get('Skewness',0)}
CrestFactor: {BY.get('CrestFactor',0)}

==================================================
MAINTENANCE RECOMMENDATION
==================================================

{recommendation}

==================================================
REPORT SUMMARY
==================================================

Total Monitoring Points : 4

Faulty Points :
{critical_faults}

Current Machine Status :
{status}

Health Assessment :
{health_score:.1f} %

Generated Automatically By

AI-Based Predictive Maintenance Dashboard

==================================================
"""
