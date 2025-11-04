"""MCP Server for Aviz NCP AI Agent.

This agent simulates Aviz NCP's AI infrastructure for validating builds,
monitoring multi-vendor telemetry, predicting link health, and automated remediation.

The server orchestrates multiple AI agents that work together to provide
vendor-agnostic network observability, validation, and automation capabilities.
"""
from mcp.server.fastmcp import FastMCP
from utils.logger import setup_logger
from agents.telemetry_agent import get_port_telemetry as _get_port_telemetry, get_network_topology as _get_network_topology
from agents.ai_agent import predict_link_health as _predict_link_health
from agents.build_agent import validate_build_metadata as _validate_build_metadata
from agents.remediation_agent import remediate_link as _remediate_link

# Initialize logger
logger = setup_logger(__name__)

# Initialize MCP server
mcp = FastMCP("aviz-ncp-ai-agent")
logger.info("Initializing Aviz NCP AI Agent MCP Server")


# -----------------------------
# 1. TELEMETRY TOOLS
# -----------------------------

@mcp.tool()
def get_port_telemetry() -> dict:
    """
    Simulate SONiC port telemetry metrics.
    
    Maps to Aviz NCP functionality:
    - Collects real-time interface statistics from SONiC switches
    - Normalizes data for consumption by AI/ML models
    - Supports integration with gNMI telemetry streams
    
    Returns:
        Dictionary containing port telemetry data (rx_bytes, tx_bytes, errors, utilization)
    """
    try:
        return _get_port_telemetry()
    except Exception as e:
        logger.error(f"Error collecting port telemetry: {e}")
        return {
            "error": "Telemetry collection failed",
            "message": str(e)
        }


@mcp.tool()
def get_network_topology() -> dict:
    """
    Return a mock network topology with multiple device types.
    
    Simulates a multi-vendor network with SONiC, Cisco, FortiGate, and EdgeCore devices.
    This demonstrates Aviz NCP's vendor-agnostic approach to network management.
    
    Maps to Aviz NCP functionality:
    - Aggregates topology data from multiple vendor APIs
    - Normalizes device and link information across vendors
    - Provides unified view of network infrastructure
    - Supports both SONiC (~5%) and non-SONiC devices (~95%)
    
    Returns:
        Dictionary containing network topology with devices, links, and statistics
    """
    try:
        return _get_network_topology()
    except Exception as e:
        logger.error(f"Error generating network topology: {e}")
        return {
            "error": "Topology generation failed",
            "message": str(e),
            "devices": [],
            "links": [],
            "statistics": {}
        }


# -----------------------------
# 2. AI PREDICTION TOOLS
# -----------------------------

@mcp.tool()
def predict_link_health(rx_errors: int, tx_errors: int, utilization: float) -> dict:
    """
    Run AI model to predict overall link health based on telemetry.
    
    Uses a PyTorch neural network to analyze link metrics and predict health.
    Supports GPU acceleration via MPS (Mac) or CUDA (Linux/Windows).
    
    Maps to Aviz NCP functionality:
    - Analyzes real-time telemetry from network devices
    - Uses ML model to predict link degradation before failures occur
    - Provides actionable health scores for monitoring and alerting
    - Integrates with remediation workflows for automated response
    
    Args:
        rx_errors: Number of receive errors
        tx_errors: Number of transmit errors
        utilization: Link utilization (0.0 to 1.0)
        
    Returns:
        Dictionary containing health_score and status
    """
    try:
        return _predict_link_health(rx_errors, tx_errors, utilization)
    except Exception as e:
        logger.error(f"Error predicting link health: {e}")
        return {
            "error": "Health prediction failed",
            "message": str(e),
            "health_score": None,
            "status": "error"
        }


# -----------------------------
# 3. BUILD VALIDATION TOOLS
# -----------------------------

@mcp.tool()
def validate_build_metadata(build_json_path: str) -> dict:
    """
    Validate SONiC or non-SONiC build JSON files.
    
    Checks build metadata files for required fields and structure.
    Supports both SONiC and non-SONiC device builds with different validation rules.
    
    Maps to Aviz NCP functionality:
    - Validates build metadata before deployment
    - Ensures version, hardware, and feature consistency
    - Prevents deployment of incompatible or misconfigured builds
    - Supports vendor-agnostic build validation workflows
    
    Args:
        build_json_path: Path to the build JSON file (can be relative to data/builds/)
        
    Returns:
        Dictionary containing validation results, errors, and warnings
    """
    try:
        return _validate_build_metadata(build_json_path)
    except Exception as e:
        logger.error(f"Error validating build metadata: {e}")
        return {
            "valid": False,
            "error": "Validation failed",
            "message": str(e),
            "errors": [str(e)],
            "warnings": []
        }


# -----------------------------
# 4. REMEDIATION TOOLS
# -----------------------------

@mcp.tool()
def remediate_link(interface: str) -> dict:
    """
    Mock closed-loop automation tool that returns recommended remediation action.
    
    Analyzes interface health and returns actionable remediation recommendations.
    In production, this would integrate with Ansible or similar automation tools
    to execute remediation actions automatically.
    
    Maps to Aviz NCP functionality:
    - Analyzes link health from telemetry data
    - Determines appropriate remediation action based on device type and issue
    - Returns actionable recommendations for automation workflows
    - Supports closed-loop automation for network operations
    
    Args:
        interface: Interface name (e.g., "Ethernet12", "GigabitEthernet0/1")
        
    Returns:
        Dictionary containing recommended action, reason, and confidence
    """
    try:
        return _remediate_link(interface)
    except Exception as e:
        logger.error(f"Error generating remediation recommendation: {e}")
        return {
            "error": "Remediation analysis failed",
            "message": str(e),
            "interface": interface,
            "recommended_action": None
        }


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    logger.info("Running Aviz NCP AI Agent MCP Server")
    logger.info("Available tools:")
    logger.info("  1. get_port_telemetry - Collect SONiC port telemetry")
    logger.info("  2. get_network_topology - Get multi-vendor network topology")
    logger.info("  3. predict_link_health - AI-based link health prediction")
    logger.info("  4. validate_build_metadata - Validate build JSON files")
    logger.info("  5. remediate_link - Automated link remediation recommendations")
    logger.info("Waiting for requests on stdio...")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error in MCP server: {e}")
        raise

