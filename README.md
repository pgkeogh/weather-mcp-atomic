MCP Atomic Tool Architecture Design Document


Executive Summary


Transform the current MCP Weather Server from composite tools to atomic, reusable components that provide AI agents with granular control and true agency over weather data workflows.
________________________________________
Current Architecture Analysis
Existing Composite Tools
# Current: Monolithic weather tools
get_current_weather(location) → formatted_weather_string
get_weather_forecast(location) → formatted_forecast_string  
get_weather_insights(location) → ai_generated_insights_string
Issues with Current Approach
•	Limited Agency: Agents can't control individual steps
•	No Reusability: Weather-specific logic can't be used elsewhere
•	Poor Error Recovery: Failure in one step kills entire workflow
•	No Optimization: Can't cache intermediate results
•	Hard to Test: Complex integration testing required
________________________________________
Atomic Tool Architecture
Design Principles
1.	Single Responsibility: Each tool does one thing well
2.	Composability: Tools combine to create complex workflows
3.	Reusability: Same tools work across different domains
4.	Agency: Agents control workflow and decision-making
5.	Testability: Each tool independently verifiable
Tool Categories
🔑 Infrastructure Tools
Generic, reusable system operations
🌐 HTTP & API Tools
Network communication and data retrieval
🧠 AI & Processing Tools
Intelligence and data transformation
🌤️ Domain-Specific Tools
Weather-specific business logic
________________________________________
Detailed Tool Definitions
Infrastructure Tools
@mcp.tool()
async def get_secret(
    secret_name: str, 
    vault_name: str = None
) -> str:
    """
    Retrieve any secret from Azure Key Vault.

    Args:
        secret_name: Name of the secret to retrieve
        vault_name: Optional vault name (uses default if not provided)

    Returns:
        Secret value as string

    Security: Validate secret_name against allowlist
    """

@mcp.tool()
async def cache_data(
    key: str, 
    data: dict, 
    ttl_seconds: int = 300
) -> bool:
    """
    Cache data with expiration for performance optimization.

    Args:
        key: Cache key identifier
        data: Data to cache (JSON serializable)
        ttl_seconds: Time to live in seconds

    Returns:
        True if cached successfully
    """

@mcp.tool()
async def get_cached_data(key: str) -> dict:
    """
    Retrieve cached data if available and not expired.

    Args:
        key: Cache key identifier

    Returns:
        Cached data or None if not found/expired
    """
HTTP & API Tools
@mcp.tool()
async def http_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    headers: dict = None,
    timeout: int = 30
) -> dict:
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

@mcp.tool()
async def build_api_url(
    base_url: str,
    endpoint: str,
    params: dict = None
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

@mcp.tool()
async def validate_api_response(
    response_data: dict,
    required_fields: list,
    response_type: str = "json"
) -> dict:
    """
    Validate API response structure and required fields.

    Args:
        response_data: Response data to validate
        required_fields: List of required field names
        response_type: Expected response type

    Returns:
        {"valid": bool, "missing_fields": list, "errors": list}
    """
AI & Processing Tools
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

@mcp.tool()
async def format_data(
    data: dict,
    format_type: str,
    template: str = None
) -> str:
    """
    Format data using specified formatter.

    Args:
        data: Input data to format
        format_type: Format type (json, table, summary, detailed)
        template: Optional custom template

    Returns:
        Formatted string output
    """

@mcp.tool()
async def extract_data_fields(
    source_data: dict,
    field_mapping: dict
) -> dict:
    """
    Extract and map specific fields from complex data structures.

    Args:
        source_data: Source data structure
        field_mapping: {"new_name": "source.path", ...}

    Returns:
        Extracted data with new field names
    """

@mcp.tool()
async def calculate_metrics(
    input_data: dict,
    calculations: list
) -> dict:
    """
    Perform calculations on input data.

    Args:
        input_data: Source data for calculations
        calculations: List of calculation definitions

    Returns:
        Calculated metrics and derived values
    """
Weather Domain Tools
@mcp.tool()
async def parse_coordinates(location: str) -> dict:
    """
    Convert location string to geographic coordinates.

    Args:
        location: Location name or address

    Returns:
        {"lat": float, "lon": float, "name": str, "country": str}
    """

@mcp.tool()
async def calculate_weather_metrics(
    temperature: float,
    humidity: int,
    wind_speed: float,
    wind_direction: int = None
) -> dict:
    """
    Calculate derived weather metrics.

    Args:
        temperature: Temperature in selected units
        humidity: Relative humidity percentage
        wind_speed: Wind speed in selected units
        wind_direction: Wind direction in degrees

    Returns:
        {"heat_index": float, "wind_chill": float, "comfort_level": str}
    """

@mcp.tool()
async def generate_weather_prompt(
    current_weather: dict,
    forecast_data: list = None,
    insight_type: str = "general"
) -> str:
    """
    Generate specialized prompts for weather AI analysis.

    Args:
        current_weather: Current weather data
        forecast_data: Optional forecast data
        insight_type: Type of insights (general, clothing, activities, travel)

    Returns:
        Formatted prompt string for AI analysis
    """

@mcp.tool()
async def validate_location(location: str) -> dict:
    """
    Validate and standardize location input.

    Args:
        location: User-provided location string

    Returns:
        {"valid": bool, "standardized": str, "suggestions": list}
    """
________________________________________
Implementation Plan
Phase 1: Foundation
Goals
•	Implement core infrastructure tools
•	Maintain existing composite tools for compatibility
•	Set up atomic tool testing framework
Deliverables
# New atomic tools
- get_secret()
- http_request()  
- ai_completion()
- format_data()

# Enhanced project structure
atomic_tools/
├── infrastructure.py
├── http_api.py
├── ai_processing.py
└── weather_domain.py
Implementation Steps
1.	Create atomic tool modules
2.	Implement basic infrastructure tools
3.	Set up comprehensive testing
4.	Document tool combinations
Phase 2: HTTP & API Tools
Goals
•	Generic HTTP client with retry logic
•	API response validation
•	URL building utilities
Deliverables
# HTTP tools
- http_request() - Generic HTTP client
- build_api_url() - URL construction
- validate_api_response() - Response validation
Phase 3: AI & Processing Tools
Goals
•	Flexible AI completion tool
•	Data formatting and extraction tools
•	Calculation utilities
Deliverables
# AI tools
- ai_completion() - Generic AI calls
- format_data() - Multiple format types
- extract_data_fields() - Data transformation
- calculate_metrics() - Derived calculations
Phase 4: Weather Domain Tools
Goals
•	Weather-specific business logic
•	Location handling and validation
•	Weather metrics calculations
Deliverables
# Weather domain tools
- parse_coordinates()
- calculate_weather_metrics()
- generate_weather_prompt()
- validate_location()
Phase 5: Workflow Examples
Goals
•	Document common agent workflows
•	Create workflow templates
•	Performance optimization guide
Deliverables
# Example workflows
workflows/
├── current_weather_atomic.py
├── forecast_analysis_atomic.py
└── ai_insights_atomic.py
________________________________________
Security Considerations
🔐 Secret Management
# Implement allowlist for secret access
ALLOWED_SECRETS = [
    "openweather-api-key",
    "openai-api-key",
    # No wildcard access
]

async def get_secret(secret_name: str) -> str:
    if secret_name not in ALLOWED_SECRETS:
        raise SecurityError(f"Access denied to secret: {secret_name}")
🌐 HTTP Request Security
# Implement URL allowlist for HTTP requests
ALLOWED_DOMAINS = [
    "api.openweathermap.org",
    "api.openai.com"
]

async def http_request(url: str, ...) -> dict:
    domain = urlparse(url).netloc
    if domain not in ALLOWED_DOMAINS:
        raise SecurityError(f"HTTP requests not allowed to: {domain}")
🧠 AI Request Limits
# Implement rate limiting and content filtering
async def ai_completion(prompt: str, ...) -> str:
    await rate_limiter.check_limit()
    filtered_prompt = content_filter.sanitize(prompt)
    # ... proceed with filtered prompt
________________________________________

Performance Considerations
Caching Strategy
# Cache frequently requested data
cache_keys = {
    "weather_{location}_{date}": 300,  # 5 minutes
    "forecast_{location}_{date}": 1800,  # 30 minutes
    "ai_insights_{hash}": 3600  # 1 hour
}
Request Optimization
# Batch requests where possible
async def batch_weather_request(locations: list) -> dict:
    """Request weather for multiple locations efficiently."""

# Parallel processing
async def parallel_ai_analysis(prompts: list) -> list:
    """Process multiple AI requests concurrently."""

________________________________________
Expected Benefits
🤖 For AI Agents
•	Greater Control: Choose workflow steps
•	Error Recovery: Retry individual components
•	Optimization: Cache intermediate results
•	Creativity: Novel tool combinations
🔧 for Developers
•	Reusability: Tools work across domains
•	Testability: Simple unit testing
•	Debugging: Isolate failure points
•	Extensibility: Add tools without duplication
📈 For Performance
•	Caching: Intermediate result storage
•	Parallelization: Concurrent tool execution
•	Efficiency: Skip unnecessary steps
________________________________________
