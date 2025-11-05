"""
Simple test endpoint without dependencies to isolate issue.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/test", tags=["Test"])

class TestRequest(BaseModel):
    api_key: str

@router.post("/echo")
async def echo(request: TestRequest):
    """Simple echo endpoint."""
    return {
        "received": request.api_key,
        "length": len(request.api_key),
        "status": "ok"
    }

@router.post("/raw")
async def raw(request: Request):
    """Raw request test."""
    body = await request.body()
    return {
        "body_bytes": len(body),
        "body_preview": body[:100].decode('utf-8', errors='ignore'),
        "content_type": request.headers.get("content-type"),
        "status": "ok"
    }
