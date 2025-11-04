"""File loading utilities for build JSONs and telemetry data."""
import json
import os
from pathlib import Path
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_build_json(file_path: str) -> Optional[Dict]:
    """
    Load and parse a build JSON file.
    
    Args:
        file_path: Path to the JSON file (can be relative to data/builds/)
        
    Returns:
        Parsed JSON data or None if file not found/invalid
    """
    # Resolve path - check if it's already absolute, or relative to data/builds/
    if not os.path.isabs(file_path):
        # Try relative to data/builds/ first
        data_path = Path(__file__).parent.parent / "data" / "builds" / file_path
        if data_path.exists():
            file_path = str(data_path)
        else:
            # Try as relative to current working directory
            file_path = os.path.abspath(file_path)
    
    logger.debug(f"Loading build JSON from: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"Build file not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded build JSON: {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def list_available_builds() -> list:
    """
    List all available build JSON files in data/builds/.
    
    Returns:
        List of build file names
    """
    builds_dir = Path(__file__).parent.parent / "data" / "builds"
    if not builds_dir.exists():
        logger.warning(f"Builds directory not found: {builds_dir}")
        return []
    
    build_files = [
        f.name for f in builds_dir.iterdir() 
        if f.is_file() and f.suffix == '.json'
    ]
    logger.debug(f"Found {len(build_files)} build files")
    return sorted(build_files)

