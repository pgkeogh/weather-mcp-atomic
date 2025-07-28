# atomic_tools/ai_processing.py
"""
AI and data processing atomic tools for MCP server.
Provides intelligence and data transformation capabilities.
"""
import logging
import json
from typing import Dict, Any, Optional, List
from atomic_tools.http_api import HTTPAPITools
from services.key_vault_service import KeyVaultService

logger = logging.getLogger(__name__)

class AIProcessingTools:
    """AI and processing atomic tools with flexible capabilities."""
    
    def __init__(self, key_vault_service: KeyVaultService, http_tools: HTTPAPITools):
        self.key_vault_service = key_vault_service
        self.http_tools = http_tools
        self._openai_key: Optional[str] = None
    
    async def _get_openai_key(self) -> str:
        """Get OpenAI API key from Key Vault."""
        if self._openai_key is None:
            self._openai_key = await self.key_vault_service.get_secret("OPENAI-API-KEY")
        return self._openai_key
    
    async def ai_completion(
        self,
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
            
            api_key = await self._get_openai_key()
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            logger.info("Making AI completion request with model: %s", model)
            
            response = await self.http_tools.http_request(
                "https://api.openai.com/v1/chat/completions",
                method="POST",
                params=payload,
                headers=headers,
                timeout=60
            )
            
            completion_text = response["data"]["choices"][0]["message"]["content"]
            logger.info("AI completion successful, length: %d chars", len(completion_text))
            
            return completion_text.strip()
            
        except Exception as e:
            logger.error("AI completion failed: %s", e)
            raise RuntimeError(f"AI service unavailable: {str(e)}") from e
    
    async def format_data(
        self,
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
            if format_type == "json":
                return json.dumps(data, indent=2)
            
            elif format_type == "weather_current":
                return self._format_current_weather(data)
            
            elif format_type == "weather_forecast":
                return self._format_forecast_weather(data)
            
            elif format_type == "summary":
                return self._format_summary(data)
            
            elif format_type == "detailed":
                return self._format_detailed(data)
            
            elif format_type == "table":
                return self._format_table(data)
            
            elif template:
                return self._format_with_template(data, template)
            
            else:
                # Default: readable key-value format
                return self._format_default(data)
                
        except Exception as e:
            logger.error("Data formatting failed: %s", e)
            return f"Formatting error: {str(e)}"
    
    def _format_current_weather(self, data: Dict[str, Any]) -> str:
        """Format current weather data."""
        location = data.get('location', 'Unknown')
        temp = data.get('temp', 'N/A')
        description = data.get('description', 'N/A')
        humidity = data.get('humidity', 'N/A')
        wind_speed = data.get('wind_speed', 'N/A')
        
        return f"""Current weather in {location}:
Temperature: {temp}°C
Condition: {description}
Humidity: {humidity}%
Wind: {wind_speed} m/s"""
    
    def _format_forecast_weather(self, data: List[Dict[str, Any]]) -> str:
        """Format forecast weather data."""
        if not data:
            return "No forecast data available"
        
        result = "5-day weather forecast:\n"
        for day in data:
            result += f"\n{day.get('date', 'Unknown')}: "
            result += f"{day.get('temp_high', 'N/A')}°/{day.get('temp_low', 'N/A')}° - "
            result += f"{day.get('description', 'N/A')}"
        
        return result
    
    def _format_summary(self, data: Dict[str, Any]) -> str:
        """Format data as brief summary."""
        summary_items = []
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                summary_items.append(f"{key}: {value}")
        return "; ".join(summary_items)
    
    def _format_detailed(self, data: Dict[str, Any]) -> str:
        """Format data with detailed breakdown."""
        result = []
        for key, value in data.items():
            if isinstance(value, dict):
                result.append(f"{key.title()}:")
                for sub_key, sub_value in value.items():
                    result.append(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                result.append(f"{key.title()}: {len(value)} items")
            else:
                result.append(f"{key.title()}: {value}")
        return "\n".join(result)
    
    def _format_table(self, data: Dict[str, Any]) -> str:
        """Format data as simple table."""
        if not data:
            return "No data"
        
        max_key_len = max(len(str(k)) for k in data.keys())
        result = []
        
        for key, value in data.items():
            padded_key = str(key).ljust(max_key_len)
            result.append(f"{padded_key} | {value}")
        
        return "\n".join(result)
    
    def _format_with_template(self, data: Dict[str, Any], template: str) -> str:
        """Format data using custom template."""
        try:
            return template.format(**data)
        except KeyError as e:
            return f"Template error - missing key: {e}"
    
    def _format_default(self, data: Dict[str, Any]) -> str:
        """Default formatting for any data structure."""
        result = []
        for key, value in data.items():
            result.append(f"{key}: {value}")
        return "\n".join(result)
    
    async def extract_data_fields(
        self,
        source_data: Dict[str, Any],
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract and map specific fields from complex data structures.
        Supports nested objects and arrays (e.g., "weather.0.description").
        Args:
            source_data: Source data structure
            field_mapping: {"new_name": "source.path", ...}
        
        Returns:
            Extracted data with new field names
        """
        
        try:
            extracted = {}
            
            for new_field, source_path in field_mapping.items():
                try:
                    # Split the path and navigate step by step
                    path_parts = source_path.split('.')
                    current_value = source_data
                    
                    for part in path_parts:
                        if part.isdigit():
                            # Handle array index
                            index = int(part)
                            if isinstance(current_value, list) and 0 <= index < len(current_value):
                                current_value = current_value[index]
                            else:
                                raise IndexError(f"Invalid array index {index}")
                        else:
                            # Handle object key
                            if isinstance(current_value, dict) and part in current_value:
                                current_value = current_value[part]
                            else:
                                raise KeyError(f"Key '{part}' not found")
                    
                    extracted[new_field] = current_value
                    
                except (KeyError, IndexError, TypeError) as e:
                    logger.warning("Failed to extract field '%s' with path '%s': %s", 
                                new_field, source_path, e)
                    extracted[new_field] = None
            
            logger.debug("Field extraction completed: %s", extracted)
            return extracted
            
        except Exception as e:
            logger.error("Data extraction failed: %s", e)
            raise
    
    async def calculate_metrics(
        self,
        input_data: Dict[str, Any],
        calculations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform calculations on input data.
        
        Args:
            input_data: Source data for calculations
            calculations: List of calculation definitions
                Example: [{"name": "temp_range", "operation": "subtract", "fields": ["max_temp", "min_temp"]}]
        
        Returns:
            Calculated metrics and derived values
        """
        try:
            results = {}
            
            for calc in calculations:
                calc_name = calc.get("name", "unknown")
                operation = calc.get("operation", "")
                fields = calc.get("fields", [])
                
                try:
                    if operation == "subtract" and len(fields) == 2:
                        val1 = input_data.get(fields[0], 0)
                        val2 = input_data.get(fields[1], 0)
                        results[calc_name] = val1 - val2
                    
                    elif operation == "add" and len(fields) >= 2:
                        total = sum(input_data.get(field, 0) for field in fields)
                        results[calc_name] = total
                    
                    elif operation == "average" and len(fields) >= 2:
                        values = [input_data.get(field, 0) for field in fields]
                        results[calc_name] = sum(values) / len(values)
                    
                    elif operation == "max" and len(fields) >= 2:
                        values = [input_data.get(field, 0) for field in fields]
                        results[calc_name] = max(values)
                    
                    elif operation == "min" and len(fields) >= 2:
                        values = [input_data.get(field, 0) for field in fields]
                        results[calc_name] = min(values)
                    
                    else:
                        logger.warning("Unknown calculation operation: %s", operation)
                        results[calc_name] = None
                        
                except Exception as e:
                    logger.warning("Calculation failed for %s: %s", calc_name, e)
                    results[calc_name] = None
            
            logger.debug("Completed %d calculations", len(results))
            return results
            
        except Exception as e:
            logger.error("Metric calculation failed: %s", e)
            raise ValueError(f"Calculation failed: {str(e)}") from e