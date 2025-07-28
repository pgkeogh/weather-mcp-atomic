# security/allowlists.py
"""
Security allowlists for atomic tools.
Defines what secrets, domains, and operations are permitted.
"""

# Allowed secrets from Key Vault
ALLOWED_SECRETS = [
    "OWM-API-KEY",      # OpenWeatherMap API key
    "OPENAI-API-KEY",   # OpenAI API key
    # Add other secrets as needed - no wildcard access
]

# Allowed domains for HTTP requests
ALLOWED_DOMAINS = [
    "api.openweathermap.org",
    "api.openai.com",
    "httpbin.org",  # For testing
    # Add other trusted domains as needed
]

# Cache key patterns (for validation)
ALLOWED_CACHE_PATTERNS = [
    "weather_",
    "forecast_", 
    "ai_insights_",
    "api_response_",
    # Add patterns as needed
]