"""
MCP SERVER IMPLEMENTATION FROM FINANCIAL DATASETS API (Modified from https://github.com/financial-datasets/mcp-server)
"""


import json
import os
import httpx
import logging
from datetime import datetime
from fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("financial_datasets")

# Constants
FINANCIAL_DATASETS_API_BASE = "https://api.financialdatasets.ai"


# Helper function to make API requests
async def make_request(url: str) -> dict[str, any] | None:
    """Make a request to the Financial Datasets API with proper error handling."""
    # Load environment variables from .env file
    load_dotenv()
    
    headers = {}
    if api_key := os.environ.get("FINANCIAL_DATASETS_API_KEY"):
        headers["X-API-KEY"] = api_key

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"Error": str(e)}


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_income_statements(
    ticker: str,
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d"),
    period: str = "annual",
    limit: int = 4,
) -> str:
    """Get historical income statements for a company.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL for Apple, MSFT for Microsoft, GOOGL for Google)
        period: Time period - "annual" for yearly data, "quarterly" for Q1/Q2/Q3/Q4, "ttm" for trailing twelve months
        limit: Number of historical periods to return (default: 4, e.g. last 4 years or quarters)

    Returns:
        JSON array of income statements with fields like revenue, net_income, operating_income, earnings_per_share, etc.
    """
    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/financials/income-statements/?ticker={ticker}&period={period}&limit={limit}&report_period_lte={cutoff_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch income statements or no income statements found."

    # Extract the income statements
    income_statements = data.get("income_statements", [])

    # Check if income statements are found
    if not income_statements:
        return "Unable to fetch income statements or no income statements found."

    # Stringify the income statements
    return json.dumps(income_statements, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_balance_sheets(
    ticker: str,
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d"),
    period: str = "annual",
    limit: int = 4,
) -> str:
    """Get historical balance sheets for a company.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL for Apple, MSFT for Microsoft, GOOGL for Google)
        period: Time period - "annual" for yearly data, "quarterly" for Q1/Q2/Q3/Q4, "ttm" for trailing twelve months
        limit: Number of historical periods to return (default: 4, e.g. last 4 years or quarters)

    Returns:
        JSON array of balance sheets with fields like total_assets, cash_and_equivalents, total_debt, shareholders_equity, etc.
    """
    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/financials/balance-sheets/?ticker={ticker}&period={period}&limit={limit}&report_period_lte={cutoff_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch balance sheets or no balance sheets found."

    # Extract the balance sheets
    balance_sheets = data.get("balance_sheets", [])

    # Check if balance sheets are found
    if not balance_sheets:
        return "Unable to fetch balance sheets or no balance sheets found."

    # Stringify the balance sheets
    return json.dumps(balance_sheets, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_cash_flow_statements(
    ticker: str,
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d"),
    period: str = "annual",
    limit: int = 4,
) -> str:
    """Get historical cash flow statements for a company.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL for Apple, MSFT for Microsoft, GOOGL for Google)
        period: Time period - "annual" for yearly data, "quarterly" for Q1/Q2/Q3/Q4, "ttm" for trailing twelve months
        limit: Number of historical periods to return (default: 4, e.g. last 4 years or quarters)

    Returns:
        JSON array of cash flow statements with fields like net_cash_flow_from_operations, capital_expenditure, free_cash_flow, etc.
    """
    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/financials/cash-flow-statements/?ticker={ticker}&period={period}&limit={limit}&report_period_lte={cutoff_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch cash flow statements or no cash flow statements found."

    # Extract the cash flow statements
    cash_flow_statements = data.get("cash_flow_statements", [])

    # Check if cash flow statements are found
    if not cash_flow_statements:
        return "Unable to fetch cash flow statements or no cash flow statements found."

    # Stringify the cash flow statements
    return json.dumps(cash_flow_statements, indent=2)


# DISABLED FOR BACKTESTING: This tool returns the current/latest stock price, which would always
# leak future information relative to any historical cutoff_date. There is no way to make this
# endpoint compliant for backtesting purposes.
#
# ALTERNATIVE: Use get_historical_stock_prices with start_date=cutoff_date and end_date=cutoff_date
# to get the price at a specific historical date.
#
# @mcp.tool(
#     exclude_args=["cutoff_date"]
# )
# async def get_current_stock_price(ticker: str) -> str:
#     """Get the current / latest price of a company.
#
#     Args:
#         ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
#     """
#     # Fetch data from the API
#     url = f"{FINANCIAL_DATASETS_API_BASE}/prices/snapshot/?ticker={ticker}"
#     data = await make_request(url)
#
#     # Check if data is found
#     if not data:
#         return "Unable to fetch current price or no current price found."
#
#     # Extract the current price
#     snapshot = data.get("snapshot", {})
#
#     # Check if current price is found
#     if not snapshot:
#         return "Unable to fetch current price or no current price found."
#
#     # Stringify the current price
#     return json.dumps(snapshot, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_historical_stock_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d"),
    interval: str = "day",
    interval_multiplier: int = 1,
) -> str:
    """Get historical stock price data including open, close, high, low, and volume for a date range.

    Returns OHLCV (Open, High, Low, Close, Volume) price data at specified time intervals. Use this
    to analyze price trends, calculate returns, identify support/resistance levels, or build technical
    indicators. Perfect for backtesting strategies or understanding price movements over time.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL for Apple, TSLA for Tesla, NVDA for Nvidia)
        start_date: Start date in YYYY-MM-DD format (e.g. 2020-01-01)
        end_date: End date in YYYY-MM-DD format (e.g. 2020-12-31)
        interval: Time interval - "minute", "hour", "day", "week", or "month"
        interval_multiplier: Multiply the interval (e.g. 5 with "minute" = every 5 minutes, 2 with "day" = every 2 days)

    Returns:
        JSON array of price records with open, close, high, low, volume, and timestamp fields.
    """
    # Clamp end_date to cutoff_date if it exceeds it
    if end_date > cutoff_date:
        end_date = cutoff_date

    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/prices/?ticker={ticker}&interval={interval}&interval_multiplier={interval_multiplier}&start_date={start_date}&end_date={end_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch prices or no prices found."

    # Extract the prices
    prices = data.get("prices", [])

    # Check if prices are found
    if not prices:
        return "Unable to fetch prices or no prices found."

    # Stringify the prices
    return json.dumps(prices, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_company_news(ticker: str, 
                           cutoff_date: str = datetime.now().strftime("%Y-%m-%d")) -> str:
    """Get recent news articles about a specific company from major financial news sources.

    Returns up to 20 recent news articles with titles, URLs, publication dates, authors, and sentiment.
    Use this to understand recent events, announcements, product launches, earnings reports, or market
    sentiment that might affect the company's stock price or business performance.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL for Apple, TSLA for Tesla, NVDA for Nvidia)

    Returns:
        JSON array of news articles with title, url, date, author, source, and sentiment fields.
    """

    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/news/?limit=20&end_date={cutoff_date}&ticker={ticker}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch news or no news found."

    # Extract the news
    news = data.get("news", [])

    # Check if news are found
    if not news:
        return "Unable to fetch news or no news found."
    return json.dumps(news, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_available_crypto_tickers(
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d")
) -> str:
    """Get a list of all available cryptocurrency tickers that can be queried for price data.

    Returns ticker symbols for major cryptocurrencies like BTC-USD (Bitcoin), ETH-USD (Ethereum),
    and many others. Use this to discover what crypto assets are available before requesting their
    price history or current data.

    Returns:
        JSON array of available cryptocurrency ticker symbols (e.g. ["BTC-USD", "ETH-USD", "SOL-USD"]).
    """
    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/crypto/prices/tickers"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch available crypto tickers or no available crypto tickers found."

    # Extract the available crypto tickers
    tickers = data.get("tickers", [])

    # Stringify the available crypto tickers
    return json.dumps(tickers, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_crypto_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d"),
    interval: str = "day",
    interval_multiplier: int = 1,
) -> str:
    """Get historical cryptocurrency price data including open, close, high, low, and volume.

    Returns OHLCV (Open, High, Low, Close, Volume) price data for cryptocurrencies at specified time
    intervals. Use this to analyze crypto price trends, volatility, trading volumes, or build technical
    analysis. Covers major cryptocurrencies like Bitcoin, Ethereum, and many altcoins.

    Args:
        ticker: Cryptocurrency ticker symbol (e.g. BTC-USD for Bitcoin, ETH-USD for Ethereum, SOL-USD for Solana)
        start_date: Start date in YYYY-MM-DD format (e.g. 2020-01-01)
        end_date: End date in YYYY-MM-DD format (e.g. 2020-12-31)
        interval: Time interval - "minute", "hour", "day", "week", or "month"
        interval_multiplier: Multiply the interval (e.g. 5 with "minute" = every 5 minutes, 2 with "day" = every 2 days)

    Returns:
        JSON array of price records with open, close, high, low, volume, and timestamp fields.
    """
    # Clamp end_date to cutoff_date if it exceeds it
    if end_date > cutoff_date:
        end_date = cutoff_date

    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/crypto/prices/?ticker={ticker}&interval={interval}&interval_multiplier={interval_multiplier}&start_date={start_date}&end_date={end_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch prices or no prices found."

    # Extract the prices
    prices = data.get("prices", [])

    # Check if prices are found
    if not prices:
        return "Unable to fetch prices or no prices found."

    # Stringify the prices
    return json.dumps(prices, indent=2)


@mcp.tool(
    exclude_args=["cutoff_date"]
)
async def get_historical_crypto_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    cutoff_date: str = datetime.now().strftime("%Y-%m-%d"),
    interval: str = "day",
    interval_multiplier: int = 1,
) -> str:
    """Get historical cryptocurrency price data including open, close, high, low, and volume.

    Returns OHLCV (Open, High, Low, Close, Volume) price data for cryptocurrencies at specified time
    intervals. Identical to get_crypto_prices - use either one. Covers major cryptocurrencies sourced
    from exchanges like Coinbase, Kraken, and Bitfinex. Use get_available_crypto_tickers to see all
    available cryptocurrency tickers before querying.

    Args:
        ticker: Cryptocurrency ticker symbol (e.g. BTC-USD for Bitcoin, ETH-USD for Ethereum, SOL-USD for Solana)
        start_date: Start date in YYYY-MM-DD format (e.g. 2020-01-01)
        end_date: End date in YYYY-MM-DD format (e.g. 2020-12-31)
        interval: Time interval - "minute", "hour", "day", "week", or "month"
        interval_multiplier: Multiply the interval (e.g. 5 with "minute" = every 5 minutes, 2 with "day" = every 2 days)

    Returns:
        JSON array of price records with open, close, high, low, volume, and timestamp fields.
    """
    # Clamp end_date to cutoff_date if it exceeds it
    if end_date > cutoff_date:
        end_date = cutoff_date

    # Fetch data from the API
    url = f"{FINANCIAL_DATASETS_API_BASE}/crypto/prices/?ticker={ticker}&interval={interval}&interval_multiplier={interval_multiplier}&start_date={start_date}&end_date={end_date}"
    data = await make_request(url)

    # Check if data is found
    if not data:
        return "Unable to fetch prices or no prices found."

    # Extract the prices
    prices = data.get("prices", [])

    # Check if prices are found
    if not prices:
        return "Unable to fetch prices or no prices found."

    # Stringify the prices
    return json.dumps(prices, indent=2)


# DISABLED FOR BACKTESTING: This tool returns the current/latest crypto price, which would always
# leak future information relative to any historical cutoff_date. There is no way to make this
# endpoint compliant for backtesting purposes.
#
# ALTERNATIVE: Use get_historical_crypto_prices or get_crypto_prices with start_date=cutoff_date
# and end_date=cutoff_date to get the price at a specific historical date.
#
# @mcp.tool(
#     exclude_args=["cutoff_date"]
# )
# async def get_current_crypto_price(ticker: str) -> str:
#     """Get the current / latest price of a crypto currency.
#
#     Args:
#         ticker: Ticker symbol of the crypto currency (e.g. BTC-USD). The list of available crypto tickers can be retrieved via the get_available_crypto_tickers tool.
#     """
#     # Fetch data from the API
#     url = f"{FINANCIAL_DATASETS_API_BASE}/crypto/prices/snapshot/?ticker={ticker}"
#     data = await make_request(url)
#
#     # Check if data is found
#     if not data:
#         return "Unable to fetch current price or no current price found."
#
#     # Extract the current price
#     snapshot = data.get("snapshot", {})
#
#     # Check if current price is found
#     if not snapshot:
#         return "Unable to fetch current price or no current price found."
#
#     # Stringify the current price
#     return json.dumps(snapshot, indent=2)


# DISABLED FOR BACKTESTING: This tool cannot guarantee backtesting validity because the API
# only returns 'report_date' (the fiscal period end date), not the 'filing_date' (when the
# filing was actually made public with the SEC).
#
# ISSUE: A 10-K for fiscal year ending Dec 31, 2023 (report_date=2023-12-31) might not be
# filed until March 2024. If cutoff_date=2024-02-01, we would incorrectly include a filing
# that wasn't yet public, leaking future information.
#
# Without access to the actual filing date (when made public), we cannot reliably filter
# SEC filings for backtesting purposes. The report_date is not sufficient.
#
# POTENTIAL SOLUTION: If the API supports filing_date filtering, this could be re-enabled.
# The filing_date would need to be <= cutoff_date to ensure the filing was publicly available.
#
# @mcp.tool(
    # exclude_args=["cutoff_date"]
# )
# async def get_sec_filings(
#     ticker: str,
#     cutoff_date: str,
#     limit: int = 10,
#     filing_type: str | None = None,
# ) -> str:
#     """Get all SEC filings for a company.
#
#     Args:
#         ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)
#         cutoff_date: Cutoff date in YYYY-MM-DD format. Only returns filings made public before this date.
#         limit: Number of SEC filings to return (default: 10)
#         filing_type: Type of SEC filing (e.g. 10-K, 10-Q, 8-K)
#     """
#     # Fetch data from the API
#     url = f"{FINANCIAL_DATASETS_API_BASE}/filings/?ticker={ticker}&limit={limit}"
#     if filing_type:
#         url += f"&filing_type={filing_type}"
#
#     # Call the API
#     data = await make_request(url)
#
#     # Extract the SEC filings
#     filings = data.get("filings", [])
#
#     # Check if SEC filings are found
#     if not filings:
#         return f"Unable to fetch SEC filings or no SEC filings found."
#
#     # Stringify the SEC filings
#     return json.dumps(filings, indent=2)

if __name__ == "__main__":
    # Log server startup
    logger.info("Starting Financial Datasets MCP Server...")

    # Initialize and run the server
    mcp.run(transport="stdio")

    # This line won't be reached during normal operation
    logger.info("Server stopped")