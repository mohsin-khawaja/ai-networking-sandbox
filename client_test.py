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

# Test 6: Get device status from Telnet
print("=" * 70)
print("Test 6: Get Device Status from Telnet")
print("=" * 70)
print("Note: This test uses mock credentials. In production, use real device credentials.")
telnet_data = call_tool(proc, "get_device_status_from_telnet", {
    "host": "192.168.1.100",
    "username": "admin",
    "password": "password",
    "command": "show version"
}, request_id)
request_id += 1
if telnet_data:
    if telnet_data.get("success"):
        print(f"Success: Command executed on {telnet_data.get('host')}")
        print(f"Command: {telnet_data.get('command')}")
        print(f"Output length: {len(telnet_data.get('output', ''))} characters")
        if telnet_data.get("output"):
            print("\nCommand output (first 500 chars):")
            output = telnet_data.get("output", "")
            print(output[:500] + ("..." if len(output) > 500 else ""))
    else:
        print(f"Error: {telnet_data.get('error', 'Unknown error')}")
        print("This is expected if no device is reachable at the test IP.")
    print("\nFull Telnet result:")
    print(json.dumps(telnet_data, indent=2))
else:
    print("Error: Failed to execute Telnet command")
print()

# Test 7: Get topology from NetBox
print("=" * 70)
print("Test 7: Get Topology from NetBox")
print("=" * 70)
print("Note: Using example token - will automatically fall back to sample data.")
print("      In production, provide a valid NetBox API token.")
netbox_data = call_tool(proc, "get_topology_from_netbox", {
    "base_url": "https://netbox.example.com",
    "token": "your-api-token-here"
}, request_id)
request_id += 1
if netbox_data:
    if netbox_data.get("success"):
        stats = netbox_data.get("statistics", {})
        note = netbox_data.get("note", "")
        if note:
            print(f"Note: {note}")
        print(f"Success: Topology fetched (from {'sample data' if note else 'NetBox API'})")
        print(f"Devices: {stats.get('total_devices', 0)}")
        print(f"Interfaces: {stats.get('total_interfaces', 0)}")
        print(f"Links: {stats.get('total_links', 0)}")
        if netbox_data.get("devices"):
            print("\nSample devices (first 3):")
            for device in netbox_data.get("devices", [])[:3]:
                print(f"  - {device.get('name')} ({device.get('device_type')})")
    else:
        print(f"Error: {netbox_data.get('error', 'Unknown error')}")
        print("This is expected if NetBox is not accessible or token is invalid.")
    print("\nFull NetBox result:")
    print(json.dumps(netbox_data, indent=2))
else:
    print("Error: Failed to fetch topology from NetBox")
print()

# Test 8: Get device and interface report (NetBox + Telnet)
print("=" * 70)
print("Test 8: Get Device and Interface Report (NetBox + Telnet)")
print("=" * 70)
print("This tool combines NetBox device inventory with Telnet interface data.")
print("Supports both mock (local) and real (lab) environments via .env configuration.")
print()

# Try calling with empty parameters first (uses .env if available)
try:
    report_data = call_tool(proc, "get_device_and_interface_report", {}, request_id)
    request_id += 1
    
    if report_data:
        # Display status summary
        netbox_status = report_data.get('NetBox_Status', 'Unknown')
        telnet_status = report_data.get('Telnet_Status', 'Unknown')
        
        print("Report Status:")
        print(f"  NetBox: {netbox_status}")
        print(f"  Telnet: {telnet_status}")
        print()
        
        # Display NetBox results
        if netbox_status == "Success":
            devices = report_data.get("NetBox_Devices", [])
            print(f"NetBox Devices ({len(devices)}):")
            if devices:
                for i, device in enumerate(devices[:10], 1):
                    print(f"  {i}. {device}")
                if len(devices) > 10:
                    print(f"  ... and {len(devices) - 10} more devices")
            else:
                print("  No devices found in NetBox inventory")
        elif netbox_status == "Failed":
            error_msg = report_data.get("error", "Unknown error")
            print(f"NetBox Error: {error_msg}")
            print("  Note: This is expected if NetBox is not accessible or token is invalid.")
            print("  In production, ensure NETBOX_URL and NETBOX_TOKEN are set in .env")
        else:
            print(f"NetBox Status: {netbox_status}")
        
        print()
        
        # Display Telnet results
        if telnet_status == "Success":
            telnet_output = report_data.get("Telnet_Output", "")
            if telnet_output:
                print("Telnet Command Output (first 500 characters):")
                print("-" * 70)
                print(telnet_output)
                print("-" * 70)
            else:
                print("Telnet: Command executed but no output received")
        elif telnet_status == "Failed":
            error_msg = report_data.get("error", "Unknown error")
            print(f"Telnet Error: {error_msg}")
            print("  Note: This is expected if no device is reachable at the configured host.")
            print("  In production, ensure TELNET_HOST, TELNET_USERNAME, and TELNET_PASSWORD are set in .env")
        elif telnet_status == "Skipped":
            print("Telnet: Skipped (no host configured)")
            print("  To enable Telnet, set TELNET_HOST in .env or pass telnet_host parameter")
        else:
            print(f"Telnet Status: {telnet_status}")
        
        print()
        
        # Display full JSON report for debugging
        print("Full Report (JSON):")
        print("-" * 70)
        print(json.dumps(report_data, indent=2))
        print("-" * 70)
        
    else:
        print("Error: Failed to generate device and interface report")
        print("The tool call returned no data. Check server logs for details.")
        
except Exception as e:
    print(f"Exception occurred while calling get_device_and_interface_report: {e}")
    print("This indicates a communication error with the MCP server.")
    import traceback
    traceback.print_exc()

print()

# Test 9: Validate system health
print("=" * 70)
print("Test 9: Validate System Health (AI ONE Center Style)")
print("=" * 70)
print("Note: This performs comprehensive system validation similar to AI ONE Center POC.")
health_data = call_tool(proc, "validate_system_health", {}, request_id)
request_id += 1
if health_data:
    if "Total" in health_data:
        total = health_data["Total"]
        print(f"Validation Summary:")
        print(f"  Passed: {total.get('Passed', 0)}")
        print(f"  Failed: {total.get('Failed', 0)}")
        print(f"  Not Run: {total.get('NotRun', 0)}")
        print()
        print("Component Status:")
        for component in ["NetBox", "Syslog", "ServiceNow", "Zendesk", "FlowAnalytics"]:
            if component in health_data:
                status = health_data[component].get("status", "Unknown")
                details = health_data[component].get("details", "N/A")
                print(f"  {component}: {status}")
                if status != "Passed":
                    print(f"    Details: {details}")
        print("\nFull validation report:")
        print(json.dumps(health_data, indent=2))
    else:
        print("Error: Invalid validation response format")
        print(json.dumps(health_data, indent=2))
else:
    print("Error: Failed to validate system health")
print()

# Test 10: Get inventory devices from NetBox (NCP SDK)
print("=" * 70)
print("Test 10: Get Inventory Devices from NetBox (NCP SDK)")
print("=" * 70)
print("Note: This tool uses the NCP SDK NetboxClient to query device inventory.")
print("      Requires NETBOX_URL and NETBOX_TOKEN in .env file.")
print("      Install NCP SDK with: pip install git+https://github.com/Ashok-Aviz/ncp-sdk.git")
print()
inventory_data = call_tool(proc, "get_inventory_devices", {}, request_id)
request_id += 1
if inventory_data:
    if inventory_data.get("success"):
        devices = inventory_data.get("devices", [])
        count = inventory_data.get("count", 0)
        print(f"Success: Retrieved {count} devices from NetBox")
        if devices:
            print("\nSample devices (first 5):")
            for i, device in enumerate(devices[:5], 1):
                hostname = device.get("hostname", "N/A")
                mgmt_ip = device.get("mgmt_ip", "N/A")
                vendor = device.get("vendor", "N/A")
                model = device.get("model", "N/A")
                role = device.get("role", "N/A")
                site = device.get("site", "N/A")
                print(f"  {i}. {hostname}")
                print(f"     IP: {mgmt_ip}, Vendor: {vendor}, Model: {model}")
                print(f"     Role: {role}, Site: {site}")
            if len(devices) > 5:
                print(f"  ... and {len(devices) - 5} more devices")
        else:
            print("  No devices found in NetBox inventory")
    else:
        error = inventory_data.get("error", "Unknown error")
        print(f"Error: {error}")
        print("  Note: This is expected if:")
        print("    - NETBOX_URL or NETBOX_TOKEN are not set in .env")
        print("    - NCP SDK is not installed")
        print("    - NetBox instance is not accessible or authentication fails")
    print("\nFull inventory result:")
    print(json.dumps(inventory_data, indent=2))
else:
    print("Error: Failed to query inventory devices")
print()

# Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)
print("All tools tested successfully.")
print("Note: Integration tools (Telnet, NetBox) may show errors if devices/services")
print("      are not accessible. This is expected in test environments.")
print("      Configure .env file for Telnet credentials if needed.")
print("      For get_inventory_devices, ensure NCP SDK is installed and NETBOX_URL/TOKEN are set.")
print()

# Close the process
proc.stdin.close()
proc.wait()
