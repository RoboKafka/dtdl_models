# DTDL Digital Twin Visualization System

A comprehensive toolkit for creating, visualizing, and managing Digital Twins Definition Language (DTDL) models with interactive tree diagrams and flow visualizations.

## Table of Contents

- [Overview](#overview)
- [What is DTDL?](#what-is-dtdl)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Customization](#customization)
- [File Formats](#file-formats)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project provides tools to:
- **Define** digital twin models using DTDL (JSON-based schema)
- **Generate** mock twin instances with realistic telemetry data
- **Visualize** relationships using interactive CSS tree diagrams
- **Customize** layouts via JSON configuration files
- **Export** to HTML for presentations and documentation

### Key Features

- ✓ Black and white minimalist design
- ✓ Clickable nodes with detailed popups
- ✓ JSON-controlled tree structure
- ✓ Template-based HTML generation
- ✓ Support for industrial equipment (pumps, tanks, motors)
- ✓ Mock telemetry data generation
- ✓ No cloud/Azure account needed for local visualization

---

## What is DTDL?

**Digital Twins Definition Language (DTDL)** is a JSON-LD based language for defining digital twin models. It's used primarily with Azure Digital Twins but can be used standalone for modeling IoT systems.

### Core Concepts

#### 1. Interface
The main building block - defines what a digital twin "is"

```json
{
  "@context": "dtmi:dtdl:context;2",
  "@id": "dtmi:com:industrial:Motor;1",
  "@type": "Interface",
  "displayName": "Motor"
}
```

#### 2. Contents
What's inside the interface:

**Property** - Configuration/static data
```json
{
  "@type": "Property",
  "name": "serialNumber",
  "schema": "string",
  "writable": false
}
```

**Telemetry** - Streaming sensor data
```json
{
  "@type": "Telemetry",
  "name": "temperature",
  "schema": "double",
  "unit": "degreeCelsius"
}
```

**Command** - Actions that can be invoked
```json
{
  "@type": "Command",
  "name": "restart"
}
```

**Relationship** - Connections to other twins
```json
{
  "@type": "Relationship",
  "name": "feedsTo",
  "target": "dtmi:com:industrial:Tank;1"
}
```

#### 3. Inheritance
Models can extend other models:

```json
{
  "@id": "dtmi:com:industrial:Pump;1",
  "@type": "Interface",
  "extends": "dtmi:com:industrial:Motor;1"
}
```

Pump inherits all properties/telemetry from Motor.

---

## Project Structure

```
dt_test_onto/
│
├── templates/
│   └── tree_template.html          # HTML/CSS template for tree diagram
│
├── dtdl-models/
│   ├── Motor.json                  # Base motor model
│   ├── Pump.json                   # Pump model (extends Motor)
│   └── Tank.json                   # Tank storage model
│
├── output/                          # Generated files (created automatically)
│   ├── tree_diagram.html           # Interactive tree visualization
│   ├── industrial_flow_diagram.html
│   └── industrial_flow_model.json
│
├── create_dtdl_files.py            # Script: Create DTDL model files
├── dtdl_flow_generator.py          # Script: Generate flow models with mock data
├── dtdl_tree_generator.py          # Script: Generate tree diagrams from connections
├── connections.json                # Configuration: Define tree structure
└── README.md                        # This file
```

### File Descriptions

#### Python Scripts

**create_dtdl_files.py**
- Creates the three DTDL model files (Motor, Pump, Tank)
- Saves them to `dtdl-models/` directory
- Run this first if you don't have model files

**dtdl_flow_generator.py**
- Parses DTDL models
- Creates twin instances (virtual copies of equipment)
- Generates mock telemetry data
- Creates relationships between twins
- Exports flow diagrams and JSON data

**dtdl_tree_generator.py**
- Reads DTDL models and twin instances
- Builds hierarchical tree structure from connections
- Uses HTML template to generate visualization
- Creates clickable CSS tree diagram

#### Templates

**templates/tree_template.html**
- HTML/CSS template with placeholders
- Placeholders: `{{TREE_CONTENT}}`, `{{TWIN_DATA}}`, `{{MODEL_NAMES}}`
- Black and white minimalist design
- Includes modal popup for detailed views

#### Configuration

**connections.json**
- Defines which twins connect to which
- Simple source → target format
- Controls tree structure

Example:
```json
{
  "connections": [
    {"source": "pump-001", "target": "tank-001"},
    {"source": "pump-001", "target": "tank-002"},
    {"source": "pump-002", "target": "tank-003"}
  ]
}
```

#### Models

**dtdl-models/*.json**
- DTDL model definitions
- Define schemas for digital twins
- Specify properties, telemetry, relationships

---

## Installation

### Prerequisites

- Python 3.7 or higher
- No external Python packages required (uses standard library only)

### Setup

```bash
# 1. Create project directory
mkdir dt_test_onto
cd dt_test_onto

# 2. Create subdirectories
mkdir templates
mkdir dtdl-models
mkdir output

# 3. Copy all Python scripts to project root
# - create_dtdl_files.py
# - dtdl_flow_generator.py
# - dtdl_tree_generator.py

# 4. Copy tree_template.html to templates/
# Save the HTML template artifact as templates/tree_template.html

# 5. Verify structure
dir  # Windows
ls   # Linux/Mac
```

---

## Quick Start

### Option 1: Generate Everything from Scratch

```bash
# Step 1: Create DTDL model files
python create_dtdl_files.py

# Step 2: Generate tree diagram with default connections
python dtdl_tree_generator.py

# Step 3: Open the result
# Windows
start tree_diagram.html
# Mac
open tree_diagram.html
# Linux
xdg-open tree_diagram.html
```

### Option 2: Custom Configuration

```bash
# Step 1: Create models
python create_dtdl_files.py

# Step 2: Edit connections.json to define your structure
notepad connections.json  # Windows
nano connections.json     # Linux/Mac

# Step 3: Generate tree
python dtdl_tree_generator.py

# Step 4: View result
start tree_diagram.html
```

---

## Usage Guide

### Creating Your Own Models

#### 1. Define a New DTDL Model

Create `dtdl-models/Sensor.json`:

```json
{
  "@context": "dtmi:dtdl:context;2",
  "@id": "dtmi:com:industrial:Sensor;1",
  "@type": "Interface",
  "displayName": "Temperature Sensor",
  "contents": [
    {
      "@type": "Telemetry",
      "name": "temperature",
      "schema": "double",
      "unit": "degreeCelsius"
    },
    {
      "@type": "Property",
      "name": "location",
      "schema": "string"
    }
  ]
}
```

#### 2. Use It in Your Code

Edit `dtdl_tree_generator.py` function `create_tree_from_json()`:

```python
# Add to twin creation section
flow.generate_twin_instance(
    "sensor-001",
    "dtmi:com:industrial:Sensor;1",
    {"location": "Building A"}
)
```

#### 3. Define Connections

Edit `connections.json`:

```json
{
  "connections": [
    {"source": "sensor-001", "target": "tank-001"}
  ]
}
```

### Customizing the Tree Structure

The tree structure is controlled by `connections.json`. Each connection creates a parent-child relationship in the tree.

#### Example: 16 Pumps → 20 Tanks

Edit the `create_tree_from_json()` function in `dtdl_tree_generator.py`:

```python
# Create 16 pumps
for i in range(1, 17):
    flow.generate_twin_instance(
        f"pump-{i:03d}",
        "dtmi:com:industrial:Pump;1",
        {"ratedPower": 15.0 + i*5, "status": "running"}
    )

# Create 20 tanks
for i in range(1, 21):
    flow.generate_twin_instance(
        f"tank-{i:03d}",
        "dtmi:com:industrial:Tank;1",
        {"capacity": 5000.0 * i}
    )

# Define connections
connections_data = {
    "connections": [
        {"source": "pump-001", "target": "tank-001"},
        {"source": "pump-001", "target": "tank-002"},
        # ... add more connections
    ]
}
```

### Understanding the Output

#### tree_diagram.html

Interactive HTML page with:
- **Header**: Title and description
- **Tree Diagram**: Visual hierarchy of connections
- **Clickable Nodes**: Click any equipment to see details
- **Modal Popup**: Shows properties, telemetry, relationships

#### Node Visual Indicators

- **Solid border**: Running equipment
- **Dashed border**: Stopped equipment
- **Black lines**: Connection paths
- **Hover effect**: Gray background on hover

---

## Customization

### Modifying the Template

Edit `templates/tree_template.html` to customize:

#### Change Colors

```css
/* Find this in the <style> section */
.tree li a:hover {
    background: #f0f0f0;  /* Change hover color */
}

.pump-node.running {
    border-style: solid;
    border-width: 3px;  /* Make borders thicker */
}
```

#### Change Layout

```css
/* Adjust node spacing */
.tree li {
    padding: 30px 10px 0 10px;  /* Increase vertical spacing */
}

/* Change node size */
.tree li a {
    min-width: 200px;  /* Make nodes wider */
    padding: 20px 30px;  /* More internal padding */
}
```

#### Add Colors (If Desired)

```css
/* Add color to running pumps */
.pump-node.running {
    background: #e8f5e9 !important;  /* Light green */
    border-color: #4CAF50 !important;  /* Green border */
}

/* Add color to tanks */
.tank-node {
    background: #e3f2fd !important;  /* Light blue */
    border-color: #2196F3 !important;  /* Blue border */
}
```

### Creating Multiple Templates

Create variations for different use cases:

```bash
templates/
├── tree_template.html           # Default black and white
├── tree_template_color.html     # Colored version
├── tree_template_print.html     # Print-friendly version
└── tree_template_dark.html      # Dark mode version
```

Specify template when calling:

```python
tree.generate_tree_html(
    output_file="tree_diagram.html",
    template_file="templates/tree_template_dark.html"
)
```

---

## File Formats

### connections.json Format

```json
{
  "connections": [
    {
      "source": "equipment-id",
      "target": "connected-equipment-id"
    }
  ]
}
```

**Rules:**
- Source becomes parent in tree
- Target becomes child
- Same source can have multiple targets (multiple children)
- Equipment IDs must match twin instance IDs

### DTDL Model Format

```json
{
  "@context": "dtmi:dtdl:context;2",
  "@id": "dtmi:namespace:ModelName;version",
  "@type": "Interface",
  "displayName": "Human Readable Name",
  "description": "Description of the model",
  "contents": [
    {
      "@type": "Property|Telemetry|Command|Relationship",
      "name": "propertyName",
      "schema": "string|double|integer|boolean|...",
      "writable": true|false  // For properties
    }
  ]
}
```

### Twin Instance Format (Generated)

```json
{
  "$dtId": "pump-001",
  "$etag": "W/\"1234\"",
  "$metadata": {
    "$model": "dtmi:com:industrial:Pump;1"
  },
  "properties": {
    "ratedPower": 15.0,
    "status": "running"
  }
}
```

---

## Workflow Diagram

```
┌─────────────────────┐
│ Define DTDL Models  │
│ (Motor, Pump, Tank) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Run Python Scripts  │
│ Generate Twins      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Define Connections  │
│ (connections.json)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Generate Tree       │
│ (tree_diagram.html) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ View & Interact     │
│ (Open in Browser)   │
└─────────────────────┘
```

---

## Troubleshooting

### Common Issues

#### 1. No models loaded (Total models loaded: 0)

**Problem**: Python can't find DTDL model files

**Solution**:
```bash
# Check if files exist
dir dtdl-models\  # Windows
ls dtdl-models/   # Linux/Mac

# If empty, create them
python create_dtdl_files.py

# Verify they were created
dir dtdl-models\
```

#### 2. UnicodeEncodeError with emoji

**Problem**: Windows encoding issue with emoji characters

**Solution**: Already fixed in code with `encoding='utf-8'`. If still occurs:
- Remove emoji from template (🌳, 🛢, etc.)
- Or save template as UTF-8 with BOM

#### 3. Template file not found

**Problem**: `tree_template.html` not in correct location

**Solution**:
```bash
# Create templates directory
mkdir templates

# Move/copy template file
copy tree_template.html templates\  # Windows
cp tree_template.html templates/    # Linux/Mac

# Or update path in script
tree.generate_tree_html(
    template_file="./tree_template.html"  # If in root directory
)
```

#### 4. Empty tree diagram

**Problem**: No connections defined or twins not created

**Solution**:
```bash
# Check connections.json exists and has content
type connections.json  # Windows
cat connections.json   # Linux/Mac

# Verify twins were created by checking console output
# Should see: [x] Created twin: pump-001 (Pump)
```

#### 5. Node not clickable

**Problem**: JavaScript error or missing twin data

**Solution**:
- Open browser console (F12) to check for errors
- Verify twin ID matches exactly (case-sensitive)
- Check that telemetry was generated

---

## Advanced Usage

### Integrating with Real IoT Data

Replace mock telemetry generation with real data:

```python
# Instead of:
flow.generate_telemetry(twin_id)

# Use real data:
real_data = read_from_iot_hub(device_id)
flow.update_twin_properties(twin_id, {
    "temperature": real_data["temp"],
    "pressure": real_data["pressure"]
})
```

### Exporting for Presentations

The generated HTML is self-contained and can be:
- Opened offline (no internet needed)
- Embedded in other web pages
- Converted to PDF (print from browser)
- Shared via email or file sharing

### Version Control

Add `.gitignore`:

```
# Generated files
output/
tree_diagram.html
industrial_flow_diagram.html
industrial_flow_model.json
connections.json

# Keep templates and models
!templates/
!dtdl-models/
```

---

## Next Steps

### Learning Resources

- **Azure Digital Twins**: https://docs.microsoft.com/azure/digital-twins/
- **DTDL Specification**: https://github.com/Azure/opendigitaltwins-dtdl
- **DTDL v2 Reference**: https://docs.microsoft.com/azure/digital-twins/concepts-models

### Enhancements

Potential additions to this project:
- [ ] Time-series telemetry visualization
- [ ] Export to Azure Digital Twins
- [ ] Import from OPC UA servers
- [ ] Real-time data updates via WebSockets
- [ ] Graph database integration
- [ ] Multiple view types (grid, force-directed, etc.)
- [ ] Search and filter functionality
- [ ] Export to SVG/PNG for documentation

---

## License

This is a learning/demonstration project. Use and modify as needed for your purposes.

## Contributing

This is a standalone educational project. Feel free to fork and customize for your specific use cases.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify file structure matches documented layout
3. Review Python console output for error messages
4. Check browser console (F12) for JavaScript errors

---

**Last Updated**: 2025
**Version**: 1.0