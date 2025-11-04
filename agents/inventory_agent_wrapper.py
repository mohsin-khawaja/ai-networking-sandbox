"""Inventory agent wrapper for coordinator system.

This wraps the existing inventory_agent functions into a class-based interface
for the coordinator system.
"""
from typing import Dict, Any, Optional
from utils.logger import setup_logger
from agents.inventory_agent import (
    get_device_info,
    list_devices_by_vlan,
    get_vlan_table,
    load_device_inventory
)

logger = setup_logger(__name__)


class InventoryAgent:
    """Agent for handling device inventory queries."""
    
    def __init__(self):
        """Initialize the inventory agent."""
        # Ensure inventory is loaded
        try:
            load_device_inventory()
        except Exception as e:
            logger.warning(f"Failed to load device inventory: {e}")
        logger.info("Inventory agent initialized")
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an inventory-related query.
        
        Args:
            query: Natural language query
            context: Optional conversation context
            
        Returns:
            Dictionary with query result and summary
        """
        query_lower = query.lower()
        
        # Extract VLAN ID if present
        import re
        vlan_match = re.search(r'vlan\s+(\d+)', query_lower)
        if vlan_match:
            vlan_id = int(vlan_match.group(1))
            result = list_devices_by_vlan(vlan_id)
            return {
                "success": True,
                "agent": "inventory",
                "query_type": "vlan_lookup",
                "data": result,
                "summary": f"Found {result.get('count', 0)} device(s) on VLAN {vlan_id}"
            }
        
        # Check for VLAN table request
        if "vlan table" in query_lower or "show vlan" in query_lower:
            result = get_vlan_table()
            return {
                "success": True,
                "agent": "inventory",
                "query_type": "vlan_table",
                "data": result,
                "summary": f"VLAN table with {result.get('total_vlans', 0)} VLANs"
            }
        
        # Extract device name if present
        device_pattern = r'\b(sonic-\S+|nexus-\S+|edgecore-\S+|celtica-\S+|\S+-\d+)\b'
        device_match = re.search(device_pattern, query, re.IGNORECASE)
        if device_match:
            device_name = device_match.group(1)
            result = get_device_info(device_name=device_name)
            if result.get("success"):
                device = result.get("device", {})
                return {
                    "success": True,
                    "agent": "inventory",
                    "query_type": "device_info",
                    "data": result,
                    "summary": f"Device {device_name}: {device.get('role', 'N/A')} role, {len(device.get('vlans', []))} VLAN(s)"
                }
            else:
                return {
                    "success": False,
                    "agent": "inventory",
                    "query_type": "device_info",
                    "data": result,
                    "summary": f"Device {device_name} not found in inventory"
                }
        
        # Check for list all devices queries
        if "list all" in query_lower or "show all" in query_lower:
            if "sonic" in query_lower:
                result = get_device_info(query_type="sonic")
            else:
                result = get_device_info(query_type="all")
            
            count = result.get("count", 0)
            return {
                "success": True,
                "agent": "inventory",
                "query_type": "device_list",
                "data": result,
                "summary": f"Found {count} device(s) in inventory"
            }
        
        # Default: return all devices
        result = get_device_info(query_type="all")
        return {
            "success": True,
            "agent": "inventory",
            "query_type": "device_list",
            "data": result,
            "summary": f"Retrieved {result.get('count', 0)} device(s) from inventory"
        }

