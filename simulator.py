import pandas as pd
import time

faults = [

    {
        "Fault": "Normal",
        "Location": "Machine Healthy",
        "Severity": "Low",
        "Recommendation": "No action required"
    },

    {
        "Fault": "Unbalance",
        "Location": "Rotor",
        "Severity": "Medium",
        "Recommendation": "Check rotor balancing"
    },

    {
        "Fault": "Misalignment",
        "Location": "Coupling",
        "Severity": "High",
        "Recommendation": "Perform shaft alignment"
    },

    {
        "Fault": "BPFI",
        "Location": "Inner Race Bearing",
        "Severity": "Critical",
        "Recommendation": "Replace bearing"
    },

    {
        "Fault": "BPFO",
        "Location": "Outer Race Bearing",
        "Severity": "Critical",
        "Recommendation": "Replace bearing immediately"
    }

]

while True:

    for fault in faults:

        df = pd.DataFrame([fault])

        df.to_csv(
            "fault_data.csv",
            index=False
        )

        print("Current Fault:", fault["Fault"])

        time.sleep(5)