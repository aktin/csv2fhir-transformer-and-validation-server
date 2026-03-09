import pandas as pd
import json
from datetime import datetime
from fhir.resources.observation import Observation

# Mapping ICM names to MII-compliant LOINC codes 
BPS_LOINC_MAP = {
    "BPS - Gesichtsausdruck": "38214-3",
    "BPS - Obere Extremität": "38215-0",
    "BPS - Adaptation an Beatmungsgerät": "38216-8"
}

def map_bps_group_to_fhir(finding_key, group_df, patient_id):
    # Use the timestamp from the first record in the group
    raw_ts = str(group_df.iloc[0]['TIMESTAMP'])
    formatted_time = datetime.strptime(raw_ts, "%Y%m%d%H%M%S").isoformat()

    # Create the Parent Observation for BPS [cite: 41, 42]
    observation = Observation(
        status="final",
        category=[{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "clinical-test"}]}],
        code={
            "coding": [{"system": "http://loinc.org", "code": "38221-8", "display": "Behavioral Pain Scale total"}]
        },
        subject={"reference": f"Patient/{patient_id}"},
        effectiveDateTime=formatted_time,
        component=[]
    )

    total_score = 0
    for _, row in group_df.iterrows():
        treatment = row['T_TREATMENTNAME']
        if treatment in BPS_LOINC_MAP:
            val = float(row['VALUE'])
            total_score += val
            # Add sub-score as a component 
            observation.component.append({
                "code": {"coding": [{"system": "http://loinc.org", "code": BPS_LOINC_MAP[treatment]}]},
                "valueQuantity": {"value": val, "unit": "{score}", "system": "http://unitsofmeasure.org", "code": "{score}"}
            })

    # Set the total score value 
    observation.valueQuantity = {"value": total_score, "unit": "{score}", "system": "http://unitsofmeasure.org", "code": "{score}"}
    return observation

# --- Execution ---
# Load your exported CSV
df = pd.read_csv("bps_export.csv", sep=";")

# Group by FindingKey to keep the 3 sub-scores together 
grouped = df.groupby('FINDINGKEY')

for fk, group in grouped:
    fhir_res = map_bps_group_to_fhir(fk, group, patient_id="87994")
    print(json.dumps(json.loads(fhir_res.json()), indent=2))