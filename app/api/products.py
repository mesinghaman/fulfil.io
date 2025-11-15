"""
Product API routes.

This module contains all API endpoints related to product operations
including upload, CRUD operations, and bulk operations.
"""

import uuid
import asyncio
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models import get_db, Product
from app.services import ProductService

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Global storage for async operations
progress_store = {}
cancel_flags = {}
executor = ThreadPoolExecutor(max_workers=2)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the main upload interface.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered upload page
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload-direct")
async def upload_file_direct(file: UploadFile = File(...)):
    """
    Upload and process CSV file asynchronously.
    
    Args:
        file (UploadFile): Uploaded CSV file
        
    Returns:
        dict: Task information for progress tracking
        
    Raises:
        HTTPException: If file is not CSV or upload fails
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    task_id = str(uuid.uuid4())
    progress_store[task_id] = {
        "progress": 0, 
        "status": "Starting...", 
        "completed": False
    }
    
    try:
        content = await file.read()
        
        # Save temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Start async processing
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor, 
            ProductService.import_products_from_csv,
            file_path, 
            task_id, 
            progress_store, 
            cancel_flags
        )
        
        return {"status": "processing", "task_id": task_id}
        
    except Exception as e:
        progress_store[task_id] = {
            "progress": 0,
            "status": f"Error: {str(e)}",
            "completed": True,
            "error": True
        }
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/progress/{task_id}")
async def get_progress_stream(task_id: str):
    """
    Get real-time progress updates via Server-Sent Events.
    
    Args:
        task_id (str): Task identifier
        
    Returns:
        StreamingResponse: SSE stream with progress updates
    """
    async def event_stream():
        while task_id in progress_store:
            data = progress_store[task_id]
            import json
            yield f"data: {json.dumps(data)}\n\n"
            if data.get('completed'):
                await asyncio.sleep(1)
                if task_id in progress_store:
                    del progress_store[task_id]
                break
            await asyncio.sleep(0.5)
    
    return StreamingResponse(
        event_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get task status for progress polling.
    
    Args:
        task_id (str): Task identifier
        
    Returns:
        dict: Task status and progress information
    """
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    data = progress_store[task_id]
    
    # Convert to Celery-like format for compatibility
    if data.get('completed'):
        if 'error' in data:
            return {
                "state": "FAILURE",
                "result": data.get('error', 'Unknown error')
            }
        else:
            return {
                "state": "SUCCESS",
                "result": {
                    "imported": data.get('imported', 0),
                    "total": data.get('total', 0)
                }
            }
    else:
        return {
            "state": "PROGRESS",
            "progress": data.get('progress', 0),
            "current": data.get('current', 0),
            "total": data.get('total', 0),
            "status": data.get('status', 'Processing...')
        }


@router.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running import task.
    
    Args:
        task_id (str): Task identifier to cancel
        
    Returns:
        dict: Cancellation status
    """
    cancel_flags[task_id] = True
    if task_id in progress_store:
        progress_store[task_id]["status"] = "Cancelling..."
    return {"status": "cancelled"}


@router.get("/products")
async def get_products(
    request: Request,
    page: int = 1,
    search: Optional[str] = None,
    active: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get paginated products with optional filtering.
    
    Args:
        request (Request): FastAPI request object
        page (int): Page number
        search (str, optional): Search term
        active (str, optional): Active filter
        db (Session): Database session
        
    Returns:
        HTMLResponse: Rendered products page
    """
    result = ProductService.get_products_paginated(
        db=db, 
        page=page, 
        search=search, 
        active=active
    )
    
    return templates.TemplateResponse("products.html", {
        "request": request,
        **result,
        "search": search or "",
        "active": active
    })


@router.delete("/products-all")
async def delete_all_products_direct(db: Session = Depends(get_db)):
    """
    Delete all products from database.
    
    Args:
        db (Session): Database session
        
    Returns:
        dict: Deletion result
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        count = db.query(Product).count()
        logger.info(f"Direct delete all products requested - Current count: {count}")
        
        deleted = ProductService.delete_all_products(db)
        
        return {
            "status": "completed", 
            "deleted": deleted, 
            "message": f"Deleted {deleted} products"
        }
    except Exception as e:
        logger.error(f"Error during direct deletion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    """
    Get database status and statistics.
    
    Args:
        db (Session): Database session
        
    Returns:
        dict: Database status information
    """
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.active == True).count()
    inactive_products = total_products - active_products
    
    logger.info(f"Database status - Total: {total_products}, Active: {active_products}, Inactive: {inactive_products}")
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "database_status": "connected"
    }
