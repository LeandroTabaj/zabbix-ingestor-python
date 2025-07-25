#!/usr/bin/env python3
"""
Zabbix Telemetry Ingestor
A simple Flask application to receive Zabbix telemetry data via HTTP POST
and convert NDJSON format to standardized JSON structure.
"""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def parse_ndjson(ndjson_data: str) -> List[Dict[str, Any]]:
    """
    Parse NDJSON (Newline Delimited JSON) data into a list of dictionaries.
    
    Args:
        ndjson_data: String containing NDJSON data
        
    Returns:
        List of parsed JSON objects
    """
    records = []
    for line in ndjson_data.strip().split('\n'):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON line: {line}, error: {e}")
                raise
    return records


def transform_zabbix_data(zabbix_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform Zabbix NDJSON record to standardized JSON structure.
    
    Args:
        zabbix_record: Raw Zabbix data record
        
    Returns:
        Standardized JSON structure with specific format
    """
    # Extract host IP from the nested host structure
    host_ip = zabbix_record.get("host", {}).get("host", "")
    
    # Create timestamp from clock field
    timestamp = ""
    if zabbix_record.get("clock"):
        timestamp = datetime.fromtimestamp(zabbix_record.get("clock")).isoformat()
    
    # Map Zabbix metric name to appropriate field
    metric_name = zabbix_record.get("name", "").lower()
    metric_value = zabbix_record.get("value", 0)
    
    # Initialize standardized structure with default values
    standardized = {
        "timestamp": timestamp,
        "ip": host_ip,
        "ping": None,
        "latency": None,
        "packet_loss": None,
        "cpu_usage": None,
        "memory_usage": None,
        "signal_strength": None,
        "signal_quality": None,
        "throughput": None
    }
    
    # Map Zabbix metrics to standardized fields based on metric name
    if "icmp" in metric_name or "ping" in metric_name:
        if "response time" in metric_name or "latency" in metric_name:
            # Convert seconds to milliseconds if needed
            latency_ms = float(metric_value) * 1000 if float(metric_value) < 1 else float(metric_value)
            standardized["latency"] = int(latency_ms)
            standardized["ping"] = 1  # Successful ping if we have response time
        elif "loss" in metric_name:
            standardized["packet_loss"] = int(float(metric_value))
        else:
            standardized["ping"] = 1 if float(metric_value) > 0 else 0
    elif "cpu" in metric_name:
        standardized["cpu_usage"] = int(float(metric_value))
    elif "memory" in metric_name or "ram" in metric_name:
        standardized["memory_usage"] = int(float(metric_value))
    elif "signal" in metric_name:
        if "strength" in metric_name:
            standardized["signal_strength"] = int(float(metric_value))
        elif "quality" in metric_name:
            standardized["signal_quality"] = int(float(metric_value))
    elif "throughput" in metric_name or "bandwidth" in metric_name:
        standardized["throughput"] = int(float(metric_value))
    
    return standardized


@app.route('/ingest', methods=['POST'])
def ingest_telemetry():
    """
    Endpoint to receive Zabbix telemetry data via HTTP POST.
    Expects NDJSON format in request body.
    """
    try:
        # Get raw request data
        raw_data = request.get_data(as_text=True)
        
        if not raw_data:
            logger.warning("Received empty request body")
            return jsonify({"error": "Empty request body"}), 400
        
        logger.info(f"Received telemetry data: {len(raw_data)} characters")
        
        # Parse NDJSON
        records = parse_ndjson(raw_data)
        logger.info(f"Parsed {len(records)} records from NDJSON")
        
        # Transform each record
        standardized_records = []
        for record in records:
            try:
                standardized = transform_zabbix_data(record)
                standardized_records.append(standardized)
            except Exception as e:
                logger.error(f"Failed to transform record: {record}, error: {e}")
                return jsonify({"error": f"Failed to transform record: {str(e)}"}), 400
        
        logger.info(f"Successfully transformed {len(standardized_records)} records")
        
        # Return standardized data
        response = {
            "status": "success",
            "records_processed": len(standardized_records),
            "data": standardized_records
        }
        
        return jsonify(response), 200
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "zabbix-ingestor"}), 200


if __name__ == '__main__':
    logger.info("Starting Zabbix Telemetry Ingestor...")
    app.run(host='0.0.0.0', port=5000, debug=True)
