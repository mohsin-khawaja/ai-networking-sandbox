#!/usr/bin/env python3
"""
Quick test script for get_inventory_devices MCP tool.

This script:
1. Starts the MCP server
2. Calls get_inventory_devices tool
3. Displays the results

Run:
    python test_inventory_devices.py
"""
import json
import subprocess
import sys
import time
import os

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
    """Read a JSON-RPC response from the process."""
    try:
        response_line = proc.stdout.readline()
        if response_line:
            return json.loads(response_line.strip())
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"Error reading response: {e}", file=sys.stderr)
        return None
    return None

def call_tool(proc, tool_name, arguments, request_id):
    """Call an MCP tool and return the result."""
    request = send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments
    }, request_id=request_id)
    
    try:
        proc.stdin.write(request)
        proc.stdin.flush()
    except (BrokenPipeError, OSError) as e:
        print(f"Error writing to MCP server: {e}", file=sys.stderr)
        return None
    
    time.sleep(0.5)
    response = read_response(proc)
    
    if response and "result" in response:
        result = response["result"]
        if "content" in result and len(result["content"]) > 0:
            content_item = result["content"][0]
            if "json" in content_item:
                return content_item["json"]
            elif "text" in content_item:
                try:
                    return json.loads(content_item["text"])
                except json.JSONDecodeError:
                    return {"raw_content": content_item["text"]}
        return result
    elif response and "error" in response:
        error = response["error"]
        error_msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        print(f"MCP tool error: {error_msg}", file=sys.stderr)
        return {"error": error_msg}
    
    return None

def main():
    """Main entry point for testing get_inventory_devices."""
    print("=" * 70)
    print("Testing get_inventory_devices MCP Tool")
    print("=" * 70)
    print()
    
    # Check if .env exists and has NETBOX_URL/TOKEN
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✓ Found {env_file} file")
        # Load env vars to check
        try:
            from dotenv import load_dotenv
            load_dotenv()
            netbox_url = os.getenv("NETBOX_URL")
            netbox_token = os.getenv("NETBOX_TOKEN")
            if netbox_url:
                print(f"✓ NETBOX_URL is set: {netbox_url}")
            else:
                print("⚠ NETBOX_URL is not set in .env")
            if netbox_token:
                print(f"✓ NETBOX_TOKEN is set: {'*' * (len(netbox_token) - 4) + netbox_token[-4:]}")
            else:
                print("⚠ NETBOX_TOKEN is not set in .env")
        except ImportError:
            print("⚠ python-dotenv not available")
    else:
        print(f"⚠ {env_file} file not found")
        print("  Create .env file with:")
        print("    NETBOX_URL=https://your-netbox-instance.com")
        print("    NETBOX_TOKEN=your-api-token-here")
    
    print()
    
    # Check if NCP SDK is installed
    try:
        from ncp_sdk.netbox import NetboxClient
        print("✓ NCP SDK is installed")
    except ImportError:
        print("✗ NCP SDK is not installed")
        print()
        print("Install it with:")
        print("  pip install git+https://github.com/Ashok-Aviz/ncp-sdk.git")
        print()
        print("Note: The tool will return an error if NCP SDK is not installed.")
        print("      But we can still test the error handling.")
    
    print()
    print("Starting MCP server...")
    print()
    
    mcp_server_script = "mcp_server.py"
    if not os.path.exists(mcp_server_script):
        print(f"Error: {mcp_server_script} not found", file=sys.stderr)
        sys.exit(1)
    
    proc = subprocess.Popen(
        [sys.executable, mcp_server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    time.sleep(2)
    
    if proc.poll() is not None:
        stderr_output = proc.stderr.read() if proc.stderr else ""
        print(f"Error: MCP server process terminated (exit code: {proc.returncode})", file=sys.stderr)
        if stderr_output:
            print(f"Server stderr: {stderr_output}", file=sys.stderr)
        sys.exit(1)
    
    try:
        print("Initializing MCP connection...")
        init_request = send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-inventory-client",
                "version": "1.0.0"
            }
        }, request_id=1)
        
        try:
            proc.stdin.write(init_request)
            proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            print(f"Error: MCP server process terminated: {e}", file=sys.stderr)
            sys.exit(1)
        
        time.sleep(0.5)
        init_response = read_response(proc)
        
        if not init_response or "result" not in init_response:
            print("Error: Failed to initialize MCP connection", file=sys.stderr)
            if init_response and "error" in init_response:
                error = init_response["error"]
                error_msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
                print(f"MCP error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        server_info = init_response["result"].get("serverInfo", {})
        print(f"✓ Connected to MCP server: {server_info.get('name', 'unknown')} v{server_info.get('version', 'unknown')}")
        
        initialized_notification = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }) + "\n"
        
        try:
            proc.stdin.write(initialized_notification)
            proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            print(f"Error: MCP server process terminated: {e}", file=sys.stderr)
            sys.exit(1)
        
        time.sleep(0.5)
        
        print()
        print("Calling get_inventory_devices tool...")
        print()
        
        request_id = 2
        inventory_data = call_tool(proc, "get_inventory_devices", {}, request_id)
        
        if not inventory_data:
            print("Error: No response from get_inventory_devices tool", file=sys.stderr)
            sys.exit(1)
        
        # Display results
        print("=" * 70)
        print("Results")
        print("=" * 70)
        print()
        
        if inventory_data.get("success"):
            devices = inventory_data.get("devices", [])
            count = inventory_data.get("count", 0)
            print(f"✓ Success! Retrieved {count} devices from NetBox")
            print()
            
            if devices:
                print("Device Inventory:")
                print("-" * 70)
                for i, device in enumerate(devices[:10], 1):  # Show first 10
                    hostname = device.get("hostname", "N/A")
                    mgmt_ip = device.get("mgmt_ip", "N/A")
                    vendor = device.get("vendor", "N/A")
                    model = device.get("model", "N/A")
                    role = device.get("role", "N/A")
                    site = device.get("site", "N/A")
                    region = device.get("region", "N/A")
                    
                    print(f"{i}. {hostname}")
                    print(f"   IP: {mgmt_ip}")
                    print(f"   Vendor: {vendor}, Model: {model}")
                    print(f"   Role: {role}")
                    if site != "N/A":
                        print(f"   Site: {site}")
                    if region != "N/A":
                        print(f"   Region: {region}")
                    print()
                
                if len(devices) > 10:
                    print(f"... and {len(devices) - 10} more devices")
                    print()
            else:
                print("No devices found in NetBox inventory")
                print()
        else:
            error = inventory_data.get("error", "Unknown error")
            print(f"✗ Error: {error}")
            print()
            print("Troubleshooting:")
            print("  1. Check that NETBOX_URL and NETBOX_TOKEN are set in .env")
            print("  2. Verify NCP SDK is installed: pip install git+https://github.com/Ashok-Aviz/ncp-sdk.git")
            print("  3. Ensure your NetBox instance is accessible")
            print("  4. Verify your API token has the correct permissions")
            print()
        
        print("Full JSON Response:")
        print("-" * 70)
        print(json.dumps(inventory_data, indent=2))
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up MCP server...")
        try:
            proc.stdin.close()
        except:
            pass
        
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        except:
            pass
        
        print("Done.")

if __name__ == "__main__":
    main()

