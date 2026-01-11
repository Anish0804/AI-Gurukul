from fastmcp import FastMCP
import requests

BASE_API_URL = "http://localhost:8000"

mcp = FastMCP("banking-mcp-tools")

TOOLS = {}   


@mcp.tool()
def get_account_balance(account_id: int) -> dict:
    r = requests.get(f"{BASE_API_URL}/api/accounts/{account_id}/balance")
    r.raise_for_status()
    return r.json()

TOOLS["get_account_balance"] = get_account_balance


@mcp.tool()
def get_transaction_history(account_id: int) -> dict:
    r = requests.get(f"{BASE_API_URL}/api/accounts/{account_id}/transactions")
    r.raise_for_status()
    return r.json()

TOOLS["get_transaction_history"] = get_transaction_history


@mcp.tool()
def get_adhoc_statements(account_id: int) -> dict:
    r = requests.get(
        f"{BASE_API_URL}/api/accounts/{account_id}/statements/adhoc"
    )
    r.raise_for_status()
    return r.json()

TOOLS["get_adhoc_statements"] = get_adhoc_statements


@mcp.tool()
def get_periodic_statements(account_id: int) -> dict:
    r = requests.get(
        f"{BASE_API_URL}/api/accounts/{account_id}/statements/current"
    )
    r.raise_for_status()
    return r.json()

TOOLS["get_periodic_statements"] = get_periodic_statements
