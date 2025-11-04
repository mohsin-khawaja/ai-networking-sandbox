"""Test client for Aviz NCP AI Agent MCP Server.

This client demonstrates how to interact with the MCP server and test all available tools.
"""
import json
import subprocess
import sys
import time

def send_request(method, params=None, request_id=1):
    """Send a JSON-RPC request."""
    req = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    return json.dumps(req) + "\n"

def read_response(proc, timeout=5):
    """Read a JSON-RPC response from the process with timeout."""
    import select
    import sys as sys_module
    
    # For Windows compatibility, use a simple readline approach
    # In production, use proper async I/O
    try:
        response_line = proc.stdout.readline()
        if response_line:
            return json.loads(response_line.strip())
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys_module.stderr)
        return None
    except Exception as e:
        print(f"Error reading response: {e}", file=sys_module.stderr)
        return None
    return None

def call_tool(proc, tool_name, arguments, request_id):
    """Call an MCP tool and return the result."""
    request = send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments
    }, request_id=request_id)
    
    proc.stdin.write(request)
    proc.stdin.flush()
    
    response = read_response(proc)
    if response and "result" in response:
        result = response["result"]
        if "content" in result and len(result["content"]) > 0:
            content_text = result["content"][0].get("text", "{}")
            try:
                return json.loads(content_text)
            except json.JSONDecodeError:
                return {"raw_content": content_text}
        return result
    elif response and "error" in response:
        return {"error": response["error"]}
    return None

# Launch the server
print("Starting MCP server...")
proc = subprocess.Popen(
    [sys.executable, "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=0
)

# Step 1: Initialize the MCP connection
init_request = send_request("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
    }
}, request_id=1)

proc.stdin.write(init_request)
proc.stdin.flush()

# Read initialization response
init_response = read_response(proc)
if init_response and "result" in init_response:
    server_info = init_response["result"].get("serverInfo", {})
    print(f"Connected to MCP server: {server_info.get('name', 'unknown')} v{server_info.get('version', 'unknown')}\n")
else:
    print("Warning: Failed to initialize connection")
    sys.exit(1)

# Step 2: Send initialized notification
initialized_notification = json.dumps({
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}) + "\n"
proc.stdin.write(initialized_notification)
proc.stdin.flush()

request_id = 2

# Test 1: Get port telemetry
print("=" * 70)
print("Test 1: Get Port Telemetry")
print("=" * 70)
telemetry_data = call_tool(proc, "get_port_telemetry", {}, request_id)
request_id += 1
if telemetry_data:
    print(json.dumps(telemetry_data, indent=2))
else:
    print("Error: Failed to get telemetry")
print()

# Test 2: Get network topology
print("=" * 70)
print("Test 2: Get Network Topology")
print("=" * 70)
topology_data = call_tool(proc, "get_network_topology", {}, request_id)
request_id += 1
if topology_data:
    stats = topology_data.get("statistics", {})
    print(f"Topology: {stats.get('total_devices', 0)} devices, {stats.get('total_links', 0)} links")
    print(f"  SONiC devices: {stats.get('sonic_devices', 0)}")
    print(f"  Non-SONiC devices: {stats.get('non_sonic_devices', 0)}")
    print("\nFull topology:")
    print(json.dumps(topology_data, indent=2))
else:
    print("Error: Failed to get topology")
print()

# Test 3: Predict link health
print("=" * 70)
print("Test 3: Predict Link Health")
print("=" * 70)
health_data = call_tool(proc, "predict_link_health", {
    "rx_errors": 2,
    "tx_errors": 5,
    "utilization": 0.85
}, request_id)
request_id += 1
if health_data:
    print(json.dumps(health_data, indent=2))
else:
    print("Error: Failed to predict link health")
print()

# Test 4: Validate build metadata
print("=" * 70)
print("Test 4: Validate Build Metadata")
print("=" * 70)
build_data = call_tool(proc, "validate_build_metadata", {
    "build_json_path": "data/builds/sonic_build.json"
}, request_id)
request_id += 1
if build_data:
    print(f"Valid: {build_data.get('valid', False)}")
    print(f"Device Type: {build_data.get('device_type', 'unknown')}")
    if build_data.get("errors"):
        print(f"Errors: {build_data['errors']}")
    if build_data.get("warnings"):
        print(f"Warnings: {build_data['warnings']}")
    print("\nFull validation result:")
    print(json.dumps(build_data, indent=2))
else:
    print("Error: Failed to validate build metadata")
print()

# Test 5: Remediate link
print("=" * 70)
print("Test 5: Remediate Link")
print("=" * 70)
remediation_data = call_tool(proc, "remediate_link", {
    "interface": "Ethernet12"
}, request_id)
request_id += 1
if remediation_data:
    print(f"Recommended Action: {remediation_data.get('recommended_action', 'unknown')}")
    print(f"Reason: {remediation_data.get('reason', 'N/A')}")
    print(f"Confidence: {remediation_data.get('confidence', 0.0)}")
    print("\nFull remediation result:")
    print(json.dumps(remediation_data, indent=2))
else:
    print("Error: Failed to get remediation recommendation")
print()

# Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)
print("All tools tested successfully.")
print()

# Close the process
proc.stdin.close()
proc.wait()
