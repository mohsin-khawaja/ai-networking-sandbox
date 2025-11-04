# client_test.py
import json
import subprocess
import sys

def send_request(method, params=None, request_id=1):
    """Send a JSON-RPC request."""
    req = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    return json.dumps(req) + "\n"

def read_response(proc):
    """Read a JSON-RPC response from the process."""
    response_line = proc.stdout.readline()
    if response_line:
        return json.loads(response_line.strip())
    return None

# Launch the server
proc = subprocess.Popen(
    [sys.executable, "mcp_test_server.py"],
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
    print(f"✓ Connected to MCP server: {server_info.get('name', 'unknown')} v{server_info.get('version', 'unknown')}\n")

# Step 2: Send initialized notification (notifications don't have id)
initialized_notification = json.dumps({
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}) + "\n"
proc.stdin.write(initialized_notification)
proc.stdin.flush()

# Step 3: Get simulated telemetry
print("=" * 60)
print("📊 SONiC Port Telemetry")
print("=" * 60)
telemetry_request = send_request("tools/call", {
    "name": "get_port_telemetry",
    "arguments": {}
}, request_id=2)

proc.stdin.write(telemetry_request)
proc.stdin.flush()

telemetry_response = read_response(proc)
if telemetry_response and "result" in telemetry_response:
    result = telemetry_response["result"]
    if "content" in result and len(result["content"]) > 0:
        telemetry_text = result["content"][0].get("text", "{}")
        telemetry_data = json.loads(telemetry_text)
        print(json.dumps(telemetry_data, indent=2))
    else:
        print(json.dumps(result, indent=2))
else:
    print(f"Error: {json.dumps(telemetry_response, indent=2)}")

print()

# Step 4: Example AI prediction
print("=" * 60)
print("🤖 AI Link Health Prediction")
print("=" * 60)
ai_request = send_request("tools/call", {
    "name": "predict_link_health",
    "arguments": {
        "rx_errors": 2,
        "tx_errors": 5,
        "utilization": 0.85
    }
}, request_id=3)

proc.stdin.write(ai_request)
proc.stdin.flush()

ai_response = read_response(proc)
if ai_response and "result" in ai_response:
    result = ai_response["result"]
    if "content" in result and len(result["content"]) > 0:
        ai_text = result["content"][0].get("text", "{}")
        ai_data = json.loads(ai_text)
        print(json.dumps(ai_data, indent=2))
    else:
        print(json.dumps(result, indent=2))
else:
    print(f"Error: {json.dumps(ai_response, indent=2)}")

# Close the process
proc.stdin.close()
proc.wait()
