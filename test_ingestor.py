#!/usr/bin/env python3
"""
Test script for the Zabbix Telemetry Ingestor
"""

import json
import requests
import time

# Test data - the example NDJSON you provided
test_data = '{"host": {"host": "223.254.163.30", "name": "Test Host 20000"}, "groups": ["Example Group"], "item_tags": [{"tag": "env", "value": "test"}], "itemid": 2000000000, "name": "ICMP response time", "clock": 1721818560, "ns": 200001000, "value": 0.389, "type": 0}'
test_data += '\n{"host": {"host": "223.254.163.30", "name": "Test Host 20000"}, "groups": ["Example Group"], "item_tags": [{"tag": "env", "value": "test"}], "itemid": 2000000001, "name": "CPU Load", "clock": 1721818560, "ns": 200002000, "value": 1.5, "type": 0}'
test_data += '\n{"host": {"host": "223.254.163.30", "name": "Test Host 20000"}, "groups": ["Example Group"], "item_tags": [{"tag": "env", "value": "test"}], "itemid": 2000000002, "name": "Memory utilization", "clock": 1721818560, "ns": 200003000, "value": 83.5, "type": 0}'
test_data += '\n{"host": {"host": "223.254.163.30", "name": "Test Host 20000"}, "groups": ["Example Group"], "item_tags": [{"tag": "env", "value": "test"}], "itemid": 2000000003, "name": "ICMP loss", "clock": 1721818560, "ns": 200004000, "value": 7.68, "type": 0}'
test_data += '\n{"host": {"host": "223.254.163.30", "name": "Test Host 20000"}, "groups": ["Example Group"], "item_tags": [{"tag": "env", "value": "test"}], "itemid": 2000000004, "name": "Uptime (hardware)", "clock": 1721818560, "ns": 200005000, "value": 5370662, "type": 0}'

def test_local_transformation():
    """Test the transformation function locally without HTTP"""
    from app import transform_zabbix_data, parse_ndjson
    
    print("Testing local transformation...")
    print(f"Input NDJSON: {test_data}")
    
    # Parse the NDJSON
    records = parse_ndjson(test_data)
    print(f"\nParsed {len(records)} records")
    
    # Transform each record
    for i, record in enumerate(records):
        print(f"\nOriginal record {i+1}:")
        print(json.dumps(record, indent=2))
        
        transformed = transform_zabbix_data(record)
        print(f"\nTransformed record {i+1}:")
        print(json.dumps(transformed, indent=2))

def test_http_endpoint():
    """Test the HTTP endpoint"""
    url = "http://localhost:5000/ingest"
    
    print("\nTesting HTTP endpoint...")
    print(f"Sending POST request to: {url}")
    print(f"Data: {test_data}")
    
    try:
        response = requests.post(
            url,
            data=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_health_endpoint():
    """Test the health check endpoint"""
    url = "http://localhost:5000/health"
    
    print("\nTesting health endpoint...")
    try:
        response = requests.get(url)
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test local transformation first
    test_local_transformation()
    
    # Wait a moment
    print("\n" + "="*50)
    
    # Test HTTP endpoints
    test_health_endpoint()
    test_http_endpoint()
