# Zabbix Telemetry Ingestor

A simple Python Flask application to receive telemetry data from Zabbix via HTTP POST requests and convert NDJSON format to standardized JSON structure.

## Features

- Single HTTP endpoint (`/ingest`) to receive Zabbix telemetry data
- Parses NDJSON (Newline Delimited JSON) format
- Transforms data to standardized JSON structure
- Health check endpoint (`/health`)
- Comprehensive logging and error handling

## Setup

1. Activate your virtual environment:
   ```bash
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### POST /ingest
Receives Zabbix telemetry data in NDJSON format and returns standardized JSON.

**Request:**
- Method: POST
- Content-Type: application/json (or text/plain for NDJSON)
- Body: NDJSON format data

**Response:**
```json
{
  "status": "success",
  "records_processed": 1,
  "data": [
    {
      "timestamp": "2024-07-24T12:36:00",
      "source": "zabbix",
      "host": {
        "ip": "223.254.163.30",
        "name": "Test Host 20000"
      },
      "metric": {
        "id": 2000000000,
        "name": "ICMP response time",
        "value": 0.389,
        "type": 0
      },
      "groups": ["Example Group"],
      "tags": [{"tag": "env", "value": "test"}],
      "nanoseconds": 200001000
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "zabbix-ingestor"
}
```

## Example Usage

Test with curl:
```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{"host": {"host": "223.254.163.30", "name": "Test Host 20000"}, "groups": ["Example Group"], "item_tags": [{"tag": "env", "value": "test"}], "itemid": 2000000000, "name": "ICMP response time", "clock": 1721818560, "ns": 200001000, "value": 0.389, "type": 0}'
```

## Configuration

The current implementation includes a placeholder transformation function. You'll need to update the `transform_zabbix_data()` function in `app.py` with your specific standardized JSON structure requirements.
