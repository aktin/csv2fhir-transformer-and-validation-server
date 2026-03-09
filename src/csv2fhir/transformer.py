"""CSV to FHIR transformation module."""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from uuid import uuid4


class CSVTransformer:
    """Transforms CSV data into FHIR resources."""

    def __init__(self):
        """Initialize the CSV transformer."""
        self.bundle_id = str(uuid4())

    def transform_patient(self, row: pd.Series) -> Dict[str, Any]:
        """Transform a patient row to FHIR Patient resource.
        
        Args:
            row: Patient data row from CSV
            
        Returns:
            FHIR Patient resource
        """
        return {
            "resourceType": "Patient",
            "id": row.get("patient_id", ""),
            "identifier": [
                {
                    "system": "http://example.com/patient-id",
                    "value": row.get("patient_id", "")
                }
            ],
            "name": [
                {
                    "family": row.get("last_name", ""),
                    "given": [row.get("first_name", "")]
                }
            ],
            "gender": row.get("gender", "unknown").lower(),
            "birthDate": str(row.get("date_of_birth", "")),
            "telecom": [
                {
                    "system": "email",
                    "value": row.get("email", "")
                },
                {
                    "system": "phone",
                    "value": row.get("phone", "")
                }
            ] if row.get("email") or row.get("phone") else [],
            "address": [
                {
                    "text": row.get("address", "")
                }
            ] if row.get("address") else []
        }

    def transform_observation(self, row: pd.Series) -> Dict[str, Any]:
        """Transform an observation row to FHIR Observation resource.
        
        Args:
            row: Observation data row from CSV
            
        Returns:
            FHIR Observation resource
        """
        return {
            "resourceType": "Observation",
            "id": row.get("observation_id", ""),
            "identifier": [
                {
                    "system": "http://example.com/observation-id",
                    "value": row.get("observation_id", "")
                }
            ],
            "status": row.get("status", "final").lower(),
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": row.get("observation_type", ""),
                        "display": row.get("observation_type", "").replace("_", " ").title()
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{row.get('patient_id', '')}"
            },
            "effectiveDateTime": str(row.get("observation_date", "")),
            "valueQuantity": {
                "value": float(row.get("value", 0)),
                "unit": row.get("unit", "")
            } if row.get("value") else None,
            "issued": datetime.now().isoformat()
        }

    def transform_condition(self, row: pd.Series) -> Dict[str, Any]:
        """Transform a condition row to FHIR Condition resource.
        
        Args:
            row: Condition data row from CSV
            
        Returns:
            FHIR Condition resource
        """
        return {
            "resourceType": "Condition",
            "id": row.get("condition_id", ""),
            "identifier": [
                {
                    "system": "http://example.com/condition-id",
                    "value": row.get("condition_id", "")
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "code": row.get("condition_code", ""),
                        "display": row.get("condition_name", "")
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{row.get('patient_id', '')}"
            },
            "onsetDateTime": str(row.get("onset_date", "")),
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": row.get("status", "active").lower()
                    }
                ]
            }
        }

    def transform(self, csv_file_path: str, resource_type: str = "Patient") -> Dict[str, Any]:
        """Transform CSV data to FHIR resources.
        
        Args:
            csv_file_path: Path to CSV file
            resource_type: Type of FHIR resource (Patient, Observation, Condition)
            
        Returns:
            FHIR bundle with transformed resources
        """
        try:
            df = pd.read_csv(csv_file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")

        entries = []
        transformer_map = {
            "Patient": self.transform_patient,
            "Observation": self.transform_observation,
            "Condition": self.transform_condition
        }

        if resource_type not in transformer_map:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        transformer = transformer_map[resource_type]

        for _, row in df.iterrows():
            try:
                resource = transformer(row)
                entries.append({
                    "resource": resource,
                    "request": {
                        "method": "POST",
                        "url": resource_type
                    }
                })
            except Exception as e:
                raise ValueError(f"Failed to transform row: {str(e)}")

        bundle = {
            "resourceType": "Bundle",
            "id": self.bundle_id,
            "type": "transaction",
            "entry": entries,
            "timestamp": datetime.now().isoformat()
        }

        return bundle
