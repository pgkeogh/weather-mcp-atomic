# atomic_tools/http_api.py
"""
HTTP and API atomic tools for MCP server.
Provides generic network communication and API handling.
"""
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlencode, urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from security.allowlists import ALLOWED_DOMAINS

logger = logging.getLogger(__name__)

class HTTPAPITools:
    """HTTP and API atomic tools with security controls."""
    
    def __init__(self):
        self._session: Optional[requests.Session] = None
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        if self._session is None:
            session = requests.Session()
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            self._session = session
            logger.info("HTTP session initialized with retry strategy")
        
        return self._session
    
    async def http_request(
        self,
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
        
        # Security check
        domain = urlparse(url).netloc
        if domain not in ALLOWED_DOMAINS:
            raise SecurityError(f"HTTP requests not allowed to: {domain}")
        
        try:
            session = self._create_session()
            
            # Prepare request
            request_kwargs = {
                "timeout": timeout,
                "headers": headers or {}
            }
            
            if method.upper() == "GET":
                request_kwargs["params"] = params
            else:
                request_kwargs["json"] = params
            
            logger.info("Making %s request to: %s", method, url)
            
            response = session.request(method, url, **request_kwargs)
            response.raise_for_status()
            
            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"text": response.text}
            
            result = {
                "status": response.status_code,
                "data": response_data,
                "headers": dict(response.headers)
            }
            
            logger.info("HTTP request successful: %d", response.status_code)
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error for %s: %s", url, e)
            raise RuntimeError(f"HTTP request failed: {e.response.status_code}") from e
            
        except Exception as e:
            logger.error("HTTP request failed for %s: %s", url, e)
            raise RuntimeError(f"Network request failed: {str(e)}") from e
    
    async def build_api_url(
        self,
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
            # Fix: Ensure base_url ends with "/" and endpoint doesn't start with "/"
            base_url = base_url.rstrip('/') + '/'
            endpoint = endpoint.lstrip('/')
            
            full_url = urljoin(base_url, endpoint)
            
            # Add query parameters if provided
            if params:
                # Filter out None values
                clean_params = {k: v for k, v in params.items() if v is not None}
                if clean_params:
                    query_string = urlencode(clean_params)
                    full_url = f"{full_url}?{query_string}"
            
            logger.debug("Built API URL: %s", full_url)
            return full_url
            
        except Exception as e:
            logger.error("Failed to build URL: %s", e)
            raise ValueError(f"URL construction failed: {str(e)}") from e
    
    async def validate_api_response(
        self,
        response_data: Dict[str, Any],
        required_fields: list,
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
            validation_result = {
                "valid": True,
                "missing_fields": [],
                "errors": []
            }
            
            # Check response type
            if response_type == "json" and not isinstance(response_data, dict):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Expected dict, got {type(response_data)}")
                return validation_result
            
            # Check required fields
            if isinstance(response_data, dict):
                for field in required_fields:
                    if '.' in field:
                        # Nested field check (e.g., "main.temp")
                        field_parts = field.split('.')
                        current_data = response_data
                        
                        for part in field_parts:
                            if not isinstance(current_data, dict) or part not in current_data:
                                validation_result["missing_fields"].append(field)
                                break
                            current_data = current_data[part]
                    else:
                        # Simple field check
                        if field not in response_data:
                            validation_result["missing_fields"].append(field)
                            
            # Set overall validity
            if validation_result["missing_fields"]:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required fields: {validation_result['missing_fields']}")
            
            logger.debug("Response validation: %s", validation_result)
            return validation_result
            
        except Exception as e:
            logger.error("Response validation failed: %s", e)
            return {
                "valid": False,
                "missing_fields": [],
                "errors": [f"Validation error: {str(e)}"]
            }


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass