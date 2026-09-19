import yfinance as yf
import requests
import pandas as pd
from io import StringIO
import databricks.sql
import os
from databricks.sdk.core import Config
from mcp.server.fastmcp import FastMCP

# create MCP server
mcp = FastMCP("custom MCP server on databricks apps")

# Tool 1
@mcp.tool(
    name = "get_stock_info",
    description = "Fetch the stock information of the given symbol"
)
def get_stock_info(symbol: str) -> str | None:
    """Fetch market cap, current price, and 52-week range for NSE stock."""
    try:
        info = yf.Ticker(f"{symbol}.NS").fast_info
        return (
            f"\nDetails for {symbol}.NS:\n"
            f"market_cap = {info['marketCap']}\n"
            f"current_price = {info['last_price']} INR\n"
            f"year_low = {info['year_low']} INR\n"
            f"year_high = {info['year_high']} INR\n"
        )
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

# Tool 2
@mcp.tool(
    name="run_query_on_databricks",
    description="Gets the SQL query and execute the query on databricks SQL warehouse"
)
def run_query_on_databricks(sql_query: str):
    """
    Executes a SQL query on a Databricks SQL Warehouse and returns the results as a pandas DataFrame.
    """
    cfg = Config()
    warehouse_id = os.getenv("WAREHOUSE_ID")
    host = cfg.host
    http_path = f"/sql/1.0/warehouses/{warehouse_id}"
    if not all([host, http_path]):
        raise ValueError("Missing required Databricks connection environment variables.")

    with databricks.sql.connect(server_hostname=host, http_path=http_path, credentials_provider=lambda: cfg.authenticate) as conn, conn.cursor() as cur:
        cur.execute(sql_query)
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=[c[0] for c in cur.description])

# Run the MCP server
if __name__ == "__main__":
    mcp.run()