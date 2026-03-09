"""Quick test script to verify the setup is working correctly."""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csv2fhir.transformer import CSVTransformer
from csv2fhir.validator import FHIRValidator


def test_patient_transformation():
    """Test transforming patient CSV."""
    print("\n" + "="*60)
    print("Testing Patient CSV Transformation")
    print("="*60)
    
    transformer = CSVTransformer()
    csv_path = "data/patients.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found")
        return False
    
    try:
        bundle = transformer.transform(csv_path, "Patient")
        print(f"✅ Successfully transformed CSV")
        print(f"   - Bundle ID: {bundle['id']}")
        print(f"   - Number of resources: {len(bundle['entry'])}")
        print(f"   - Resource types: {[e['resource']['resourceType'] for e in bundle['entry']]}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_observation_transformation():
    """Test transforming observation CSV."""
    print("\n" + "="*60)
    print("Testing Observation CSV Transformation")
    print("="*60)
    
    transformer = CSVTransformer()
    csv_path = "data/observations.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found")
        return False
    
    try:
        bundle = transformer.transform(csv_path, "Observation")
        print(f"✅ Successfully transformed CSV")
        print(f"   - Bundle ID: {bundle['id']}")
        print(f"   - Number of resources: {len(bundle['entry'])}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_condition_transformation():
    """Test transforming condition CSV."""
    print("\n" + "="*60)
    print("Testing Condition CSV Transformation")
    print("="*60)
    
    transformer = CSVTransformer()
    csv_path = "data/conditions.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found")
        return False
    
    try:
        bundle = transformer.transform(csv_path, "Condition")
        print(f"✅ Successfully transformed CSV")
        print(f"   - Bundle ID: {bundle['id']}")
        print(f"   - Number of resources: {len(bundle['entry'])}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_validation():
    """Test FHIR bundle validation."""
    print("\n" + "="*60)
    print("Testing FHIR Bundle Validation")
    print("="*60)
    
    transformer = CSVTransformer()
    validator = FHIRValidator()
    csv_path = "data/patients.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found")
        return False
    
    try:
        # Transform
        bundle = transformer.transform(csv_path, "Patient")
        
        # Validate
        result = validator.validate(bundle)
        
        print(f"✅ Validation completed")
        print(f"   - Valid: {result.valid}")
        print(f"   - Total resources: {result.stats['total_resources']}")
        print(f"   - Valid resources: {result.stats['valid_resources']}")
        print(f"   - Invalid resources: {result.stats['invalid_resources']}")
        print(f"   - Errors: {len(result.errors)}")
        print(f"   - Warnings: {len(result.warnings)}")
        
        if result.errors:
            print(f"\n   Errors:")
            for error in result.errors[:3]:  # Show first 3
                print(f"   - {error}")
        
        if result.warnings:
            print(f"\n   Warnings:")
            for warning in result.warnings[:3]:  # Show first 3
                print(f"   - {warning}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# csv2fhir Setup Verification Tests")
    print("#"*60)
    
    results = {
        "Patient Transformation": test_patient_transformation(),
        "Observation Transformation": test_observation_transformation(),
        "Condition Transformation": test_condition_transformation(),
        "FHIR Validation": test_validation(),
    }
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The setup is ready to use.")
        print("\nNext steps:")
        print("1. Run the server: python main.py")
        print("2. Open http://127.0.0.1:8000/docs in your browser")
        print("3. Test the API endpoints with sample CSV files")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
