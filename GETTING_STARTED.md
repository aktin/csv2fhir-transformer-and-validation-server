## Getting Started with csv2fhir Validation Server

This guide will help you set up and run the csv2fhir transformation and validation server.

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- Git (optional)

### Installation Steps

#### 1. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -e ".[dev]"
```

#### 2. Verify Installation

Check that all dependencies are installed correctly:
```bash
python -c "import pandas; import fastapi; import pydantic; print('All dependencies installed!')"
```

### Running the Server

#### Option 1: Using the main.py script (Simple)

```bash
python main.py
```

The server will start at `http://127.0.0.1:8000`

#### Option 2: Using uvicorn directly (More control)

```bash
uvicorn src.csv2fhir.server:app --reload --host 127.0.0.1 --port 8000
```

#### Option 3: Using Python module

```bash
python -m uvicorn src.csv2fhir.server:app --reload --host 127.0.0.1 --port 8000
```

### Accessing the Server

Once the server is running:

1. **API Documentation (Interactive)**: 
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

2. **Health Check**:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

3. **Root Endpoint**:
   ```bash
   curl http://127.0.0.1:8000/
   ```

### API Endpoints

#### 1. Transform CSV to FHIR
**POST** `/api/transform`

Transforms a CSV file to FHIR resources.

**Parameters:**
- `file` (form-data): CSV file
- `resource_type` (query): Type of resource - `Patient`, `Observation`, or `Condition` (default: `Patient`)

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/transform?resource_type=Patient" \
  -H "accept: application/json" \
  -F "file=@data/patients.csv"
```

#### 2. Validate CSV
**POST** `/api/validate`

Validates a CSV file for structural correctness and FHIR compliance.

**Parameters:**
- `file` (form-data): CSV file
- `resource_type` (query): Type of resource - `Patient`, `Observation`, or `Condition` (default: `Patient`)

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/validate?resource_type=Patient" \
  -H "accept: application/json" \
  -F "file=@data/patients.csv"
```

#### 3. Get Supported Resources
**GET** `/api/resources/supported`

Returns list of supported FHIR resource types.

**Example:**
```bash
curl http://127.0.0.1:8000/api/resources/supported
```

### Sample Data

Sample CSV files are provided in the `data/` directory:

- **patients.csv**: Patient demographic information
- **observations.csv**: Medical observations (blood pressure, heart rate, etc.)
- **conditions.csv**: Patient medical conditions (diagnoses)

### Testing

#### Run Unit Tests

```bash
pytest tests/
```

#### Run Tests with Coverage

```bash
pytest tests/ --cov=src/csv2fhir --cov-report=html
```

#### Test Specific Module

```bash
pytest tests/test_transformer.py -v
pytest tests/test_validator.py -v
```

### Project Structure

```
csv2fhir-transformer-and-validation-server-dev/
├── src/
│   └── csv2fhir/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # FastAPI application
│       ├── transformer.py       # CSV to FHIR conversion logic
│       └── validator.py         # FHIR validation logic
├── tests/
│   ├── __init__.py
│   ├── test_transformer.py      # Transformer tests
│   └── test_validator.py        # Validator tests
├── data/
│   ├── patients.csv             # Sample patient data
│   ├── observations.csv         # Sample observation data
│   └── conditions.csv           # Sample condition data
├── main.py                      # Server entry point
├── pyproject.toml              # Project configuration
└── README.md                    # Project documentation
```

### Troubleshooting

#### Port Already in Use
If port 8000 is already in use, change it:
```bash
python -m uvicorn src.csv2fhir.server:app --host 127.0.0.1 --port 8001
```

#### Import Errors
If you get import errors, ensure the project is installed in editable mode:
```bash
pip install -e "."
```

#### Dependencies Not Found
Reinstall all dependencies:
```bash
pip install -r requirements.txt
```
Or with uv:
```bash
uv sync --reinstall
```

### Next Steps

1. **Review sample data** in the `data/` directory
2. **Test the API** using the Swagger UI at `/docs`
3. **Implement additional transformations** as needed
4. **Write custom tests** for your specific use cases
5. **Deploy** using Docker (Dockerfile to be added)

### Support

For issues or questions:
- Check the API documentation at `/docs`
- Review test cases in `tests/` directory
- Check FHIR specifications at http://hl7.org/fhir
