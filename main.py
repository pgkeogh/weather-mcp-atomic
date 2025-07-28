# main.py - Atomic MCP Server
"""
Atomic Weather MCP Server
Provides granular, composable weather tools for AI agents.
"""
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Service imports
from services.key_vault_service import KeyVaultService

# Atomic tool imports  
from atomic_tools.infrastructure import InfrastructureTools
from atomic_tools.http_api import HTTPAPITools
from atomic_tools.ai_processing import AIProcessingTools
from atomic_tools.weather_domain import WeatherDomainTools

# Configuration
from config.settings import Settings

# Set up logging to stderr (MCP requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather-atomic-server")

# Initialize services with dependency injection
logger.info("Initializing atomic MCP server...")
key_vault_service = KeyVaultService()

# Initialize atomic tool classes in dependency order
infrastructure_tools = InfrastructureTools(key_vault_service)
http_tools = HTTPAPITools()
ai_tools = AIProcessingTools(key_vault_service, http_tools)
weather_tools = WeatherDomainTools()

logger.info("Atomic tools initialized successfully")

# =============================================================================
# INFRASTRUCTURE ATOMIC TOOLS
# =============================================================================

@mcp.tool()
async def get_secret(secret_name: str, vault_name: Optional[str] = None) -> str:
    """
    Retrieve any secret from Azure Key Vault.
    
    Args:
        secret_name: Name of the secret to retrieve
        vault_name: Optional vault name (uses default if not provided)
    
    Returns:
        Secret value as string
    """
    try:
        return await infrastructure_tools.get_secret(secret_name, vault_name)
    except Exception as e:
        logger.error("get_secret failed: %s", e)
        raise

@mcp.tool()
async def cache_data(key: str, data: Dict[str, Any], ttl_seconds: int = 300) -> bool:
    """
    Cache data with expiration for performance optimization.
    
    Args:
        key: Cache key identifier
        data: Data to cache (JSON serializable)
        ttl_seconds: Time to live in seconds
    
    Returns:
        True if cached successfully
    """
    try:
        return await infrastructure_tools.cache_data(key, data, ttl_seconds)
    except Exception as e:
        logger.error("cache_data failed: %s", e)
        return False

@mcp.tool()
async def get_cached_data(key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached data if available and not expired.
    
    Args:
        key: Cache key identifier
    
    Returns:
        Cached data or None if not found/expired
    """
    try:
        return await infrastructure_tools.get_cached_data(key)
    except Exception as e:
        logger.error("get_cached_data failed: %s", e)
        return None

@mcp.tool()
async def clear_cache(pattern: Optional[str] = None) -> int:
    """
    Clear cache entries, optionally by pattern.
    
    Args:
        pattern: Optional pattern to match keys
    
    Returns:
        Number of entries cleared
    """
    try:
        return await infrastructure_tools.clear_cache(pattern)
    except Exception as e:
        logger.error("clear_cache failed: %s", e)
        return 0

# =============================================================================
# HTTP & API ATOMIC TOOLS
# =============================================================================

@mcp.tool()
async def http_request(
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Make HTTP request with retry logic and error handling.
    
    Args:
        url: Target URL
        method: HTTP method (GET, POST, etc.)
        params: Query parameters or request body
        headers: HTTP headers
        timeout: Request timeout in seconds
    
    Returns:
        {"status": int, "data": dict, "headers": dict}
    """
    try:
        return await http_tools.http_request(url, method, params, headers, timeout)
    except Exception as e:
        logger.error("http_request failed: %s", e)
        raise

@mcp.tool()
async def build_api_url(
    base_url: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build properly formatted API URL with parameters.
    
    Args:
        base_url: API base URL
        endpoint: API endpoint path
        params: URL parameters to append
    
    Returns:
        Complete formatted URL
    """
    try:
        return await http_tools.build_api_url(base_url, endpoint, params)
    except Exception as e:
        logger.error("build_api_url failed: %s", e)
        raise

@mcp.tool()
async def validate_api_response(
    response_data: Dict[str, Any],
    required_fields: List[str],
    response_type: str = "json"
) -> Dict[str, Any]:
    """
    Validate API response structure and required fields.
    
    Args:
        response_data: Response data to validate
        required_fields: List of required field names
        response_type: Expected response type
    
    Returns:
        {"valid": bool, "missing_fields": list, "errors": list}
    """
    try:
        return await http_tools.validate_api_response(response_data, required_fields, response_type)
    except Exception as e:
        logger.error("validate_api_response failed: %s", e)
        return {"valid": False, "missing_fields": [], "errors": [str(e)]}

# =============================================================================
# AI & PROCESSING ATOMIC TOOLS
# =============================================================================

@mcp.tool()
async def ai_completion(
    prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> str:
    """
    Generate AI completion for any prompt.
    
    Args:
        prompt: Input prompt for AI
        model: OpenAI model to use
        max_tokens: Maximum response tokens
        temperature: Response creativity (0.0-1.0)
    
    Returns:
        AI-generated text response
    """
    try:
        return await ai_tools.ai_completion(prompt, model, max_tokens, temperature)
    except Exception as e:
        logger.error("ai_completion failed: %s", e)
        raise

@mcp.tool()
async def format_data(
    data: Dict[str, Any],
    format_type: str,
    template: Optional[str] = None
) -> str:
    """
    Format data using specified formatter.
    
    Args:
        data: Input data to format
        format_type: Format type (json, table, summary, detailed, weather_current, weather_forecast)
        template: Optional custom template
    
    Returns:
        Formatted string output
    """
    try:
        return await ai_tools.format_data(data, format_type, template)
    except Exception as e:
        logger.error("format_data failed: %s", e)
        return f"Formatting error: {str(e)}"

@mcp.tool()
async def extract_data_fields(
    source_data: Dict[str, Any],
    field_mapping: Dict[str, str]
) -> Dict[str, Any]:
    """
    Extract and map specific fields from complex data structures.
    
    Args:
        source_data: Source data structure
        field_mapping: {"new_name": "source.path", ...}
    
    Returns:
        Extracted data with new field names
    """
    try:
        return await ai_tools.extract_data_fields(source_data, field_mapping)
    except Exception as e:
        logger.error("extract_data_fields failed: %s", e)
        raise

@mcp.tool()
async def calculate_metrics(
    input_data: Dict[str, Any],
    calculations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Perform calculations on input data.
    
    Args:
        input_data: Source data for calculations
        calculations: List of calculation definitions
    
    Returns:
        Calculated metrics and derived values
    """
    try:
        return await ai_tools.calculate_metrics(input_data, calculations)
    except Exception as e:
        logger.error("calculate_metrics failed: %s", e)
        raise

# =============================================================================
# WEATHER DOMAIN ATOMIC TOOLS
# =============================================================================

@mcp.tool()
async def parse_coordinates(location: str) -> Dict[str, Any]:
    """
    Convert location string to geographic coordinates.
    
    Args:
        location: Location name or address
    
    Returns:
        {"lat": float, "lon": float, "name": str, "country": str}
    """
    try:
        return await weather_tools.parse_coordinates(location)
    except Exception as e:
        logger.error("parse_coordinates failed: %s", e)
        raise

@mcp.tool()
async def calculate_weather_metrics(
    temperature: float,
    humidity: int,
    wind_speed: float,
    wind_direction: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate derived weather metrics.
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage
        wind_speed: Wind speed in m/s
        wind_direction: Wind direction in degrees
    
    Returns:
        {"heat_index": float, "wind_chill": float, "comfort_level": str}
    """
    try:
        return await weather_tools.calculate_weather_metrics(
            temperature, humidity, wind_speed, wind_direction
        )
    except Exception as e:
        logger.error("calculate_weather_metrics failed: %s", e)
        raise

@mcp.tool()
async def generate_weather_prompt(
    current_weather: Dict[str, Any],
    forecast_data: Optional[List[Dict[str, Any]]] = None,
    insight_type: str = "general"
) -> str:
    """
    Generate specialized prompts for weather AI analysis.
    
    Args:
        current_weather: Current weather data
        forecast_data: Optional forecast data
        insight_type: Type of insights (general, clothing, activities, travel, health)
    
    Returns:
        Formatted prompt string for AI analysis
    """
    try:
        return await weather_tools.generate_weather_prompt(
            current_weather, forecast_data, insight_type
        )
    except Exception as e:
        logger.error("generate_weather_prompt failed: %s", e)
        raise

@mcp.tool()
async def validate_location(location: str) -> Dict[str, Any]:
    """
    Validate and standardize location input.
    
    Args:
        location: User-provided location string
    
    Returns:
        {"valid": bool, "standardized": str, "suggestions": list}
    """
    try:
        return await weather_tools.validate_location(location)
    except Exception as e:
        logger.error("validate_location failed: %s", e)
        return {
            "valid": False,
            "standardized": "",
            "suggestions": [f"Validation error: {str(e)}"]
        }

# =============================================================================
# CONVENIENCE TOOLS (Optional - for comparison with composite approach)
# =============================================================================

# @mcp.tool()
# async def get_current_weather_atomic(location: str) -> Dict[str, Any]:
#     """
#     Example workflow: Get current weather using atomic tools.
#     This demonstrates how agents can compose atomic tools.
    
#     Args:
#         location: Location for weather data
        
#     Returns:
#         Current weather data
#     """
#     try:
#         logger.info("Getting current weather using atomic tools for: %s", location)
        
#         # Step 1: Validate location
#         location_validation = await validate_location(location)
#         if not location_validation["valid"]:
#             raise ValueError(f"Invalid location: {location}")
        
#         validated_location = location_validation["standardized"]
        
#         # Step 2: Check cache first
#         cache_key = f"weather_{validated_location.replace(' ', '_').lower()}"
#         cached_data = await get_cached_data(cache_key)
#         if cached_data:
#             logger.info("Returning cached weather data")
#             return cached_data
        
#         # Step 3: Get API key
#         api_key = await get_secret("OWM-API-KEY")
        
#         # Step 4: Build API URL
#         api_url = await build_api_url(
#             Settings.OPENWEATHER_BASE_URL,
#             "weather",
#             {"q": validated_location, "appid": api_key, "units": "metric"}
#         )
        
#         # Step 5: Make API request
#         response = await http_request(api_url)
        
#         # Step 6: Validate response
#         validation = await validate_api_response(
#             response["data"],
#             ["main", "weather", "name"]
#         )
#         if not validation["valid"]:
#             raise ValueError(f"Invalid API response: {validation['errors']}")
        
#         # Step 7: Extract and format data
#         field_mapping = {
#             "location": "name",
#             "temp": "main.temp",
#             "feels_like": "main.feels_like", 
#             "description": "weather.0.description",
#             "humidity": "main.humidity",
#             "wind_speed": "wind.speed",
#             "wind_direction": "wind.deg"
#         }
        
#         weather_data = await extract_data_fields(response["data"], field_mapping)
        
#         # Step 8: Calculate weather metrics
#         if weather_data.get("temp") and weather_data.get("humidity"):
#             metrics = await calculate_weather_metrics(
#                 weather_data["temp"],
#                 weather_data["humidity"],
#                 weather_data.get("wind_speed", 0),
#                 weather_data.get("wind_direction")
#             )
#             weather_data.update(metrics)
        
#         # Step 9: Cache the result
#         await cache_data(cache_key, weather_data, 300)  # 5 minutes
        
#         logger.info("Current weather retrieved using atomic tools")
#         return weather_data
        
#     except Exception as e:
#         logger.error("Atomic current weather failed: %s", e)
#         raise

# # =============================================================================
# # SERVER STARTUP
# # =============================================================================
@mcp.prompt()
async def atomic_tools_workflow_guide():
    """
    Complete Atomic Tools Workflow Guide
    
    This server provides 16 atomic tools organized in 4 categories. Most tasks require chaining multiple tools together.
    
    🔑 ESSENTIAL PATTERN - Start with Secrets:
    All API operations need: get_secret('OWM-API-KEY') or get_secret('OPENAI-API-KEY') FIRST
    
    🌤️ WEATHER DATA WORKFLOW (Most Common):
    1. get_secret('OWM-API-KEY') → Get OpenWeatherMap API key  
    2. build_api_url('https://api.openweathermap.org/data/2.5', 'weather', {q: city, appid: key, units: 'metric'}) → Build request URL
    3. http_request(url, 'GET') → Make API call to OpenWeatherMap
    4. extract_data_fields(response, {temp: 'main.temp', condition: 'weather.0.description', city: 'name'}) → Extract key data
    5. format_data(extracted_data, 'weather') → Format for human reading
    
    🌍 MULTI-CITY COMPARISON:
    1. get_secret('OWM-API-KEY') → Get API key (reuse for all cities)
    2. FOR EACH CITY: build_api_url → http_request → extract_data_fields
    3. calculate_metrics([temp1, temp2, temp3], 'average') → Compare temperatures  
    4. format_data(comparison_results, 'comparison') → Format comparison
    
    💾 SMART CACHING (Performance Optimization):
    - Check cache_data BEFORE making API calls: get_cached_data('weather_london')
    - Store results AFTER successful calls: cache_data('weather_london', data, 300)  
    - Use clear_cache('weather_*') to cleanup old entries
    
    🤖 AI-ENHANCED RESPONSES:
    1. Complete weather workflow above to get data
    2. ai_completion(f"Based on {weather_data}, what should I wear today?") → AI insights
    
    ⚡ PERFORMANCE TIPS:
    - get_secret() results are automatically cached - call it freely
    - Weather data should be cached for 5-10 minutes (300-600 seconds)
    - validate_location() before API calls to avoid failed requests
    
    🔧 ERROR HANDLING:
    - Use validate_response() after http_request() to check for errors
    - validate_location() returns coordinates for ambiguous city names
    - Cache failures should fallback to get_cached_data()
    
    REMEMBER: Break every task into atomic steps. Think: secrets → build → request → extract → format
    """


if __name__ == "__main__":
    logger.info("Starting Atomic Weather MCP Server")
    logger.info("All atomic tools ready for agent use")
    mcp.run(transport='stdio')