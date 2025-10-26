"""Tests for market service."""

from datetime import date

import pytest


class TestMarketService:
    """Market service tests."""

    def test_get_stock_data(self, market_service, mock_athena_client):
        """Test getting stock data."""
        # Arrange
        mock_athena_client.query.return_value = [
            {
                "symbol": "ACB",
                "data_date": "2025-10-18",
                "close": 25400.0,
            }
        ]

        # Act
        result = market_service.get_stock_data(
            date(2025, 10, 1),
            date(2025, 10, 18),
        )

        # Assert
        assert len(result) == 1
        assert result[0]["symbol"] == "ACB"
        mock_athena_client.query.assert_called_once()

    def test_get_technical_indicators(self, market_service, mock_athena_client):
        """Test getting technical indicators."""
        # Arrange
        mock_athena_client.query.return_value = [
            {
                "symbol": "ACB",
                "rsi_14": 65.2,
                "ma_20": 25320.0,
            }
        ]

        # Act
        result = market_service.get_technical_indicators(
            "ACB",
            date(2025, 10, 1),
            date(2025, 10, 18),
        )

        # Assert
        assert len(result) == 1
        mock_athena_client.query.assert_called_once()
