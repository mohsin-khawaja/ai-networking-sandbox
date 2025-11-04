"""Topology building utilities for network graph generation."""
from typing import Dict, List
from utils.logger import setup_logger

logger = setup_logger(__name__)


def build_multi_vendor_topology() -> Dict:
    """
    Build a mock multi-vendor network topology.
    
    This function generates a realistic network graph representing
    Aviz NCP's vendor-agnostic approach to network management.
    
    Returns:
        Dictionary containing devices, links, and statistics
    """
    logger.info("Building multi-vendor network topology")
    
    devices = [
        {
            "id": "sonic-leaf-01",
            "type": "SONiC",
            "vendor": "Dell",
            "model": "S5248F-ON",
            "role": "leaf",
            "status": "active",
            "interfaces": [
                {"name": "Ethernet12", "status": "up", "speed": "25G"},
                {"name": "Ethernet24", "status": "up", "speed": "100G"}
            ]
        },
        {
            "id": "sonic-spine-01",
            "type": "SONiC",
            "vendor": "Arista",
            "model": "DCS-7280SR3",
            "role": "spine",
            "status": "active",
            "interfaces": [
                {"name": "Ethernet1/1", "status": "up", "speed": "100G"},
                {"name": "Ethernet1/2", "status": "up", "speed": "100G"}
            ]
        },
        {
            "id": "cisco-core-01",
            "type": "Cisco",
            "vendor": "Cisco",
            "model": "Nexus 9000",
            "role": "core",
            "status": "active",
            "interfaces": [
                {"name": "GigabitEthernet0/1", "status": "up", "speed": "10G"},
                {"name": "GigabitEthernet0/2", "status": "up", "speed": "10G"}
            ]
        },
        {
            "id": "fortigate-fw-01",
            "type": "FortiGate",
            "vendor": "Fortinet",
            "model": "FortiGate 100F",
            "role": "firewall",
            "status": "active",
            "interfaces": [
                {"name": "port1", "status": "up", "speed": "1G"},
                {"name": "port2", "status": "up", "speed": "1G"}
            ]
        },
        {
            "id": "edgecore-spine-02",
            "type": "SONiC",
            "vendor": "EdgeCore",
            "model": "AS7326-56X",
            "role": "spine",
            "status": "active",
            "interfaces": [
                {"name": "Ethernet1", "status": "up", "speed": "100G"},
                {"name": "Ethernet2", "status": "up", "speed": "100G"}
            ]
        }
    ]
    
    links = [
        {
            "source": "sonic-leaf-01",
            "source_port": "Ethernet24",
            "target": "sonic-spine-01",
            "target_port": "Ethernet1/1",
            "bandwidth": "100G",
            "status": "up"
        },
        {
            "source": "cisco-core-01",
            "source_port": "GigabitEthernet0/1",
            "target": "sonic-spine-01",
            "target_port": "Ethernet1/2",
            "bandwidth": "10G",
            "status": "up"
        },
        {
            "source": "fortigate-fw-01",
            "source_port": "port1",
            "target": "cisco-core-01",
            "target_port": "GigabitEthernet0/2",
            "bandwidth": "1G",
            "status": "up"
        },
        {
            "source": "edgecore-spine-02",
            "source_port": "Ethernet1",
            "target": "sonic-leaf-01",
            "target_port": "Ethernet12",
            "bandwidth": "25G",
            "status": "up"
        }
    ]
    
    # Calculate statistics
    sonic_devices = sum(1 for d in devices if d["type"] == "SONiC")
    non_sonic_devices = len(devices) - sonic_devices
    
    topology = {
        "timestamp": "2024-01-15T10:30:00Z",
        "devices": devices,
        "links": links,
        "statistics": {
            "total_devices": len(devices),
            "sonic_devices": sonic_devices,
            "non_sonic_devices": non_sonic_devices,
            "total_links": len(links),
            "active_links": sum(1 for l in links if l["status"] == "up")
        }
    }
    
    logger.debug(f"Topology built: {len(devices)} devices, {len(links)} links")
    return topology

