"""Utility functions and helpers."""

import hashlib
import json
from datetime import date, datetime
from typing import Any


def hash_query(query: str) -> str:
    """
    Generate SHA256 hash for a query.
    
    Args:
        query: SQL query or any string
        
    Returns:
        str: SHA256 hash
    """
    return hashlib.sha256(query.encode()).hexdigest()


def serialize_datetime(obj: Any) -> Any:
    """
    JSON serializer for datetime objects.
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serializable object
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def parse_csv_param(param: str) -> list[str]:
    """
    Parse comma-separated parameter.
    
    Args:
        param: CSV parameter string
        
    Returns:
        list: Parsed values
    """
    if not param:
        return []
    return [v.strip() for v in param.split(",")]


def build_query_string(params: dict[str, Any]) -> str:
    """
    Build query string from parameters.
    
    Args:
        params: Parameter dictionary
        
    Returns:
        str: Query string
    """
    return "&".join(f"{k}={v}" for k, v in params.items() if v is not None)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, obj: Any) -> Any:
        """Encode datetime objects."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)
