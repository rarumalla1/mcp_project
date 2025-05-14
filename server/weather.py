import logging


from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


   # Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("weather")

# Initialize FastMCP server
mcp = FastMCP("weather")
#https://api.weather.gov/alerts/active/area/ga
# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url:str) -> dict[str,Any] | None :
    """Make a request to the NWS API and return the response"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        mcp.logger.error(f"Error fetching data from NWS: {e}")
        return None
    

def format_alert(feature:dict) -> str:
    """Format an alert feature into readable string"""
    props = feature["properties"]
    return f"""
    Event: {props.get("event", "Unknown")}
    Area: {props.get("areaDesc", "Unknown")}
    Severity: {props.get("severity", "Unknown")}
    Description: {props.get("description", "No description available")}
    Instructions: {props.get("instruction", "No specific instructions available")}
    """
    

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific state
    Args:
        state (str): The two-letter state code (e.g., "CA", "NY")
    Returns:
        str: A formatted string containing all active alerts for the state
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration for the weather app"""
    return "App config here"


@mcp.resource("echo://{message}")
def echo(message:str) -> str:
    """Echo a message back to the client"""
    return f"Echo: {message}"
