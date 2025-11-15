"""
Webhook API endpoints.
"""

import time
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

# In-memory webhook storage (replace with database in production)
webhooks: List[Dict[str, Any]] = []
webhook_counter = 0


class WebhookCreate(BaseModel):
    url: str
    event_types: List[str] = ["product.created", "product.updated", "product.deleted"]
    enabled: bool = True


class WebhookUpdate(BaseModel):
    url: str = None
    event_types: List[str] = None
    enabled: bool = None


@router.get("/webhooks", response_class=HTMLResponse)
async def webhook_management():
    """Webhook management interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webhooks - Product Importer</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #007bff; }
            .controls { margin: 20px 0; display: flex; gap: 10px; align-items: center; }
            .controls input, .controls select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #0056b3; }
            .btn-danger { background: #dc3545; }
            .btn-danger:hover { background: #c82333; }
            .btn-small { padding: 5px 10px; font-size: 12px; }
            .webhook-item { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px 0; background: #f8f9fa; }
            .webhook-info { margin-bottom: 10px; }
            .webhook-actions { display: flex; gap: 10px; }
            .test-result { margin: 15px 0; padding: 10px; border-radius: 4px; }
            .test-result.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .test-result.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .form-group { margin: 15px 0; }
            .form-group label { display: block; margin-bottom: 5px; }
            .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            #webhook-form { background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Upload</a>
            <a href="/products">Products</a>
            <a href="/webhooks">Webhooks</a>
        </div>

        <h1>Webhook Management</h1>
        
        <form id="webhook-form">
            <div class="form-group">
                <label for="webhook-url">Webhook URL:</label>
                <input type="url" id="webhook-url" placeholder="https://example.com/webhook" required>
            </div>
            <div class="form-group">
                <label for="event-types">Event Types:</label>
                <select id="event-types" multiple>
                    <option value="product.created" selected>Product Created</option>
                    <option value="product.updated" selected>Product Updated</option>
                    <option value="product.deleted" selected>Product Deleted</option>
                </select>
            </div>
            <div class="form-group">
                <label><input type="checkbox" id="webhook-enabled" checked> Enabled</label>
            </div>
            <button type="submit" class="btn">Add Webhook</button>
        </form>

        <div id="webhook-list"></div>
        <div id="test-results"></div>

        <script src="/static/webhooks.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/api/webhooks")
async def list_webhooks():
    """Get all webhooks."""
    return {"webhooks": webhooks}


@router.post("/webhooks")
async def create_webhook(webhook_data: WebhookCreate):
    """Create a new webhook."""
    global webhook_counter
    webhook_counter += 1
    
    webhook = {
        "id": webhook_counter,
        "url": webhook_data.url,
        "event_types": webhook_data.event_types,
        "enabled": webhook_data.enabled,
        "created_at": "2025-11-15T11:09:00Z"
    }
    webhooks.append(webhook)
    return webhook


@router.put("/webhooks/{webhook_id}")
async def update_webhook(webhook_id: int, webhook_data: WebhookUpdate):
    """Update a webhook."""
    webhook = next((w for w in webhooks if w["id"] == webhook_id), None)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook_data.url is not None:
        webhook["url"] = webhook_data.url
    if webhook_data.event_types is not None:
        webhook["event_types"] = webhook_data.event_types
    if webhook_data.enabled is not None:
        webhook["enabled"] = webhook_data.enabled
    
    return webhook


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: int):
    """Delete a webhook."""
    global webhooks
    webhooks = [w for w in webhooks if w["id"] != webhook_id]
    return {"message": "Webhook deleted"}


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: int):
    """Test a webhook with response details."""
    webhook = next((w for w in webhooks if w["id"] == webhook_id), None)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    start_time = time.time()
    test_payload = {"event": "test", "timestamp": "2025-11-15T11:09:00Z"}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook["url"], json=test_payload)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "url": webhook["url"]
            }
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            "success": False,
            "error": str(e),
            "response_time_ms": response_time,
            "url": webhook["url"]
        }
