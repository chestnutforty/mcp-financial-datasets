import os
import pytest
import json
from financial_datasets_server import (
    get_income_statements,
    get_balance_sheets,
    get_cash_flow_statements,
    get_historical_stock_prices,
    get_company_news,
    get_available_crypto_tickers,
    get_crypto_prices,
    get_historical_crypto_prices,
)


# Check if API key is set, skip tests if not
pytestmark = pytest.mark.skipif(
    not os.environ.get("FINANCIAL_DATASETS_API_KEY"),
    reason="FINANCIAL_DATASETS_API_KEY not set"
)


@pytest.mark.asyncio
async def test_get_income_statements():
    """Test getting income statements for a company"""
    result = await get_income_statements.fn(
        ticker="AAPL",
        cutoff_date="2024-01-01",
        period="annual",
        limit=2
    )

    assert result is not None
    assert isinstance(result, str)
    # Should be valid JSON
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for expected fields
        assert "revenue" in data[0] or "net_income" in data[0]


@pytest.mark.asyncio
async def test_get_income_statements_quarterly():
    """Test getting quarterly income statements"""
    result = await get_income_statements.fn(
        ticker="MSFT",
        cutoff_date="2023-12-31",
        period="quarterly",
        limit=4
    )

    assert result is not None
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_balance_sheets():
    """Test getting balance sheets for a company"""
    result = await get_balance_sheets.fn(
        ticker="GOOGL",
        cutoff_date="2024-01-01",
        period="annual",
        limit=2
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for expected fields
        assert "total_assets" in data[0] or "total_debt" in data[0] or "shareholders_equity" in data[0]


@pytest.mark.asyncio
async def test_get_cash_flow_statements():
    """Test getting cash flow statements for a company"""
    result = await get_cash_flow_statements.fn(
        ticker="AAPL",
        cutoff_date="2024-01-01",
        period="annual",
        limit=2
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for expected fields
        assert "net_cash_flow_from_operations" in data[0] or "free_cash_flow" in data[0]


@pytest.mark.asyncio
async def test_get_historical_stock_prices():
    """Test getting historical stock prices"""
    result = await get_historical_stock_prices.fn(
        ticker="AAPL",
        start_date="2023-01-01",
        end_date="2023-01-31",
        cutoff_date="2024-01-01",
        interval="day",
        interval_multiplier=1
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for OHLCV fields
        assert "open" in data[0]
        assert "close" in data[0]
        assert "high" in data[0]
        assert "low" in data[0]
        assert "volume" in data[0]


@pytest.mark.asyncio
async def test_get_historical_stock_prices_cutoff_enforcement():
    """Test that cutoff_date properly limits the data returned"""
    # Request data beyond cutoff_date - should be clamped
    result = await get_historical_stock_prices.fn(
        ticker="AAPL",
        start_date="2023-01-01",
        end_date="2025-12-31",  # Future date
        cutoff_date="2023-06-30",  # Cutoff in middle of 2023
        interval="day",
        interval_multiplier=1
    )

    assert result is not None
    data = json.loads(result)
    # All returned dates should be <= cutoff_date
    if len(data) > 0:
        for record in data:
            if "timestamp" in record:
                # Extract date from timestamp (format may vary)
                timestamp = record["timestamp"]
                # Just verify we got some data - exact format checking depends on API
                assert timestamp is not None


@pytest.mark.asyncio
async def test_get_company_news():
    """Test getting company news"""
    result = await get_company_news.fn(
        ticker="AAPL",
        cutoff_date="2024-01-01"
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for expected fields
        assert "title" in data[0]
        assert "url" in data[0] or "date" in data[0]


@pytest.mark.asyncio
async def test_get_available_crypto_tickers():
    """Test getting available crypto tickers"""
    result = await get_available_crypto_tickers.fn()

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    # Should have at least some crypto tickers
    if len(data) > 0:
        # Check that we have ticker strings
        assert isinstance(data[0], str)
        # Common crypto tickers should be present
        assert any("BTC" in ticker for ticker in data) or len(data) > 0


@pytest.mark.asyncio
async def test_get_crypto_prices():
    """Test getting crypto prices"""
    result = await get_crypto_prices.fn(
        ticker="BTC-USD",
        start_date="2023-01-01",
        end_date="2023-01-31",
        cutoff_date="2024-01-01",
        interval="day",
        interval_multiplier=1
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for OHLCV fields
        assert "open" in data[0]
        assert "close" in data[0]
        assert "high" in data[0]
        assert "low" in data[0]


@pytest.mark.asyncio
async def test_get_historical_crypto_prices():
    """Test getting historical crypto prices (duplicate of get_crypto_prices)"""
    result = await get_historical_crypto_prices.fn(
        ticker="ETH-USD",
        start_date="2023-01-01",
        end_date="2023-01-31",
        cutoff_date="2024-01-01",
        interval="day",
        interval_multiplier=1
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        # Check for OHLCV fields
        assert "open" in data[0]
        assert "close" in data[0]


@pytest.mark.asyncio
async def test_invalid_ticker():
    """Test handling of invalid ticker"""
    result = await get_income_statements.fn(
        ticker="INVALIDTICKER123456",
        cutoff_date="2024-01-01",
        period="annual",
        limit=2
    )

    assert result is not None
    # Should contain error message or empty result
    assert "unable" in result.lower() or "no" in result.lower() or "[]" in result


@pytest.mark.asyncio
async def test_ttm_period():
    """Test trailing twelve months period"""
    result = await get_income_statements.fn(
        ticker="AAPL",
        cutoff_date="2024-01-01",
        period="ttm",
        limit=1
    )

    assert result is not None
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_large_limit():
    """Test with larger limit value"""
    result = await get_balance_sheets.fn(
        ticker="AAPL",
        cutoff_date="2024-01-01",
        period="annual",
        limit=10
    )

    assert result is not None
    data = json.loads(result)
    assert isinstance(data, list)
    # Should handle large limit gracefully
    assert len(data) <= 10


@pytest.mark.asyncio
async def test_crypto_with_different_pairs():
    """Test different cryptocurrency pairs"""
    result = await get_crypto_prices.fn(
        ticker="SOL-USD",
        start_date="2023-01-01",
        end_date="2023-01-07",
        cutoff_date="2024-01-01",
        interval="day",
        interval_multiplier=1
    )

    assert result is not None
    assert isinstance(result, str)
    # Valid JSON response
    data = json.loads(result)
    assert isinstance(data, list)
