from bson import ObjectId
from datetime import datetime
from typing import Any, Dict, List, Union

def serialize_doc(doc: Any) -> Any:
    """
    Convert MongoDB document to JSON-serializable dict.
    Handles ObjectId and datetime conversion.
    """
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == '_id':
                result['id'] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = [serialize_doc(item) if isinstance(item, (dict, list)) else item for item in value]
            else:
                result[key] = value
        return result
    
    return doc

def parse_object_id(id_str: str) -> ObjectId:
    """Parse string to ObjectId with validation"""
    try:
        return ObjectId(id_str)
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid ID format")
