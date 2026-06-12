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

col1, col2, col3, col4 = st.columns(4)

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
        round(avg_rms,2)
    )

st.markdown("---")
col5, col6, col7, col8 = st.columns(4)

with col5:

    st.metric(
        "📊 Max RMS",
        round(max(
            AX.get("RMS",0),
            AY.get("RMS",0),
            BX.get("RMS",0),
            BY.get("RMS",0)
        ),2)
    )

with col6:

    st.metric(
        "🔍 Monitoring Points",
        "A-X | A-Y | B-X | B-Y"
    )

with col7:

    st.metric(
        "⏳ Estimated RUL",
        "120 h"
    )

with col8:

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

# ==========================================
# HEALTH INDEX
# ==========================================

avg_rms = (
    float(AX.get("RMS",0)) +
    float(AY.get("RMS",0)) +
    float(BX.get("RMS",0)) +
    float(BY.get("RMS",0))
) / 4

health_score = max(
    0,
    min(
        100,
        100 - avg_rms * 5
    )
)

st.subheader("🏥 Machine Health Index")

st.progress(int(health_score))

st.metric(
    "Global Health Score",
    f"{health_score:.1f}%"
)

if health_score >= 80:
    st.success("Machine in Good Condition")

elif health_score >= 50:
    st.warning("Machine Requires Monitoring")

else:
    st.error("Critical Condition - Maintenance Required")
    
    # ==========================================
# GLOBAL MACHINE STATUS
# ==========================================

fault_count = 0

for point in [AX, AY, BX, BY]:

    if point.get("Fault","Normal") != "Normal":
        fault_count += 1

if fault_count == 0:

    machine_status = "Healthy"
    status_color = "🟢"

elif fault_count <= 2:

    machine_status = "Warning"
    status_color = "🟡"

else:

    machine_status = "Critical"
    status_color = "🔴"

st.subheader("⚙ Global Machine Status")

st.info(
    f"{status_color} Current Status : {machine_status}"
)
if machine_status == "Critical":
    st.error("🚨 Critical Machine Condition")

elif machine_status == "Warning":
    st.warning("⚠️ Warning Condition")

else:
    st.success("✅ Healthy Machine")

# =====================================
# MONITORING POINTS OVERVIEW
# =====================================

st.subheader("🏭 Monitoring Points Overview")

colA,colB,colC,colD = st.columns(4)

with colA:
    st.metric(
        "A-X",
        AX.get("Fault","Unknown")
    )

with colB:
    st.metric(
        "A-Y",
        AY.get("Fault","Unknown")
    )

with colC:
    st.metric(
        "B-X",
        BX.get("Fault","Unknown")
    )

with colD:
    st.metric(
        "B-Y",
        BY.get("Fault","Unknown")
    )

st.markdown("---")
# ==================================================
# MAIN INFORMATION
# ==================================================

st.subheader("📋 Main Diagnostic Information")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("### 🔍 Fault")

    if fault == "Normal":
        st.success(fault)
    else:
        st.error(fault)

    st.markdown("### 📍 Fault Location")
    st.info(location)

with col2:

    st.markdown("### ⚠ Severity")
    st.warning(severity)

    st.markdown("### 🏥 Health Score")
    st.metric(
        "Health",
        f"{health_score:.1f}%"
    )

with col3:

    st.markdown("### ⏳ Remaining Useful Life")
    st.metric(
        "RUL",
        f"{rul} Days"
    )

    st.markdown("### 🔧 Recommendation")
    st.write(recommendation)

st.markdown("---")

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

# ==========================================
# HISTORY
# ==========================================

try:

    history = pd.read_csv("history.csv")

except:

    history = pd.DataFrame(columns=["Time","Fault"])

new_record = pd.DataFrame({
    "Time":[datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "MachineID":[machine_id],
    "Fault":[fault],
    "Severity":[severity],
    "HealthScore":[health_score]
})


history = pd.concat(
    [history,new_record],
    ignore_index=True
)

history.to_csv("history.csv",index=False)
total_faults = len(history)

st.metric(
    "Total Detections",
    total_faults
)

fault_history = history[
    history["Fault"] != "Normal"
]

if len(fault_history) > 0:
    last_fault = fault_history.iloc[-1]["Fault"]
else:
    last_fault = "No Fault Detected"

st.metric(
    "Last Fault",
    last_fault
)
st.dataframe(
    history.tail(20)
)

# ==================================
# HEALTH HISTORY
# ==================================

try:
    health_history = pd.read_csv(
        "health_history.csv"
    )

except:
    health_history = pd.DataFrame(
        columns=["Time","HealthScore"]
    )

new_health = pd.DataFrame({
    "Time":[datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "HealthScore":[health_score]
})

health_history = pd.concat(
    [health_history,new_health],
    ignore_index=True
)

health_history.to_csv(
    "health_history.csv",
    index=False
)

fault_count = history["Fault"].value_counts().reset_index()

fault_count.columns=["Fault","Occurrences"]

# ==========================================
# CHART
# ==========================================

st.subheader("Fault Distribution")

fig = px.pie(
    fault_count,
    names="Fault",
    values="Occurrences"
)

st.plotly_chart(fig,width="stretch")

# ==========================================
# RMS TREND PER POINT
# ==========================================

st.subheader("📈 RMS Trend Per Monitoring Point")

for key in ["AX","AY","BX","BY"]:
    if key not in st.session_state:
        st.session_state[key] = []

st.session_state["AX"].append(
    float(AX.get("RMS",0))
)

st.session_state["AY"].append(
    float(AY.get("RMS",0))
)

st.session_state["BX"].append(
    float(BX.get("RMS",0))
)

st.session_state["BY"].append(
    float(BY.get("RMS",0))
)

for key in ["AX","AY","BX","BY"]:
    if len(st.session_state[key]) > 50:
        st.session_state[key].pop(0)

trend_df = pd.DataFrame({
    "AX": st.session_state["AX"],
    "AY": st.session_state["AY"],
    "BX": st.session_state["BX"],
    "BY": st.session_state["BY"]
})

fig = px.line(
    trend_df,
    title="Monitoring Points RMS Evolution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# HEALTH TREND
# =====================================

st.subheader("📈 Monitoring Points Health")

trend_df = pd.DataFrame({
    "Point":["A-X","A-Y","B-X","B-Y"],
    "Health Score":[
        AX.get("HealthScore",0),
        AY.get("HealthScore",0),
        BX.get("HealthScore",0),
        BY.get("HealthScore",0)
    ]
})

fig3 = px.line(
    trend_df,
    x="Point",
    y="Health Score",
    markers=True,
    title="Health Index Distribution"
)

fig3.update_layout(
    yaxis_range=[0,100]
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ==========================================
# PDF REPORT
# ==========================================

st.subheader("📄 Generate Maintenance Report")

report_text = f"""
PREDICTIVE MAINTENANCE REPORT

Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

==================================

GLOBAL MACHINE STATUS

Health Score : {health_score} %
Priority     : {priority}
Severity     : {severity}
Fault        : {fault}
Location     : {location}
RUL          : {rul} Days

==================================

RECOMMENDATION

{recommendation}

==================================

MONITORING POINTS

AX :
Fault = {AX.get('Fault','Normal')}
RMS = {AX.get('RMS',0)}

AY :
Fault = {AY.get('Fault','Normal')}
RMS = {AY.get('RMS',0)}

BX :
Fault = {BX.get('Fault','Normal')}
RMS = {BX.get('RMS',0)}

BY :
Fault = {BY.get('Fault','Normal')}
RMS = {BY.get('RMS',0)}

==================================

Generated Automatically By
Predictive Maintenance Dashboard
"""
st.download_button(
    label="📥 Download Report",
    data=report_text,
    file_name=f"Maintenance_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    mime="text/plain"
)
