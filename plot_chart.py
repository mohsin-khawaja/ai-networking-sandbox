#!/usr/bin/env python3
"""
Plot telemetry timeseries chart from MCP server.

This script:
- Launches the MCP server via subprocess
- Sends MCP initialize request
- Calls get_telemetry_timeseries tool
- Extracts telemetry timestamps + values
- Uses matplotlib to display a line chart
- Closes/terminates the MCP server cleanly

Run:
  source .venv/bin/activate
  python plot_chart.py
"""
import json
import subprocess
import sys
import time
import signal
import os
from typing import Optional, Dict, Any

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Error: matplotlib not available. Install with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def send_request(method: str, params: Optional[Dict[str, Any]] = None, request_id: int = 1) -> str:
    """Send a JSON-RPC request."""
    req = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params or {}
    }
    return json.dumps(req) + "\n"


def read_response(proc: subprocess.Popen, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """Read a JSON-RPC response from the process with timeout."""
    import select
    
    # Try to read a line
    try:
        response_line = proc.stdout.readline()
        if response_line:
            line = response_line.strip()
            if line and line.startswith('{'):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        print(f"Error reading response: {e}", file=sys.stderr)
    
    return None


def call_tool(proc: subprocess.Popen, tool_name: str, arguments: Dict[str, Any], request_id: int) -> Optional[Dict[str, Any]]:
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
    
    # Wait for response
    time.sleep(0.5)  # Give server time to process
    response = read_response(proc)
    
    if response and "result" in response:
        result = response["result"]
        # Handle MCP response format: result.content[].text or result.content[].json
        if "content" in result and len(result["content"]) > 0:
            content_item = result["content"][0]
            # Check for JSON content
            if "json" in content_item:
                return content_item["json"]
            # Check for text content (JSON string)
            elif "text" in content_item:
                try:
                    return json.loads(content_item["text"])
                except json.JSONDecodeError:
                    return {"raw_content": content_item["text"]}
        # Direct result
        return result
    elif response and "error" in response:
        error = response["error"]
        error_msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        print(f"MCP tool error: {error_msg}", file=sys.stderr)
        return {"error": error_msg}
    
    return None


def main():
    """Main entry point for plotting telemetry chart."""
    print("=" * 70)
    print("Telemetry Timeseries Chart Plotter")
    print("=" * 70)
    print()
    
    # Check if MCP server script exists
    mcp_server_script = "mcp_server.py"
    if not os.path.exists(mcp_server_script):
        print(f"Error: {mcp_server_script} not found", file=sys.stderr)
        sys.exit(1)
    
    # Launch the MCP server
    print(f"Starting MCP server ({mcp_server_script})...")
    proc = subprocess.Popen(
        [sys.executable, mcp_server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    # Give server time to start
    time.sleep(2)
    
    # Check if process is still running
    if proc.poll() is not None:
        stderr_output = proc.stderr.read() if proc.stderr else ""
        print(f"Error: MCP server process terminated immediately (exit code: {proc.returncode})", file=sys.stderr)
        if stderr_output:
            print(f"Server stderr: {stderr_output}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Step 1: Initialize the MCP connection
        print("Initializing MCP connection...")
        init_request = send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "plot-chart-client",
                "version": "1.0.0"
            }
        }, request_id=1)
        
        try:
            proc.stdin.write(init_request)
            proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            print(f"Error: MCP server process terminated: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Read initialization response
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
        print(f"Connected to MCP server: {server_info.get('name', 'unknown')} v{server_info.get('version', 'unknown')}")
        
        # Step 2: Send initialized notification
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
        
        # Step 3: Call get_telemetry_timeseries tool
        print("\nCalling get_telemetry_timeseries tool...")
        request_id = 2
        telemetry_data = call_tool(proc, "get_telemetry_timeseries", {}, request_id)
        
        if not telemetry_data:
            print("Error: No response from get_telemetry_timeseries tool", file=sys.stderr)
            sys.exit(1)
        
        if "error" in telemetry_data:
            print(f"Error: {telemetry_data['error']}", file=sys.stderr)
            sys.exit(1)
        
        # Extract telemetry data
        metric = telemetry_data.get("metric", "utilization")
        timestamps = telemetry_data.get("timestamps", [])
        values = telemetry_data.get("values", [])
        
        if not timestamps or not values:
            print("Error: Invalid telemetry data (missing timestamps or values)", file=sys.stderr)
            print(f"Data received: {telemetry_data}", file=sys.stderr)
            sys.exit(1)
        
        if len(timestamps) != len(values):
            print(f"Error: Timestamp and value arrays have different lengths ({len(timestamps)} vs {len(values)})", file=sys.stderr)
            sys.exit(1)
        
        print(f"Received {len(timestamps)} data points")
        print(f"Metric: {metric}")
        print(f"Time range: {time.ctime(timestamps[0])} to {time.ctime(timestamps[-1])}")
        print(f"Utilization range: {min(values):.1%} to {max(values):.1%}")
        
        # Step 4: Plot the chart
        print("\nGenerating chart...")
        
        # Convert timestamps to datetime for better x-axis display
        from datetime import datetime
        datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Convert utilization values to percentages
        utilization_percent = [v * 100 for v in values]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(datetimes, utilization_percent, marker='o', linestyle='-', linewidth=2, markersize=4)
        plt.title("Network Utilization Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Utilization (%)")
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Show the chart
        print("Displaying chart...")
        plt.show()
        
        print("\nChart displayed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup: terminate the MCP server
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

