"""FastAPI validation server for CSV uploads."""

import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from .transformer import CSVTransformer
from .validator import FHIRValidator

app = FastAPI(
    title="csv2fhir Validation Server",
    description="Validate CSV uploads for structural correctness and FHIR profile compliance",
    version="0.1.0"
)

transformer = CSVTransformer()
validator = FHIRValidator()


class TransformationRequest(BaseModel):
    """Request model for transformation."""
    resource_type: str = "Patient"


class ValidationResponse(BaseModel):
    """Response model for validation."""
    valid: bool
    errors: list
    warnings: list
    statistics: dict


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "csv2fhir validation server is running"}


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "csv2fhir Validation Server",
        "version": "0.1.0",
        "description": "CSV to HL7 FHIR transformation and validation pipeline",
        "endpoints": {
            "health": "/health",
            "transform": "/api/transform",
            "validate": "/api/validate"
        }
    }


@app.post("/api/transform")
async def transform_csv(
    file: UploadFile = File(...),
    resource_type: str = "Patient"
):
    """Transform CSV file to FHIR resources.
    
    Args:
        file: CSV file to transform
        resource_type: Type of FHIR resource (Patient, Observation, Condition)
        
    Returns:
        FHIR Bundle with transformed resources
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Transform CSV to FHIR
        try:
            bundle = transformer.transform(tmp_file_path, resource_type)
            
            # Validate the generated bundle
            validation_result = validator.validate(bundle)
            
            return {
                "success": True,
                "bundle": bundle,
                "validation": validation_result.to_dict()
            }
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transformation failed: {str(e)}")


@app.post("/api/validate")
async def validate_csv(
    file: UploadFile = File(...),
    resource_type: str = "Patient"
):
    """Validate CSV file for structural correctness.
    
    Args:
        file: CSV file to validate
        resource_type: Type of FHIR resource (Patient, Observation, Condition)
        
    Returns:
        Validation result with errors, warnings, and statistics
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Transform CSV to FHIR
            bundle = transformer.transform(tmp_file_path, resource_type)
            
            # Validate the generated bundle
            validation_result = validator.validate(bundle)
            
            return validation_result.to_dict()
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


@app.get("/api/resources/supported")
def get_supported_resources():
    """Get list of supported FHIR resource types."""
    return {
        "supported_resources": [
            {
                "type": "Patient",
                "description": "Information about an individual or animal receiving health care services"
            },
            {
                "type": "Observation",
                "description": "Measurements and simple assertions made about a patient"
            },
            {
                "type": "Condition",
                "description": "A clinical condition, problem, diagnosis, or other event statement"
            }
        ]
    }
