"""Ticketing agent for coordinator system.

This agent handles ServiceNow, Zendesk, and JIRA ticket queries.
"""
from typing import Dict, Any, Optional, List
from utils.logger import setup_logger
import json
from pathlib import Path
from datetime import datetime

logger = setup_logger(__name__)


class TicketingAgent:
    """Agent for handling ticketing system queries."""
    
    def __init__(self):
        """Initialize the ticketing agent."""
        self.tickets = self._load_tickets()
        logger.info("Ticketing agent initialized")
    
    def _load_tickets(self) -> List[Dict[str, Any]]:
        """Load ticket data from JSON file."""
        tickets_path = Path("data/tickets.json")
        if tickets_path.exists():
            try:
                with open(tickets_path, 'r') as f:
                    data = json.load(f)
                    return data.get("tickets", [])
            except Exception as e:
                logger.warning(f"Failed to load tickets: {e}")
        return []
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a ticketing-related query.
        
        Args:
            query: Natural language query
            context: Optional conversation context
            
        Returns:
            Dictionary with query result and summary
        """
        query_lower = query.lower()
        
        # Check for open tickets query
        if "open" in query_lower and "ticket" in query_lower:
            open_tickets = [t for t in self.tickets if t.get("status", "").lower() != "closed"]
            return {
                "success": True,
                "agent": "ticketing",
                "query_type": "open_tickets",
                "data": open_tickets,
                "summary": f"Found {len(open_tickets)} open ticket(s)"
            }
        
        # Check for high priority tickets
        if "high priority" in query_lower or "critical" in query_lower:
            high_priority = [t for t in self.tickets if t.get("priority", "").lower() in ["high", "critical"]]
            return {
                "success": True,
                "agent": "ticketing",
                "query_type": "high_priority",
                "data": high_priority,
                "summary": f"Found {len(high_priority)} high-priority ticket(s)"
            }
        
        # Check for device-specific tickets
        import re
        device_pattern = r'\b(sonic-\S+|nexus-\S+|edgecore-\S+|celtica-\S+|\S+-\d+)\b'
        device_match = re.search(device_pattern, query, re.IGNORECASE)
        if device_match:
            device_name = device_match.group(1)
            device_tickets = [t for t in self.tickets if device_name.lower() in t.get("device", "").lower()]
            return {
                "success": True,
                "agent": "ticketing",
                "query_type": "device_tickets",
                "data": device_tickets,
                "summary": f"Found {len(device_tickets)} ticket(s) for device {device_name}"
            }
        
        # Check for ServiceNow or Zendesk specific queries
        if "servicenow" in query_lower:
            servicenow_tickets = [t for t in self.tickets if t.get("source", "").lower() == "servicenow"]
            return {
                "success": True,
                "agent": "ticketing",
                "query_type": "servicenow_tickets",
                "data": servicenow_tickets,
                "summary": f"Found {len(servicenow_tickets)} ServiceNow ticket(s)"
            }
        
        if "zendesk" in query_lower:
            zendesk_tickets = [t for t in self.tickets if t.get("source", "").lower() == "zendesk"]
            return {
                "success": True,
                "agent": "ticketing",
                "query_type": "zendesk_tickets",
                "data": zendesk_tickets,
                "summary": f"Found {len(zendesk_tickets)} Zendesk ticket(s)"
            }
        
        # Default: return all tickets
        return {
            "success": True,
            "agent": "ticketing",
            "query_type": "all_tickets",
            "data": self.tickets,
            "summary": f"Retrieved {len(self.tickets)} ticket(s) from ticketing systems"
        }

