"""Configuration and compliance agent for coordinator system.

This agent handles configuration validation, firmware version checks,
and compliance monitoring queries.
"""
from typing import Dict, Any, Optional, List
from utils.logger import setup_logger
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta

logger = setup_logger(__name__)


class ConfigAgent:
    """Agent for handling configuration and compliance queries."""
    
    def __init__(self):
        """Initialize the config agent."""
        self.baseline_config = self._load_baseline_config()
        self.device_configs = self._load_device_configs()
        logger.info("Config agent initialized")
    
    def _load_baseline_config(self) -> Dict[str, Any]:
        """Load baseline configuration for compliance checking."""
        baseline_path = Path("data/config_baseline.yaml")
        if baseline_path.exists():
            try:
                with open(baseline_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load baseline config: {e}")
        return {}
    
    def _load_device_configs(self) -> List[Dict[str, Any]]:
        """Load device configuration data."""
        config_path = Path("data/config_baseline.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    return data.get("devices", [])
            except Exception as e:
                logger.warning(f"Failed to load device configs: {e}")
        return []
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a configuration-related query.
        
        Args:
            query: Natural language query
            context: Optional conversation context
            
        Returns:
            Dictionary with query result and summary
        """
        query_lower = query.lower()
        
        # Check for firmware/version queries
        if "firmware" in query_lower or "version" in query_lower or "outdated" in query_lower:
            outdated_devices = self._find_outdated_firmware()
            return {
                "success": True,
                "agent": "config",
                "query_type": "firmware_check",
                "data": outdated_devices,
                "summary": f"Found {len(outdated_devices)} device(s) with outdated firmware"
            }
        
        # Check for config drift queries
        if "drift" in query_lower or "compliance" in query_lower:
            drift_devices = self._find_config_drift()
            return {
                "success": True,
                "agent": "config",
                "query_type": "config_drift",
                "data": drift_devices,
                "summary": f"Found {len(drift_devices)} device(s) with configuration drift"
            }
        
        # Check for baseline comparison
        if "baseline" in query_lower:
            baseline_summary = self._get_baseline_summary()
            return {
                "success": True,
                "agent": "config",
                "query_type": "baseline",
                "data": baseline_summary,
                "summary": f"Baseline config: {baseline_summary.get('total_devices', 0)} devices configured"
            }
        
        # Default: return config status
        return {
            "success": True,
            "agent": "config",
            "query_type": "config_status",
            "data": {
                "total_devices": len(self.device_configs),
                "baseline_configured": len(self.baseline_config) > 0
            },
            "summary": f"Configuration status: {len(self.device_configs)} devices tracked"
        }
    
    def _find_outdated_firmware(self) -> List[Dict[str, Any]]:
        """Find devices with outdated firmware versions."""
        outdated = []
        baseline_version = self.baseline_config.get("target_firmware_version", "202311.1")
        
        for device in self.device_configs:
            current_version = device.get("firmware_version", "unknown")
            if current_version != baseline_version:
                outdated.append({
                    "device": device.get("name", "unknown"),
                    "current_version": current_version,
                    "target_version": baseline_version,
                    "status": "outdated"
                })
        
        return outdated
    
    def _find_config_drift(self) -> List[Dict[str, Any]]:
        """Find devices with configuration drift."""
        drift_devices = []
        
        baseline_settings = self.baseline_config.get("settings", {})
        
        for device in self.device_configs:
            device_settings = device.get("settings", {})
            drift_items = []
            
            for key, expected_value in baseline_settings.items():
                actual_value = device_settings.get(key)
                if actual_value != expected_value:
                    drift_items.append({
                        "setting": key,
                        "expected": expected_value,
                        "actual": actual_value
                    })
            
            if drift_items:
                drift_devices.append({
                    "device": device.get("name", "unknown"),
                    "drift_count": len(drift_items),
                    "drift_items": drift_items
                })
        
        return drift_devices
    
    def _get_baseline_summary(self) -> Dict[str, Any]:
        """Get summary of baseline configuration."""
        return {
            "target_firmware_version": self.baseline_config.get("target_firmware_version", "N/A"),
            "total_devices": len(self.device_configs),
            "baseline_settings": self.baseline_config.get("settings", {}),
            "last_updated": self.baseline_config.get("last_updated", "N/A")
        }

