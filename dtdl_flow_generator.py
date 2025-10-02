"""
DTDL Flow Model Generator
Generate mock twin instances and data flows without Azure
Perfect for testing and visualization
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class DTDLModel:
    """Represents a parsed DTDL model"""
    
    def __init__(self, model_json: dict):
        self.raw = model_json
        self.id = model_json.get("@id", "")
        self.type = model_json.get("@type", "Interface")
        self.display_name = self._get_display_name()
        self.description = self._get_description()
        self.extends = model_json.get("extends", [])
        
        # Ensure extends is a list
        if isinstance(self.extends, str):
            self.extends = [self.extends]
        
        # Parse contents
        self.properties = []
        self.relationships = []
        self.telemetries = []
        self.commands = []
        
        contents = model_json.get("contents", [])
        for item in contents:
            item_type = item.get("@type")
            if item_type == "Property":
                self.properties.append(item)
            elif item_type == "Relationship":
                self.relationships.append(item)
            elif item_type == "Telemetry":
                self.telemetries.append(item)
            elif item_type == "Command":
                self.commands.append(item)
    
    def _get_display_name(self) -> str:
        """Extract display name, handling string or dict format"""
        display_name = self.raw.get("displayName", "")
        if isinstance(display_name, dict):
            return display_name.get("en", list(display_name.values())[0] if display_name else "")
        return display_name or self.id.split(":")[-1].split(";")[0]
    
    def _get_description(self) -> str:
        """Extract description, handling string or dict format"""
        description = self.raw.get("description", "")
        if isinstance(description, dict):
            return description.get("en", list(description.values())[0] if description else "")
        return description
    
    def get_short_id(self) -> str:
        """Get shortened ID for display"""
        return self.id.split(":")[-1].split(";")[0]


class DTDLParser:
    """Parse DTDL models and generate Mermaid diagrams"""
    
    def __init__(self):
        self.models: Dict[str, DTDLModel] = {}
    
    def load_file(self, filepath: str) -> None:
        """Load a single DTDL JSON file"""
        with open(filepath, 'r') as f:
            model_json = json.load(f)
            model = DTDLModel(model_json)
            self.models[model.id] = model
            print(f"[x] Loaded: {model.display_name} ({model.get_short_id()})")
    
    def load_directory(self, directory: str) -> None:
        """Load all JSON files from a directory"""
        dir_path = Path(directory)
        json_files = list(dir_path.glob("*.json"))
        
        print(f"[+] Loading {len(json_files)} models from {directory}")
        for json_file in json_files:
            try:
                self.load_file(json_file)
            except Exception as e:
                print(f"[!] Error loading {json_file}: {e}")
        
        print(f"[x] Total models loaded: {len(self.models)}")


class FlowModelGenerator:
    """Generate flow models and mock data from DTDL definitions"""
    
    def __init__(self, parser: DTDLParser):
        self.parser = parser
        self.twin_instances = {}
        self.relationships = []
        self.telemetry_data = {}
    
    def generate_twin_instance(self, twin_id: str, model_id: str, properties: dict = None) -> dict:
        """
        Create a mock twin instance from a model
        
        Args:
            twin_id: Unique ID for the twin
            model_id: DTDL model ID to instantiate
            properties: Optional property values
        
        Returns:
            Twin instance dictionary
        """
        if model_id not in self.parser.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.parser.models[model_id]
        
        twin = {
            "$dtId": twin_id,
            "$etag": f"W/\"{random.randint(1000, 9999)}\"",
            "$metadata": {
                "$model": model_id
            },
            "properties": properties or {}
        }
        
        # Initialize default property values
        for prop in model.properties:
            prop_name = prop.get("name")
            if prop_name not in twin["properties"]:
                twin["properties"][prop_name] = self._generate_default_value(prop.get("schema"))
        
        self.twin_instances[twin_id] = twin
        print(f"[x] Created twin: {twin_id} ({model.display_name})")
        
        return twin
    
    def create_relationship(self, source_id: str, relationship_name: str, target_id: str) -> dict:
        """
        Create a relationship between two twins
        
        Args:
            source_id: Source twin ID
            relationship_name: Name of relationship
            target_id: Target twin ID
        
        Returns:
            Relationship dictionary
        """
        relationship = {
            "$relationshipId": f"{source_id}-{relationship_name}-{target_id}",
            "$sourceId": source_id,
            "$targetId": target_id,
            "$relationshipName": relationship_name
        }
        
        self.relationships.append(relationship)
        print(f"[x] Created relationship: {source_id} --{relationship_name}--> {target_id}")
        
        return relationship
    
    def generate_telemetry(self, twin_id: str) -> dict:
        """
        Generate mock telemetry data for a twin
        
        Args:
            twin_id: Twin ID to generate telemetry for
        
        Returns:
            Telemetry data dictionary
        """
        if twin_id not in self.twin_instances:
            raise ValueError(f"Twin {twin_id} not found")
        
        twin = self.twin_instances[twin_id]
        model_id = twin["$metadata"]["$model"]
        model = self.parser.models[model_id]
        
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "twin_id": twin_id,
            "data": {}
        }
        
        # Generate mock values for each telemetry
        for tel in model.telemetries:
            tel_name = tel.get("name")
            tel_schema = tel.get("schema")
            telemetry["data"][tel_name] = self._generate_telemetry_value(tel_name, tel_schema)
        
        # Store for later retrieval
        if twin_id not in self.telemetry_data:
            self.telemetry_data[twin_id] = []
        self.telemetry_data[twin_id].append(telemetry)
        
        return telemetry
    
    def _generate_default_value(self, schema):
        """Generate default value based on schema type"""
        if schema == "string":
            return ""
        elif schema in ["double", "float"]:
            return 0.0
        elif schema in ["integer", "long"]:
            return 0
        elif schema == "boolean":
            return False
        elif isinstance(schema, dict) and schema.get("@type") == "Enum":
            enum_values = schema.get("enumValues", [])
            if enum_values:
                return enum_values[0].get("enumValue")
        return None
    
    def _generate_telemetry_value(self, name: str, schema: str):
        """Generate realistic mock telemetry values"""
        name_lower = name.lower()
        
        # Temperature
        if "temp" in name_lower:
            return round(random.uniform(20.0, 80.0), 1)
        # Current
        elif "current" in name_lower:
            return round(random.uniform(5.0, 20.0), 2)
        # Voltage
        elif "voltage" in name_lower or "volt" in name_lower:
            return round(random.uniform(220.0, 240.0), 1)
        # Pressure
        elif "pressure" in name_lower:
            return round(random.uniform(1.0, 5.0), 2)
        # Flow rate
        elif "flow" in name_lower:
            return round(random.uniform(10.0, 50.0), 2)
        # Level
        elif "level" in name_lower:
            return round(random.uniform(0.0, 100.0), 1)
        # Vibration
        elif "vibration" in name_lower or "vib" in name_lower:
            return round(random.uniform(0.1, 2.0), 2)
        # Generic double
        elif schema in ["double", "float"]:
            return round(random.uniform(0.0, 100.0), 2)
        # Generic integer
        elif schema in ["integer", "long"]:
            return random.randint(0, 100)
        else:
            return 0.0
    
    def export_flow_model(self, output_file: str = "flow_model.json"):
        """
        Export complete flow model with twins, relationships, and telemetry
        
        Args:
            output_file: Output JSON file path
        """
        flow_model = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_twins": len(self.twin_instances),
                "total_relationships": len(self.relationships),
                "models_used": list(self.parser.models.keys())
            },
            "twins": self.twin_instances,
            "relationships": self.relationships,
            "telemetry": self.telemetry_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(flow_model, f, indent=2)
        
        print(f"\n[x] Exported flow model to: {output_file}")
        print(f"    Twins: {len(self.twin_instances)}")
        print(f"    Relationships: {len(self.relationships)}")
        print(f"    Telemetry snapshots: {sum(len(v) for v in self.telemetry_data.values())}")
    
    
