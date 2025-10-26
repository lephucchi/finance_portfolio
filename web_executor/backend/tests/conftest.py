"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch

from app.db import AthenaClient, SupabaseClient
from app.services import (
    MarketService,
    SentimentService,
    MacroService,
    AnalyticsService,
)


@pytest.fixture
def mock_athena_client():
    """Mock Athena client."""
    client = Mock(spec=AthenaClient)
    client.query.return_value = []
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    client = Mock(spec=SupabaseClient)
    client.get_cached_result.return_value = None
    return client


@pytest.fixture
def market_service(mock_athena_client, mock_supabase_client):
    """Market service with mocked dependencies."""
    return MarketService(mock_athena_client, mock_supabase_client)


@pytest.fixture
def sentiment_service(mock_athena_client, mock_supabase_client):
    """Sentiment service with mocked dependencies."""
    return SentimentService(mock_athena_client, mock_supabase_client)


@pytest.fixture
def macro_service(mock_athena_client, mock_supabase_client):
    """Macro service with mocked dependencies."""
    return MacroService(mock_athena_client, mock_supabase_client)


@pytest.fixture
def analytics_service(mock_athena_client, mock_supabase_client):
    """Analytics service with mocked dependencies."""
    return AnalyticsService(mock_athena_client, mock_supabase_client)
