"""
Product service containing business logic for product operations.

This module handles product import, CRUD operations, and related business logic.
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Set
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Product, SessionLocal

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product-related operations."""
    
    @staticmethod
    def import_products_from_csv(
        file_path: str, 
        task_id: str, 
        progress_store: Dict,
        cancel_flags: Dict
    ) -> Dict:
        """
        Import products from CSV file with progress tracking.
        
        Args:
            file_path (str): Path to the CSV file
            task_id (str): Unique task identifier for progress tracking
            progress_store (Dict): Shared progress storage
            cancel_flags (Dict): Shared cancellation flags
            
        Returns:
            Dict: Import result with status and statistics
        """
        db_session = SessionLocal()
        
        try:
            # Load and validate CSV
            progress_store[task_id] = {
                "progress": 5, 
                "status": "Loading CSV...", 
                "completed": False
            }
            
            df = pd.read_csv(file_path)
            total_rows = len(df)
            logger.info(f"Loaded CSV with {total_rows} rows")
            
            # Data preprocessing
            progress_store[task_id] = {
                "progress": 10, 
                "status": "Preprocessing data...", 
                "completed": False
            }
            
            df = ProductService._preprocess_dataframe(df)
            
            # Get existing SKUs for deduplication
            existing_skus = ProductService._get_existing_skus(db_session)
            
            # Process in batches
            imported = ProductService._process_batches(
                df, db_session, task_id, progress_store, 
                cancel_flags, existing_skus
            )
            
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
            
            progress_store[task_id] = {
                "progress": 100,
                "status": f"Completed! {imported} products imported",
                "completed": True,
                "imported": imported
            }
            
            logger.info(f"Import completed: {imported} new products imported")
            return {
                "status": "completed", 
                "imported": imported, 
                "total_processed": total_rows
            }
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            progress_store[task_id] = {
                "progress": 0,
                "status": f"Error: {str(e)}",
                "completed": True,
                "error": True
            }
            db_session.rollback()
            raise
        finally:
            db_session.close()
    
    @staticmethod
    def _preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the dataframe for import.
        
        Args:
            df (pd.DataFrame): Raw dataframe from CSV
            
        Returns:
            pd.DataFrame: Preprocessed dataframe
        """
        # Remove duplicates and normalize SKUs
        df = df.drop_duplicates(subset=['sku'], keep='last').copy()
        df['sku'] = df['sku'].str.strip().str.lower()
        return df
    
    @staticmethod
    def _get_existing_skus(db_session: Session) -> Set[str]:
        """
        Get all existing SKUs from database.
        
        Args:
            db_session (Session): Database session
            
        Returns:
            Set[str]: Set of existing SKUs
        """
        result = db_session.execute(text("SELECT LOWER(sku) FROM products"))
        return {row[0] for row in result}
    
    @staticmethod
    def _process_batches(
        df: pd.DataFrame,
        db_session: Session,
        task_id: str,
        progress_store: Dict,
        cancel_flags: Dict,
        existing_skus: Set[str]
    ) -> int:
        """
        Process dataframe in batches for efficient import.
        
        Args:
            df (pd.DataFrame): Preprocessed dataframe
            db_session (Session): Database session
            task_id (str): Task identifier
            progress_store (Dict): Progress storage
            cancel_flags (Dict): Cancellation flags
            existing_skus (Set[str]): Existing SKUs to avoid duplicates
            
        Returns:
            int: Number of products imported
        """
        imported = 0
        batch_size = 5000
        
        for i in range(0, len(df), batch_size):
            # Check for cancellation
            if cancel_flags.get(task_id, False):
                progress_store[task_id] = {
                    "progress": 0,
                    "status": "Cancelled by user",
                    "completed": True,
                    "cancelled": True
                }
                logger.info(f"Import cancelled at {i}/{len(df)} records")
                return imported
            
            batch = df.iloc[i:i+batch_size]
            new_products = []
            
            # Prepare batch data
            for _, row in batch.iterrows():
                sku = str(row['sku']).lower()
                if sku not in existing_skus:
                    new_products.append({
                        'name': str(row['name']),
                        'sku': sku,
                        'description': str(row.get('description', '')),
                        'active': True
                    })
                    existing_skus.add(sku)
                    imported += 1
            
            # Bulk insert
            if new_products:
                db_session.execute(text("""
                    INSERT INTO products (name, sku, description, active, created_at) 
                    VALUES (:name, :sku, :description, :active, datetime('now'))
                """), new_products)
            
            db_session.commit()
            
            # Update progress
            progress = min(95, int((i + batch_size) / len(df) * 85) + 10)
            progress_store[task_id] = {
                "progress": progress,
                "status": f"Processing... {i + batch_size}/{len(df)} ({imported} imported)",
                "completed": False
            }
            
            logger.info(f"Progress: {progress}% ({i + batch_size}/{len(df)} processed, {imported} imported)")
        
        return imported
    
    @staticmethod
    def get_products_paginated(
        db: Session,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        active: Optional[str] = None
    ) -> Dict:
        """
        Get paginated products with optional filtering.
        
        Args:
            db (Session): Database session
            page (int): Page number
            per_page (int): Items per page
            search (str, optional): Search term
            active (str, optional): Active filter
            
        Returns:
            Dict: Paginated products data
        """
        query = db.query(Product)
        
        # Apply filters
        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) |
                (Product.sku.ilike(f"%{search}%")) |
                (Product.description.ilike(f"%{search}%"))
            )
        
        if active and active.lower() not in ['none', '']:
            active_bool = active.lower() == 'true'
            query = query.filter(Product.active == active_bool)
        
        total = query.count()
        products = query.offset((page-1) * per_page).limit(per_page).all()
        
        return {
            "products": products,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def create_product(
        db: Session,
        name: str,
        sku: str,
        description: str = "",
        active: bool = True
    ) -> Product:
        """
        Create a new product.
        
        Args:
            db (Session): Database session
            name (str): Product name
            sku (str): Product SKU
            description (str): Product description
            active (bool): Product active status
            
        Returns:
            Product: Created product
        """
        # Check if SKU already exists
        existing = db.query(Product).filter(Product.sku.ilike(sku)).first()
        if existing:
            raise ValueError(f"Product with SKU '{sku}' already exists")
        
        product = Product(
            name=name,
            sku=sku.lower(),
            description=description,
            active=active
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        name: str = None,
        sku: str = None,
        description: str = None,
        active: bool = None
    ) -> Optional[Product]:
        """
        Update an existing product.
        
        Args:
            db (Session): Database session
            product_id (int): Product ID
            name (str, optional): New product name
            sku (str, optional): New product SKU
            description (str, optional): New product description
            active (bool, optional): New product active status
            
        Returns:
            Product: Updated product or None if not found
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        # Check SKU uniqueness if updating SKU
        if sku and sku.lower() != product.sku:
            existing = db.query(Product).filter(
                Product.sku.ilike(sku),
                Product.id != product_id
            ).first()
            if existing:
                raise ValueError(f"Product with SKU '{sku}' already exists")
        
        # Update fields
        if name is not None:
            product.name = name
        if sku is not None:
            product.sku = sku.lower()
        if description is not None:
            product.description = description
        if active is not None:
            product.active = active
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        Delete a product.
        
        Args:
            db (Session): Database session
            product_id (int): Product ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True
    
    @staticmethod
    def delete_all_products(db: Session) -> int:
        """
        Delete all products from database.
        
        Args:
            db (Session): Database session
            
        Returns:
            int: Number of products deleted
        """
        count = db.query(Product).count()
        db.query(Product).delete()
        db.commit()
        logger.info(f"Deleted {count} products from database")
        return count
