"""Telemetry agent wrapper for coordinator system.

This wraps the existing telemetry_agent functions into a class-based interface
for the coordinator system.
"""
from typing import Dict, Any, Optional, List
from utils.logger import setup_logger
from agents.telemetry_agent import get_port_telemetry, get_network_topology
import json
from pathlib import Path

logger = setup_logger(__name__)


class TelemetryAgent:
    """Agent for handling telemetry and monitoring queries."""
    
    def __init__(self):
        """Initialize the telemetry agent."""
        # Load telemetry data
        self.telemetry_data = self._load_telemetry_data()
        logger.info("Telemetry agent initialized")
    
    def _load_telemetry_data(self) -> List[Dict[str, Any]]:
        """Load telemetry data from JSON file."""
        telemetry_path = Path("data/telemetry_data.json")
        if telemetry_path.exists():
            try:
                with open(telemetry_path, 'r') as f:
                    data = json.load(f)
                    return data.get("telemetry", [])
            except Exception as e:
                logger.warning(f"Failed to load telemetry data: {e}")
        return []
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a telemetry-related query.
        
        Args:
            query: Natural language query
            context: Optional conversation context
            
        Returns:
            Dictionary with query result and summary
        """
        query_lower = query.lower()
        
        # Check for error threshold queries
        import re
        error_match = re.search(r'(rx_errors|tx_errors|errors?)\s*(?:>|greater than|above|more than)?\s*(\d+)', query_lower)
        if error_match:
            threshold = int(error_match.group(2))
            error_type = error_match.group(1)
            matching_devices = self._find_devices_with_errors(threshold, error_type)
            return {
                "success": True,
                "agent": "telemetry",
                "query_type": "error_threshold",
                "data": matching_devices,
                "summary": f"Found {len(matching_devices)} device(s) with {error_type} > {threshold}"
            }
        
        # Check for utilization queries
        util_match = re.search(r'(utilization|usage|bandwidth)\s*(?:>|greater than|above|high)', query_lower)
        if util_match or "high usage" in query_lower or "high cpu" in query_lower:
            high_usage_devices = self._find_high_utilization_devices()
            return {
                "success": True,
                "agent": "telemetry",
                "query_type": "high_utilization",
                "data": high_usage_devices,
                "summary": f"Found {len(high_usage_devices)} device(s) with high utilization"
            }
        
        # Check for interface status queries
        if "interface" in query_lower and ("status" in query_lower or "show" in query_lower):
            # Get sample telemetry
            telemetry = get_port_telemetry()
            return {
                "success": True,
                "agent": "telemetry",
                "query_type": "interface_status",
                "data": telemetry,
                "summary": f"Interface {telemetry.get('interface')} on {telemetry.get('switch')}: {telemetry.get('utilization', 0):.1%} utilization"
            }
        
        # Check for topology queries
        if "topology" in query_lower or "network" in query_lower:
            topology = get_network_topology()
            stats = topology.get("statistics", {})
            return {
                "success": True,
                "agent": "telemetry",
                "query_type": "topology",
                "data": topology,
                "summary": f"Network topology: {stats.get('total_devices', 0)} devices, {stats.get('total_links', 0)} links"
            }
        
        # Default: return all telemetry data
        if self.telemetry_data:
            return {
                "success": True,
                "agent": "telemetry",
                "query_type": "all_telemetry",
                "data": self.telemetry_data,
                "summary": f"Retrieved telemetry for {len(self.telemetry_data)} device(s)"
            }
        else:
            # Fallback to generating sample telemetry
            telemetry = get_port_telemetry()
            return {
                "success": True,
                "agent": "telemetry",
                "query_type": "sample_telemetry",
                "data": telemetry,
                "summary": f"Sample telemetry: {telemetry.get('switch')} interface {telemetry.get('interface')}"
            }
    
    def _find_devices_with_errors(self, threshold: int, error_type: str) -> List[Dict[str, Any]]:
        """Find devices with errors above threshold."""
        matching = []
        
        if self.telemetry_data:
            for entry in self.telemetry_data:
                errors = 0
                if error_type.startswith("rx"):
                    errors = entry.get("rx_errors", 0)
                elif error_type.startswith("tx"):
                    errors = entry.get("tx_errors", 0)
                else:
                    errors = entry.get("rx_errors", 0) + entry.get("tx_errors", 0)
                
                if errors > threshold:
                    matching.append(entry)
        
        return matching
    
    def _find_high_utilization_devices(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find devices with high utilization."""
        matching = []
        
        if self.telemetry_data:
            for entry in self.telemetry_data:
                utilization = entry.get("utilization", 0.0)
                if utilization > threshold:
                    matching.append(entry)
        
        return matching

