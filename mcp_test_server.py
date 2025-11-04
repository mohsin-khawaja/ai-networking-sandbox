from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aviz-ai-agent")

@mcp.tool()
def get_link_status() -> dict:
    return {"switch": "sonic-leaf-01", "interface": "Ethernet12", "status": "up", "errors": 0}

@mcp.tool()
def predict_link_health(telemetry: dict) -> dict:
    score = 0.98 if telemetry.get("errors", 0) < 10 else 0.65
    return {"predicted_health_score": score, "confidence": "high" if score > 0.9 else "medium"}

if __name__ == "__main__":
    print("Running Aviz AI Agent prototype…")
    mcp.run()
