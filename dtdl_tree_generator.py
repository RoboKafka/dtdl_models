"""
DTDL Tree Diagram Generator
Creates CSS-based tree diagrams from JSON connection definitions
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from dtdl_flow_generator import DTDLParser, FlowModelGenerator
import time

class TreeNode:
    """Represents a node in the tree"""
    def __init__(self, id: str, data: dict = None):
        self.id = id
        self.data = data or {}
        self.children: List[TreeNode] = []
        self.parent = None
    
    def add_child(self, child):
        """Add a child node"""
        child.parent = self
        self.children.append(child)


class TreeGenerator:
    """Generate CSS tree diagrams from JSON connections"""
    
    def __init__(self, flow_model: FlowModelGenerator):
        self.flow_model = flow_model
        self.nodes: Dict[str, TreeNode] = {}
        self.roots: List[TreeNode] = []
    
    def build_from_connections(self, connections: List[dict]):
        """
        Build tree from connection definitions
        
        Args:
            connections: List of dicts like {"source": "pump-001", "target": "tank-001"}
        """
        # Create all nodes first
        all_ids = set()
        for conn in connections:
            all_ids.add(conn["source"])
            all_ids.add(conn["target"])
        
        for node_id in all_ids:
            twin_data = self.flow_model.twin_instances.get(node_id, {})
            self.nodes[node_id] = TreeNode(node_id, twin_data)
        
        # Build parent-child relationships
        children_ids = set()
        for conn in connections:
            source_id = conn["source"]
            target_id = conn["target"]
            
            if source_id in self.nodes and target_id in self.nodes:
                self.nodes[source_id].add_child(self.nodes[target_id])
                children_ids.add(target_id)
        
        # Find root nodes (nodes that are not children of anyone)
        self.roots = [node for node_id, node in self.nodes.items() if node_id not in children_ids]
        
        print(f"[x] Built tree with {len(self.nodes)} nodes and {len(self.roots)} root(s)")
    
    def build_from_json(self, json_file: str):
        """
        Build tree from JSON file
        
        JSON format:
        {
            "connections": [
                {"source": "pump-001", "target": "tank-001"},
                {"source": "pump-002", "target": "tank-002"}
            ]
        }
        """
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        connections = data.get("connections", [])
        self.build_from_connections(connections)
    
    def _render_node_html(self, node: TreeNode) -> str:
        """Render a single node and its children as HTML"""
        
        # Get node display info
        model_id = node.data.get("$metadata", {}).get("$model", "")
        model = self.flow_model.parser.models.get(model_id)
        model_name = model.display_name if model else "Unknown"
        
        # Get telemetry data
        telemetry = {}
        if node.id in self.flow_model.telemetry_data:
            telemetry = self.flow_model.telemetry_data[node.id][-1].get("data", {})
        
        properties = node.data.get("properties", {})
        status = properties.get("status", "")
        
        # Build tooltip content
        tooltip_items = []
        
        # Add key properties
        for key, value in properties.items():
            if key != "status":
                tooltip_items.append(f"{key}: {value}")
        
        # Add key telemetry
        tel_display = []
        for key, value in list(telemetry.items())[:3]:  # Show first 3
            unit = self._get_unit(key)
            tel_display.append(f"{key}: {value:.1f}{unit}")
        
        if tel_display:
            tooltip_items.extend(tel_display)
        
        tooltip = "\\A".join(tooltip_items) if tooltip_items else model_name
        
        # Determine node class
        node_class = "node"
        if "pump" in node.id.lower():
            node_class += " pump-node"
            if status == "running":
                node_class += " running"
            elif status == "stopped":
                node_class += " stopped"
        elif "tank" in node.id.lower():
            node_class += " tank-node"
        
        # Build HTML
        html = f'<li>\n'
        html += f'  <a href="#" class="{node_class}" data-id="{node.id}" data-tooltip="{tooltip}" onclick="showDetails(\'{node.id}\'); return false;">\n'
        html += f'    <span class="node-title">{node.id}</span>\n'
        html += f'    <span class="node-type">{model_name}</span>\n'
        
        # Add status indicator
        if status:
            status_icon = "▶" if status == "running" else "⏸" if status == "stopped" else "⚠"
            html += f'    <span class="status-indicator">{status_icon} {status}</span>\n'
        
        html += f'  </a>\n'
        
        # Render children
        if node.children:
            html += '  <ul>\n'
            for child in node.children:
                html += self._render_node_html(child)
            html += '  </ul>\n'
        
        html += '</li>\n'
        return html
    
    def _get_unit(self, key: str) -> str:
        """Get unit for telemetry key"""
        key_lower = key.lower()
        if "temp" in key_lower:
            return "°C"
        elif "current" in key_lower:
            return "A"
        elif "pressure" in key_lower:
            return "bar"
        elif "flow" in key_lower:
            return "L/s"
        elif "level" in key_lower:
            return "%"
        elif "vibration" in key_lower:
            return "Hz"
        return ""
    
    def generate_tree_html(self, output_file: str = "tree_diagram.html", template_file: str = "templates/tree_template.html"):
        """Generate CSS tree diagram HTML from template"""
        
        # Build tree content HTML
        tree_html = ""
        for root in self.roots:
            tree_html += self._render_node_html(root)
        
        # Prepare data for JavaScript
        twin_data = json.dumps({
            twin_id: {
                "id": twin_id,
                "model": twin["$metadata"]["$model"],
                "properties": twin["properties"],
                "telemetry": self.flow_model.telemetry_data.get(twin_id, [{}])[-1].get("data", {}) if twin_id in self.flow_model.telemetry_data else {},
                "relationships": [r for r in self.flow_model.relationships if r["$sourceId"] == twin_id]
            }
            for twin_id, twin in self.flow_model.twin_instances.items()
        }, indent=2)
        
        model_names = json.dumps({
            model_id: model.display_name 
            for model_id, model in self.flow_model.parser.models.items()
        })
        
        # Read template
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            print(f"[!] Template file not found: {template_file}")
            print("[!] Using embedded template instead")
            # Fallback to embedded minimal template
            template = self._get_fallback_template()
        
        # Replace placeholders
        html = template.replace("{{TREE_CONTENT}}", tree_html)
        html = html.replace("{{TWIN_DATA}}", twin_data)
        html = html.replace("{{MODEL_NAMES}}", model_names)
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[x] Generated tree diagram: {output_file}")
    
    def _get_fallback_template(self) -> str:
        """Minimal fallback template if file not found"""
        return """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>DTDL Tree</title></head>
<body>
<h1>DTDL Tree Diagram</h1>
<div>{{TREE_CONTENT}}</div>
<script>
const twinData = {{TWIN_DATA}};
const modelNames = {{MODEL_NAMES}};
function showDetails(id) { alert('Twin: ' + id); }
</script>
</body>
</html>"""



def create_tree_from_json():
    """Example: Create tree from JSON configuration"""
    
    print("=" * 60)
    print("DTDL Tree Generator - JSON Configuration")
    print("=" * 60)
    
    # Load DTDL models
    parser = DTDLParser()
    parser.load_directory("./dtdl-models")
    print(parser)
    time.sleep(5)
    # Create flow generator
    flow = FlowModelGenerator(parser)
    
    print("\n[1] Creating Twin Instances")
    print("-" * 60)
    
    # Create twins
    for i in range(1, 5):
        flow.generate_twin_instance(
            f"pump-{i:03d}",
            "dtmi:com:industrial:Pump;1",
            {"ratedPower": 15.0 + i*5, "status": "running" if i % 2 == 1 else "stopped", "pumpType": "Centrifugal"}
        )
    
    for i in range(1, 9):
        flow.generate_twin_instance(
            f"tank-{i:03d}",
            "dtmi:com:industrial:Tank;1",
            {"capacity": 5000.0 * i, "material": "Stainless Steel"}
        )
    
    # Create connections JSON
    connections_data = {
        "connections": [
            {"source": "pump-001", "target": "tank-001"},
            {"source": "pump-001", "target": "tank-002"},
            {"source": "pump-002", "target": "tank-003"},
            {"source": "pump-002", "target": "tank-004"},
            {"source": "pump-003", "target": "tank-005"},
            {"source": "pump-003", "target": "tank-006"},
            {"source": "pump-004", "target": "tank-007"},
            {"source": "pump-004", "target": "tank-008"},
        ]
    }
    
    # Save connections to JSON
    with open("connections.json", 'w') as f:
        json.dump(connections_data, f, indent=2)
    print("[x] Created connections.json")
    
    # Generate telemetry
    print("\n[2] Generating Telemetry")
    print("-" * 60)
    for twin_id in flow.twin_instances.keys():
        flow.generate_telemetry(twin_id)
    print(f"[x] Generated telemetry for {len(flow.twin_instances)} twins")
    
    # Build tree from relationships
    print("\n[3] Building Tree Structure")
    print("-" * 60)
    tree = TreeGenerator(flow)
    tree.build_from_connections(connections_data["connections"])
    
    # Generate tree diagram
    print("\n[4] Generating Tree Diagram")
    print("-" * 60)
    tree.generate_tree_html("tree_diagram.html")
    
    print("\n" + "=" * 60)
    print("Complete! Open tree_diagram.html to view")
    print("Edit connections.json to modify the tree structure")
    print("=" * 60)


if __name__ == "__main__":
    create_tree_from_json()