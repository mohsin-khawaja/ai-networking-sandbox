"""Telemetry agent for collecting network device telemetry."""
import random
from typing import Dict, List
from utils.logger import setup_logger
from utils.topology_builder import build_multi_vendor_topology

logger = setup_logger(__name__)


def get_port_telemetry() -> dict:
    """
    Simulate SONiC port telemetry metrics collection.
    
    Maps to Aviz NCP functionality:
    - Collects real-time interface statistics from SONiC switches via gNMI or REST APIs
    - Normalizes telemetry data for consumption by AI/ML models
    - Supports integration with gNMI telemetry streams for continuous monitoring
    - In production, this would stream data from actual network devices
    
    Returns:
        Dictionary containing port telemetry data:
        - switch: Device identifier
        - interface: Interface name
        - rx_bytes, tx_bytes: Traffic counters
        - rx_errors, tx_errors: Error counters
        - utilization: Link utilization percentage (0.0 to 1.0)
    """
    logger.info("Collecting SONiC port telemetry")
    telemetry = {
        "switch": "sonic-leaf-01",
        "interface": "Ethernet12",
        "rx_bytes": random.randint(10_000, 10_000_000),
        "tx_bytes": random.randint(10_000, 10_000_000),
        "rx_errors": random.randint(0, 10),
        "tx_errors": random.randint(0, 10),
        "utilization": round(random.uniform(0.2, 0.95), 2),
    }
    logger.debug(f"Telemetry collected: {telemetry}")
    return telemetry


def get_network_topology() -> dict:
    """
    Return a mock network topology with multiple device types.
    
    Simulates a multi-vendor network with SONiC, Cisco, FortiGate, and EdgeCore devices.
    This demonstrates Aviz NCP's vendor-agnostic approach to network management.
    
    Maps to Aviz NCP functionality:
    - Aggregates topology data from multiple vendor APIs
    - Normalizes device and link information
    - Provides unified view of network infrastructure
    
    Returns:
        Dictionary containing network topology with devices, links, and metadata
    """
    try:
        topology = build_multi_vendor_topology()
        logger.info(f"Topology generated: {topology['statistics']['total_devices']} devices, {topology['statistics']['total_links']} links")
        return topology
    except Exception as e:
        logger.error(f"Error generating topology: {e}")
        return {
            "error": "Failed to generate topology",
            "message": str(e),
            "devices": [],
            "links": [],
            "statistics": {}
        }

