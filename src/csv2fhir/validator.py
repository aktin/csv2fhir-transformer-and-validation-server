"""FHIR resource validation module."""

from typing import Dict, Any, List, Tuple


class ValidationResult:
    """Result of FHIR resource validation."""

    def __init__(self):
        """Initialize validation result."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.valid = True
        self.stats = {
            "total_resources": 0,
            "valid_resources": 0,
            "invalid_resources": 0
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self.stats
        }


class FHIRValidator:
    """Validates FHIR resources and profile compliance."""

    def __init__(self):
        """Initialize the FHIR validator."""
        self.required_fields = {
            "Patient": ["resourceType", "id", "name"],
            "Observation": ["resourceType", "id", "status", "code", "subject"],
            "Condition": ["resourceType", "id", "code", "subject"]
        }

    def validate_resource(self, resource: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate a single FHIR resource.
        
        Args:
            resource: FHIR resource to validate
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check resource type
        resource_type = resource.get("resourceType")
        if not resource_type:
            errors.append("Missing 'resourceType' field")
            return False, errors, warnings

        # Check required fields
        if resource_type in self.required_fields:
            for field in self.required_fields[resource_type]:
                if field == "resourceType":
                    continue
                if field not in resource or not resource[field]:
                    errors.append(f"Missing required field '{field}' for {resource_type}")

        # Resource-specific validation
        if resource_type == "Patient":
            errors.extend(self._validate_patient(resource))
            warnings.extend(self._warn_patient(resource))
        elif resource_type == "Observation":
            errors.extend(self._validate_observation(resource))
            warnings.extend(self._warn_observation(resource))
        elif resource_type == "Condition":
            errors.extend(self._validate_condition(resource))
            warnings.extend(self._warn_condition(resource))

        return len(errors) == 0, errors, warnings

    def _validate_patient(self, resource: Dict[str, Any]) -> List[str]:
        """Patient-specific validation."""
        errors = []
        
        # Validate gender if present
        if "gender" in resource:
            valid_genders = ["male", "female", "other", "unknown"]
            if resource["gender"] not in valid_genders:
                errors.append(f"Invalid gender value: {resource['gender']}")

        # Validate birth date format
        if "birthDate" in resource:
            try:
                from datetime import datetime
                datetime.strptime(str(resource["birthDate"]), "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid birthDate format, expected YYYY-MM-DD")

        return errors

    def _validate_observation(self, resource: Dict[str, Any]) -> List[str]:
        """Observation-specific validation."""
        errors = []
        
        # Validate status
        if "status" in resource:
            valid_statuses = ["registered", "preliminary", "final", "amended", "cancelled", "entered-in-error", "unknown"]
            if resource["status"] not in valid_statuses:
                errors.append(f"Invalid observation status: {resource['status']}")

        # Validate value if present
        if "valueQuantity" in resource and resource["valueQuantity"]:
            if "value" in resource["valueQuantity"]:
                try:
                    float(resource["valueQuantity"]["value"])
                except (ValueError, TypeError):
                    errors.append("Invalid numeric value in valueQuantity")

        return errors

    def _validate_condition(self, resource: Dict[str, Any]) -> List[str]:
        """Condition-specific validation."""
        errors = []
        
        # Validate clinical status if present
        if "clinicalStatus" in resource:
            valid_statuses = ["active", "recurrence", "relapse", "inactive", "remission", "resolved", "unknown"]
            if "coding" in resource["clinicalStatus"]:
                for coding in resource["clinicalStatus"]["coding"]:
                    if coding.get("code") not in valid_statuses:
                        errors.append(f"Invalid clinical status: {coding.get('code')}")

        return errors

    def _warn_patient(self, resource: Dict[str, Any]) -> List[str]:
        """Patient-specific warnings."""
        warnings = []
        
        if "name" not in resource or not resource["name"]:
            warnings.append("Patient resource has no name")
        
        if "telecom" not in resource or not resource["telecom"]:
            warnings.append("Patient resource has no contact information")

        return warnings

    def _warn_observation(self, resource: Dict[str, Any]) -> List[str]:
        """Observation-specific warnings."""
        warnings = []
        
        if "valueQuantity" not in resource or not resource.get("valueQuantity"):
            warnings.append("Observation has no quantitative value")

        return warnings

    def _warn_condition(self, resource: Dict[str, Any]) -> List[str]:
        """Condition-specific warnings."""
        warnings = []
        
        if "onsetDateTime" not in resource:
            warnings.append("Condition resource missing onset date information")

        return warnings

    def validate(self, fhir_bundle: Dict[str, Any]) -> ValidationResult:
        """Validate a FHIR bundle.
        
        Args:
            fhir_bundle: FHIR bundle to validate
            
        Returns:
            ValidationResult with errors, warnings, and statistics
        """
        result = ValidationResult()

        # Validate bundle structure
        if fhir_bundle.get("resourceType") != "Bundle":
            result.errors.append("Root resource must be a Bundle")
            result.valid = False
            return result

        entries = fhir_bundle.get("entry", [])
        result.stats["total_resources"] = len(entries)

        for idx, entry in enumerate(entries):
            if "resource" not in entry:
                result.errors.append(f"Entry {idx} missing 'resource' field")
                result.stats["invalid_resources"] += 1
                continue

            resource = entry["resource"]
            is_valid, errors, warnings = self.validate_resource(resource)

            for error in errors:
                result.errors.append(f"Resource {idx} ({resource.get('resourceType', 'Unknown')}): {error}")
                result.valid = False

            for warning in warnings:
                result.warnings.append(f"Resource {idx} ({resource.get('resourceType', 'Unknown')}): {warning}")

            if is_valid:
                result.stats["valid_resources"] += 1
            else:
                result.stats["invalid_resources"] += 1

        return result
