"""
Database models and configuration for the Product Importer application.

This module contains SQLAlchemy models for products and webhooks,
along with database session management.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./products.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    """
    Product model representing a product in the database.
    
    Attributes:
        id (int): Primary key
        name (str): Product name
        sku (str): Stock Keeping Unit (unique identifier)
        description (str): Product description
        active (bool): Whether the product is active
        created_at (datetime): When the product was created
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"


class Webhook(Base):
    """
    Webhook model for storing webhook configurations.
    
    Attributes:
        id (int): Primary key
        url (str): Webhook URL endpoint
        event_type (str): Type of event that triggers the webhook
        enabled (bool): Whether the webhook is enabled
        created_at (datetime): When the webhook was created
    """
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Webhook(id={self.id}, url='{self.url}', event='{self.event_type}')>"


def get_db():
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
Base.metadata.create_all(bind=engine)
