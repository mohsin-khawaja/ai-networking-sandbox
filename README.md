# Aviz Network Co-Pilot (NCP) AI Agent Framework

This repository contains a production-ready prototype of an **AI agent framework** built on the **Model Context Protocol (MCP)** for Aviz Networks' **Network Co-Pilot (NCP)** platform. This framework demonstrates how AI-driven agents can provide vendor-agnostic observability, validation, and automation for enterprise network infrastructure.

## Overview

**Aviz Networks** builds open, modular, and cloud-managed network solutions. The **Network Co-Pilot (NCP)** platform manages a diverse mix of network devices:

- **SONiC switches** (~5% of deployments)
- **Non-SONiC switches** (Cisco, Arista, EdgeCore, etc.)
- **Firewalls** (FortiGate, Palo Alto, etc.)
- **Other network elements** (routers, load balancers, etc.)

NCP is designed to be **vendor-agnostic**, providing unified observability, validation, and automation across all device types. This AI agent framework simulates the infrastructure-level AI capabilities that power NCP's intelligent operations.

## Architecture

The project follows a modular, production-ready architecture:

```
aviz_agents/
├── agents/                    # AI agent modules
│   ├── telemetry_agent.py      # Network telemetry collection
│   ├── ai_agent.py             # ML-based health prediction
│   ├── build_agent.py          # Build metadata validation
│   ├── remediation_agent.py   # Automated remediation
│   └── integration_tools.py    # Telnet and NetBox integration
├── data/                       # Data files
│   ├── builds/                 # Build JSON samples (SONiC, Cisco, EdgeCore)
│   └── netbox_sample.json      # Sample NetBox topology data
├── utils/                      # Shared utilities
│   ├── logger.py               # Centralized logging
│   ├── file_loader.py          # JSON file loading
│   └── topology_builder.py     # Network topology generation
├── mcp_server.py               # Main MCP orchestrator
├── client_test.py              # Test client
└── README.md
```

Each agent module is self-contained, testable, and designed for integration with real NCP workflows.

## Installation

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/mohsin-khawaja/ai-networking-sandbox.git
cd ai-networking-sandbox

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install "mcp[cli]" torch
```

## Available Tools

The MCP server exposes seven tools that demonstrate different aspects of NCP's AI infrastructure:

### 1. `get_port_telemetry()`

Simulates SONiC port telemetry metrics collection.

**Maps to NCP functionality:**
- Collects real-time interface statistics from SONiC switches
- Normalizes data for consumption by AI/ML models
- Supports integration with gNMI telemetry streams

**Returns:**
```json
{
  "switch": "sonic-leaf-01",
  "interface": "Ethernet12",
  "rx_bytes": 1234567,
  "tx_bytes": 2345678,
  "rx_errors": 2,
  "tx_errors": 5,
  "utilization": 0.85
}
```

**Usage:**
```python
result = await client.call_tool("get_port_telemetry", {})
```

### 2. `get_network_topology()`

Returns a mock network topology with multiple device types, demonstrating NCP's vendor-agnostic approach.

**Maps to NCP functionality:**
- Aggregates topology data from multiple vendor APIs
- Normalizes device and link information across vendors
- Provides unified view of network infrastructure
- Supports both SONiC (~5%) and non-SONiC devices (~95%)

**Returns:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "devices": [
    {
      "id": "sonic-leaf-01",
      "type": "SONiC",
      "vendor": "Dell",
      "model": "S5248F-ON",
      "role": "leaf",
      "status": "active",
      "interfaces": [...]
    },
    ...
  ],
  "links": [...],
  "statistics": {
    "total_devices": 5,
    "sonic_devices": 2,
    "non_sonic_devices": 3,
    "total_links": 4,
    "active_links": 4
  }
}
```

**Usage:**
```python
result = await client.call_tool("get_network_topology", {})
```

### 3. `predict_link_health(rx_errors, tx_errors, utilization)`

Runs an AI model to predict overall link health based on telemetry metrics. Uses a PyTorch neural network with GPU acceleration support.

**Maps to NCP functionality:**
- Analyzes real-time telemetry from network devices
- Uses ML model to predict link degradation before failures occur
- Provides actionable health scores for monitoring and alerting
- Integrates with remediation workflows for automated response

**Parameters:**
- `rx_errors` (int): Number of receive errors
- `tx_errors` (int): Number of transmit errors
- `utilization` (float): Link utilization (0.0 to 1.0)

**Returns:**
```json
{
  "health_score": 0.823,
  "status": "healthy",
  "inputs": {
    "rx_errors": 2,
    "tx_errors": 5,
    "utilization": 0.85
  }
}
```

**Usage:**
```python
result = await client.call_tool("predict_link_health", {
  "rx_errors": 2,
  "tx_errors": 5,
  "utilization": 0.85
})
```

**GPU Support:**
- Mac: Uses MPS (Metal Performance Shaders) when available
- Linux/Windows: Can be configured to use CUDA for NVIDIA GPUs
- Falls back to CPU if GPU is unavailable

### 4. `validate_build_metadata(build_json_path)`

Validates SONiC or non-SONiC build JSON files by checking for required fields and structure.

**Maps to NCP functionality:**
- Validates build metadata before deployment
- Ensures version, hardware, and feature consistency
- Prevents deployment of incompatible or misconfigured builds
- Supports vendor-agnostic build validation workflows

**Parameters:**
- `build_json_path` (str): Path to the build JSON file (can be relative to `data/builds/`)

**Returns:**
```json
{
  "valid": true,
  "device_type": "SONiC",
  "errors": [],
  "warnings": ["Recommended field missing: serial_number"],
  "metadata": {...}
}
```

**Usage:**
```python
result = await client.call_tool("validate_build_metadata", {
  "build_json_path": "data/builds/sonic_build.json"
})
```

### 5. `remediate_link(interface)`

Mock closed-loop automation tool that returns recommended remediation action based on interface health analysis.

**Maps to NCP functionality:**
- Analyzes link health from telemetry data
- Determines appropriate remediation action based on device type and issue
- Returns actionable recommendations for automation workflows
- Supports closed-loop automation for network operations

**Parameters:**
- `interface` (str): Interface name (e.g., "Ethernet12", "GigabitEthernet0/1")

**Returns:**
```json
{
  "interface": "Ethernet12",
  "recommended_action": "restart_port",
  "reason": "High error rate detected. Interface restart recommended.",
  "confidence": 0.85,
  "estimated_downtime_seconds": 5,
  "device_type": "SONiC",
  "timestamp": "2024-01-15T10:30:00Z",
  "next_steps": [
    "Review telemetry data",
    "Execute remediation if approved",
    "Monitor interface post-remediation"
  ]
}
```

**Usage:**
```python
result = await client.call_tool("remediate_link", {
  "interface": "Ethernet12"
})
```

### 6. `get_device_status_from_telnet(host, username, password, command)`

Establishes a Telnet session and runs a command on a network device. Connects to SONiC, EdgeCore, Celtica DS4000, NVIDIA SN2700, or other network devices via Telnet and executes CLI commands.

**Maps to NCP functionality:**
- Connects to network devices via Telnet for CLI access
- Executes device commands (show interfaces, show version, show environment)
- Normalizes output across different device vendors
- Supports SONiC, EdgeCore, Celtica DS4000, and NVIDIA SN2700 switches
- In production, integrates with device inventory for automated data collection

**Parameters:**
- `host` (str): Device hostname or IP address
- `username` (str): Telnet username
- `password` (str): Telnet password
- `command` (str): CLI command to execute (e.g., "show version", "show interfaces")

**Returns:**
```json
{
  "success": true,
  "host": "192.168.1.100",
  "command": "show version",
  "output": "SONiC Software Version: SONiC.202311.1...",
  "error": null
}
```

**Usage:**
```python
result = await client.call_tool("get_device_status_from_telnet", {
  "host": "192.168.1.100",
  "username": "admin",
  "password": "password",
  "command": "show version"
})
```

**Error Handling:**
- Connection timeouts are handled gracefully
- Authentication failures return clear error messages
- Invalid parameters are validated before connection attempts

### 7. `get_topology_from_netbox(base_url, token)`

Fetches network topology from NetBox (source of truth). Connects to NetBox's REST API to retrieve devices, interfaces, and links, building a graph representation of the network topology.

**Maps to NCP functionality:**
- Retrieves device inventory from NetBox (source of truth)
- Fetches interface and link information for topology mapping
- Builds unified network graph across all device types
- Supports SONiC, EdgeCore, Celtica DS4000, NVIDIA SN2700, and other devices
- In production, provides real-time topology updates for NCP operations

**Parameters:**
- `base_url` (str): NetBox base URL (e.g., "https://netbox.example.com")
- `token` (str): NetBox API token for authentication

**Returns:**
```json
{
  "success": true,
  "devices": [
    {
      "id": 1,
      "name": "sonic-leaf-01",
      "device_type": "S5248F-ON",
      "manufacturer": "Dell",
      "site": "Data Center A",
      "status": "active",
      "role": "leaf",
      "primary_ip": "192.168.1.100/24"
    }
  ],
  "links": [
    {
      "id": 1,
      "source_device": "sonic-leaf-01",
      "source_interface": "Ethernet12",
      "target_device": "sonic-spine-01",
      "target_interface": "Ethernet1/1",
      "status": "connected",
      "type": "cat6"
    }
  ],
  "statistics": {
    "total_devices": 25,
    "total_interfaces": 150,
    "total_links": 45
  },
  "error": null
}
```

**Usage:**
```python
result = await client.call_tool("get_topology_from_netbox", {
  "base_url": "https://netbox.example.com",
  "token": "your-api-token-here"
})
```

**Error Handling:**
- Authentication failures return clear error messages
- Connection errors are handled with timeout protection
- Invalid API responses are validated and reported
- **Sample Data Fallback**: If no API token is provided or token is invalid, the tool automatically falls back to sample NetBox data from `data/netbox_sample.json` for testing purposes

## Integration with Real Infrastructure

The framework now includes integration tools for connecting to real network devices and infrastructure sources:

### Telnet Integration

The Telnet integration tool enables direct CLI access to network devices. This is essential for Aviz NCP's operations as it allows:

- **Device Discovery**: Execute commands to discover device capabilities and versions
- **Health Checks**: Run diagnostic commands (show version, show environment) to verify device health
- **Configuration Retrieval**: Extract current device configurations for analysis
- **Vendor Agnostic**: Works with SONiC, EdgeCore, Celtica DS4000, NVIDIA SN2700, and other vendors

**Example Workflow:**
```python
# Check device version before deployment
version = await client.call_tool("get_device_status_from_telnet", {
  "host": "switch-01.example.com",
  "username": "admin",
  "password": "secure-password",
  "command": "show version"
})

if version["success"]:
    # Parse version information
    analyze_device_version(version["output"])
```

### NetBox Integration

NetBox serves as Aviz NCP's source of truth for network topology and device inventory. The NetBox integration tool enables:

- **Topology Discovery**: Automatically discover network topology from NetBox
- **Device Inventory**: Retrieve complete device inventory with all metadata
- **Link Mapping**: Understand physical and logical connections between devices
- **Real-time Updates**: Fetch current topology state for NCP operations
- **Sample Data Fallback**: For testing without NetBox access, automatically uses sample data from `data/netbox_sample.json`

**Example Workflow:**
```python
# Fetch topology from NetBox (production)
topology = await client.call_tool("get_topology_from_netbox", {
  "base_url": "https://netbox.production.example.com",
  "token": os.environ["NETBOX_API_TOKEN"]
})

# Or use sample data for testing (automatic fallback)
topology = await client.call_tool("get_topology_from_netbox", {
  "base_url": "https://netbox.example.com",
  "token": "your-api-token-here"  # Will automatically use sample data
})

if topology["success"]:
    # Use topology for NCP operations
    for device in topology["devices"]:
        if device["status"] == "active":
            monitor_device(device["name"])
```

## Running the Agent

### Start the MCP Server

```bash
python mcp_server.py
```

The server will initialize all agents, load the AI model, and wait for requests on stdio. Logs are written to stderr.

### Test with Client

```bash
python client_test.py
```

The test client demonstrates all seven tools:
1. Port telemetry collection
2. Network topology retrieval
3. Link health prediction
4. Build metadata validation
5. Link remediation recommendations
6. Device status via Telnet
7. Topology from NetBox

### Example Output

```
Starting MCP server...
Connected to MCP server: aviz-ncp-ai-agent v1.0.0

======================================================================
Test 1: Get Port Telemetry
======================================================================
{
  "switch": "sonic-leaf-01",
  "interface": "Ethernet12",
  "rx_bytes": 4567890,
  "tx_bytes": 5678901,
  "rx_errors": 3,
  "tx_errors": 7,
  "utilization": 0.72
}

======================================================================
Test 2: Get Network Topology
======================================================================
Topology: 5 devices, 4 links
  SONiC devices: 3
  Non-SONiC devices: 2

======================================================================
Test 3: Predict Link Health
======================================================================
{
  "health_score": 0.787,
  "status": "healthy",
  "inputs": {
    "rx_errors": 2,
    "tx_errors": 5,
    "utilization": 0.85
  }
}

======================================================================
Test 4: Validate Build Metadata
======================================================================
Valid: true
Device Type: SONiC

======================================================================
Test 5: Remediate Link
======================================================================
Recommended Action: restart_port
Reason: High error rate detected. Interface restart recommended.
Confidence: 0.85

======================================================================
Test 6: Get Device Status from Telnet
======================================================================
Note: This test uses mock credentials. In production, use real device credentials.
Success: Command executed on 192.168.1.100
Command: show version
Output length: 1234 characters

======================================================================
Test 7: Get Topology from NetBox
======================================================================
Note: This test requires NetBox URL and API token. Using example values.
Success: Topology fetched from NetBox
Devices: 25
Interfaces: 150
Links: 45
```

## Real-World Customer Workflows

This framework simulates real NCP customer workflows:

### SONiC Build Validation

Before deploying SONiC builds to production switches, NCP validates build metadata to ensure compatibility:

```python
# Validate SONiC build before deployment
validation = await client.call_tool("validate_build_metadata", {
  "build_json_path": "data/builds/sonic_build.json"
})

if validation["valid"]:
    # Proceed with deployment
    deploy_build()
else:
    # Block deployment and alert
    alert_ops_team(validation["errors"])
```

### Multi-Vendor Telemetry Monitoring

NCP collects telemetry from diverse device types and normalizes it for AI analysis:

```python
# Get unified topology view
topology = await client.call_tool("get_network_topology", {})

# Monitor all devices regardless of vendor
for device in topology["devices"]:
    if device["status"] != "active":
        alert_ops_team(f"Device {device['id']} is down")
```

### Automated Remediation

When AI detects link degradation, NCP can automatically recommend or execute remediation:

```python
# Predict health
health = await client.call_tool("predict_link_health", {
  "rx_errors": 10,
  "tx_errors": 15,
  "utilization": 0.95
})

if health["status"] == "warning":
    # Get remediation recommendation
    remediation = await client.call_tool("remediate_link", {
      "interface": "Ethernet12"
    })
    
    # Execute remediation via Ansible (in production)
    if remediation["confidence"] > 0.8:
        execute_remediation(remediation["recommended_action"])
```

## Project Structure Details

### Agents

Each agent module is self-contained and testable:

- **`agents/telemetry_agent.py`**: Handles network telemetry collection and topology generation
- **`agents/ai_agent.py`**: Contains the PyTorch model and health prediction logic with GPU support
- **`agents/build_agent.py`**: Validates build metadata for SONiC and non-SONiC devices
- **`agents/remediation_agent.py`**: Provides automated remediation recommendations
- **`agents/integration_tools.py`**: Integration tools for Telnet and NetBox connectivity

### Utilities

- **`utils/logger.py`**: Provides consistent logging configuration across all modules
- **`utils/file_loader.py`**: Handles JSON file loading with path resolution
- **`utils/topology_builder.py`**: Generates mock network topologies

### Data

- **`data/builds/`**: Sample build JSON files for SONiC, Cisco, and EdgeCore devices

## Error Handling

All tools include comprehensive error handling:

- **Input validation**: Parameters are validated before processing
- **Exception handling**: Try/except blocks prevent crashes
- **Structured errors**: Errors are returned as JSON with clear messages
- **Logging**: All errors are logged for debugging
- **Client safety**: Client never hangs waiting for responses

## Development

### Adding New Tools

1. Create or extend an agent module in `agents/`
2. Import the function in `mcp_server.py`
3. Register it with `@mcp.tool()` decorator
4. Add comprehensive docstring describing NCP functionality mapping
5. Update this README with tool documentation

### Logging

All modules use the centralized logger:

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Your log message")
```

### Testing Individual Agents

```python
from agents.telemetry_agent import get_network_topology
topology = get_network_topology()
print(topology["statistics"])
```

## Dependencies

Additional dependencies required for integration tools:

```bash
pip install requests
```

The `telnetlib` module is part of Python's standard library, so no additional installation is needed for Telnet support.

## Future Integration

This prototype is designed to evolve into production-ready components:

- **gNMI Integration**: Replace mock telemetry with real gNMI streams from network devices
- **Ansible Integration**: Execute remediation actions via Ansible playbooks
- **Multi-agent Orchestration**: Coordinate multiple specialized agents for complex workflows
- **Real-time Monitoring**: Stream telemetry data for continuous analysis
- **Production Models**: Replace mock models with trained ML models from production data
- **SSH Support**: Add SSH connectivity as an alternative to Telnet for secure device access
- **Enhanced NetBox Integration**: Support for NetBox webhooks and real-time topology updates

## GPU Configuration

The AI agent supports GPU acceleration:

- **Mac**: Uses MPS (Metal Performance Shaders) automatically
- **Linux/Windows with NVIDIA**: Modify `agents/ai_agent.py` to use CUDA:
  ```python
  device = "cuda" if torch.cuda.is_available() else "cpu"
  ```
- **CPU Fallback**: Automatically falls back to CPU if GPU is unavailable

## License

See repository for license information.

## Contributing

This is a prototype for Aviz Networks' NCP platform. For contributions, please follow the project's contribution guidelines.
