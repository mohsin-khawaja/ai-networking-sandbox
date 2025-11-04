import asyncio
import json
from mcp.client.stdio import stdio_client

async def main():
    # Define the command properly for MCP 1.20
    command = {"command": "python", "args": ["mcp_test_server.py"]}

    # Connect to the MCP server via stdio
    async with stdio_client(command) as (read, write):
        # List all available tools
        tools = await write.call("tools/list")
        print("\n✅ Available Tools:")
        print(json.dumps(tools, indent=2))

        # Call get_link_status
        result = await write.call("tools/call", {
            "name": "get_link_status",
            "arguments": {}
        })
        print("\n🌐 Link Status:")
        print(json.dumps(result, indent=2))

        # Call predict_link_health
        prediction = await write.call("tools/call", {
            "name": "predict_link_health",
            "arguments": {"telemetry": {"errors": 2, "interface": "Ethernet12"}}
        })
        print("\n🤖 AI Prediction:")
        print(json.dumps(prediction, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
