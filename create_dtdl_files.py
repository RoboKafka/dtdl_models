"""
Create DTDL model files in the dtdl-models directory
Run this first to create the model files
"""

import json
import os

# Create directory
os.makedirs('dtdl-models', exist_ok=True)

# Motor model
motor = {
  "@context": "dtmi:dtdl:context;2",
  "@id": "dtmi:com:industrial:Motor;1",
  "@type": "Interface",
  "displayName": "Motor",
  "description": "Industrial motor model",
  "contents": [
    {
      "@type": "Telemetry",
      "name": "current",
      "displayName": "Current",
      "schema": "double",
      "unit": "ampere"
    },
    {
      "@type": "Telemetry",
      "name": "vibration",
      "displayName": "Vibration",
      "schema": "double",
      "unit": "hertz"
    },
    {
      "@type": "Telemetry",
      "name": "temperature",
      "displayName": "Temperature",
      "schema": "double",
      "unit": "degreeCelsius"
    },
    {
      "@type": "Property",
      "name": "ratedPower",
      "displayName": "Rated Power",
      "schema": "double",
      "writable": False,
      "unit": "kilowatt"
    },
    {
      "@type": "Property",
      "name": "status",
      "displayName": "Operating Status",
      "schema": {
        "@type": "Enum",
        "valueSchema": "string",
        "enumValues": [
          {
            "name": "running",
            "enumValue": "running"
          },
          {
            "name": "stopped",
            "enumValue": "stopped"
          },
          {
            "name": "fault",
            "enumValue": "fault"
          }
        ]
      },
      "writable": True
    },
    {
      "@type": "Command",
      "name": "start",
      "displayName": "Start Motor"
    },
    {
      "@type": "Command",
      "name": "stop",
      "displayName": "Stop Motor"
    }
  ]
}

# Pump model
pump = {
  "@context": "dtmi:dtdl:context;2",
  "@id": "dtmi:com:industrial:Pump;1",
  "@type": "Interface",
  "displayName": "Pump",
  "description": "Industrial pump with motor",
  "extends": "dtmi:com:industrial:Motor;1",
  "contents": [
    {
      "@type": "Telemetry",
      "name": "flowRate",
      "displayName": "Flow Rate",
      "schema": "double",
      "unit": "litrePerSecond"
    },
    {
      "@type": "Telemetry",
      "name": "pressure",
      "displayName": "Discharge Pressure",
      "schema": "double",
      "unit": "bar"
    },
    {
      "@type": "Property",
      "name": "pumpType",
      "displayName": "Pump Type",
      "schema": "string",
      "writable": False
    },
    {
      "@type": "Relationship",
      "name": "feedsTo",
      "displayName": "Feeds To",
      "target": "dtmi:com:industrial:Tank;1"
    }
  ]
}

# Tank model
tank = {
  "@context": "dtmi:dtdl:context;2",
  "@id": "dtmi:com:industrial:Tank;1",
  "@type": "Interface",
  "displayName": "Tank",
  "description": "Storage tank model",
  "contents": [
    {
      "@type": "Telemetry",
      "name": "level",
      "displayName": "Level",
      "schema": "double",
      "unit": "percent"
    },
    {
      "@type": "Telemetry",
      "name": "temperature",
      "displayName": "Temperature",
      "schema": "double",
      "unit": "degreeCelsius"
    },
    {
      "@type": "Property",
      "name": "capacity",
      "displayName": "Capacity",
      "schema": "double",
      "writable": False,
      "unit": "litre"
    },
    {
      "@type": "Property",
      "name": "material",
      "displayName": "Tank Material",
      "schema": "string",
      "writable": False
    },
    {
      "@type": "Property",
      "name": "highLevelAlarm",
      "displayName": "High Level Alarm Setpoint",
      "schema": "double",
      "writable": True,
      "unit": "percent"
    },
    {
      "@type": "Property",
      "name": "lowLevelAlarm",
      "displayName": "Low Level Alarm Setpoint",
      "schema": "double",
      "writable": True,
      "unit": "percent"
    }
  ]
}

# Save files
with open('dtdl-models/Motor.json', 'w') as f:
    json.dump(motor, f, indent=2)
print("[x] Created dtdl-models/Motor.json")

with open('dtdl-models/Pump.json', 'w') as f:
    json.dump(pump, f, indent=2)
print("[x] Created dtdl-models/Pump.json")

with open('dtdl-models/Tank.json', 'w') as f:
    json.dump(tank, f, indent=2)
print("[x] Created dtdl-models/Tank.json")

print("\n[x] All model files created successfully!")
print("[x] You can now run: python dtdl_flow_generator.py")