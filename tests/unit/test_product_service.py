"""
Unit tests for ProductService.

This module contains unit tests for the ProductService class,
testing business logic and data processing functions.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.product_service import ProductService
from app.models import Product


class TestProductService:
    """Test cases for ProductService."""
    
    def test_preprocess_dataframe(self):
        """Test dataframe preprocessing."""
        # Create test dataframe with duplicates and mixed case SKUs
        data = {
            'name': ['Product A', 'Product B', 'Product A'],
            'sku': ['SKU-001', 'SKU-002', 'SKU-001'],
            'description': ['Desc A', 'Desc B', 'Desc A Updated']
        }
        df = pd.DataFrame(data)
        
        # Process dataframe
        result = ProductService._preprocess_dataframe(df)
        
        # Assertions
        assert len(result) == 2  # Duplicates removed
        # Check that SKUs are lowercase (order may vary after deduplication)
        skus = set(result['sku'].tolist())
        assert skus == {'sku-001', 'sku-002'}
        # Check that the last duplicate was kept
        sku_001_row = result[result['sku'] == 'sku-001']
        assert sku_001_row['description'].iloc[0] == 'Desc A Updated'
    
    @patch('app.services.product_service.text')
    def test_get_existing_skus(self, mock_text):
        """Test getting existing SKUs from database."""
        # Mock database session and result
        mock_session = Mock(spec=Session)
        mock_result = [('sku-001',), ('sku-002',), ('sku-003',)]
        mock_session.execute.return_value = mock_result
        
        # Call method
        result = ProductService._get_existing_skus(mock_session)
        
        # Assertions
        assert result == {'sku-001', 'sku-002', 'sku-003'}
        mock_session.execute.assert_called_once()
    
    def test_get_products_paginated_no_filters(self):
        """Test getting paginated products without filters."""
        # Mock database session and query
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.count.return_value = 50
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product) for _ in range(20)]
        
        # Call method
        result = ProductService.get_products_paginated(mock_db, page=1, per_page=20)
        
        # Assertions
        assert result['total'] == 50
        assert result['page'] == 1
        assert result['per_page'] == 20
        assert result['total_pages'] == 3
        assert len(result['products']) == 20
    
    def test_get_products_paginated_with_search(self):
        """Test getting paginated products with search filter."""
        # Mock database session and query
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Product) for _ in range(10)]
        
        # Call method
        result = ProductService.get_products_paginated(
            mock_db, page=1, per_page=20, search="test"
        )
        
        # Assertions
        assert result['total'] == 10
        assert len(result['products']) == 10
        mock_query.filter.assert_called_once()
    
    def test_delete_all_products(self):
        """Test deleting all products."""
        # Mock database session and query
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.count.return_value = 100
        mock_query.delete.return_value = 100
        
        # Call method
        result = ProductService.delete_all_products(mock_db)
        
        # Assertions
        assert result == 100
        mock_db.query.assert_called_with(Product)
        mock_query.delete.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.fixture
def sample_dataframe():
    """Fixture providing sample dataframe for tests."""
    return pd.DataFrame({
        'name': ['Product A', 'Product B', 'Product C'],
        'sku': ['SKU-001', 'SKU-002', 'SKU-003'],
        'description': ['Description A', 'Description B', 'Description C']
    })


@pytest.fixture
def mock_db_session():
    """Fixture providing mock database session."""
    return Mock(spec=Session)
