# atomic_tools/weather_domain.py
"""
Weather domain-specific atomic tools for MCP server.
Provides weather business logic and specialized operations.
"""
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherDomainTools:
    """Weather domain atomic tools for specialized weather operations."""
    
    def __init__(self):
        pass
    
    async def parse_coordinates(self, location: str) -> Dict[str, Any]:
        """
        Convert location string to geographic coordinates.
        Note: This is a simplified implementation. Production would use geocoding service.
        
        Args:
            location: Location name or address
        
        Returns:
            {"lat": float, "lon": float, "name": str, "country": str}
        """
        try:
            # Check if location is already coordinates (lat,lon format)
            coord_pattern = r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$'
            coord_match = re.match(coord_pattern, location.strip())
            
            if coord_match:
                lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
                return {
                    "lat": lat,
                    "lon": lon,
                    "name": f"Location({lat},{lon})",
                    "country": "Unknown"
                }
            
            # For this implementation, we'll use the location string as-is
            # In production, this would call a geocoding service
            logger.info("Parsing location: %s", location)
            
            # Common location mappings for testing
            location_mappings = {
                "seattle": {"lat": 47.6062, "lon": -122.3321, "name": "Seattle", "country": "US"},
                "london": {"lat": 51.5074, "lon": -0.1278, "name": "London", "country": "GB"},
                "tokyo": {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo", "country": "JP"},
                "new york": {"lat": 40.7128, "lon": -74.0060, "name": "New York", "country": "US"},
                "paris": {"lat": 48.8566, "lon": 2.3522, "name": "Paris", "country": "FR"}
            }
            
            location_key = location.lower().strip()
            if location_key in location_mappings:
                result = location_mappings[location_key]
                logger.debug("Found coordinates for %s: %s", location, result)
                return result
            
            # Default: return the location name as-is (API will handle it)
            return {
                "lat": None,
                "lon": None,
                "name": location,
                "country": "Unknown"
            }
            
        except Exception as e:
            logger.error("Failed to parse coordinates for %s: %s", location, e)
            raise ValueError(f"Location parsing failed: {str(e)}") from e
    
    async def calculate_weather_metrics(
        self,
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
            metrics = {}
            
            # Calculate heat index (simplified formula)
            if temperature >= 27:  # Only relevant for warm temperatures
                # Simplified heat index calculation
                heat_index = temperature + (0.5 * (humidity - 40))
                metrics["heat_index"] = round(heat_index, 1)
            else:
                metrics["heat_index"] = temperature
            
            # Calculate wind chill (for temperatures below 10°C)
            if temperature <= 10 and wind_speed > 1:
                # Simplified wind chill calculation
                wind_chill = 13.12 + 0.6215 * temperature - 11.37 * (wind_speed ** 0.16) + 0.3965 * temperature * (wind_speed ** 0.16)
                metrics["wind_chill"] = round(wind_chill, 1)
            else:
                metrics["wind_chill"] = temperature
            
            # Determine comfort level
            comfort_temp = metrics.get("heat_index", metrics.get("wind_chill", temperature))
            
            if comfort_temp < 0:
                comfort_level = "Very Cold"
            elif comfort_temp < 10:
                comfort_level = "Cold"
            elif comfort_temp < 18:
                comfort_level = "Cool"
            elif comfort_temp < 24:
                comfort_level = "Comfortable"
            elif comfort_temp < 28:
                comfort_level = "Warm"
            elif comfort_temp < 32:
                comfort_level = "Hot"
            else:
                comfort_level = "Very Hot"
            
            # Adjust for humidity
            if humidity > 80:
                if "Warm" in comfort_level or "Hot" in comfort_level:
                    comfort_level += " & Humid"
            elif humidity < 30:
                comfort_level += " & Dry"
            
            # Adjust for wind
            if wind_speed > 10:  # Strong wind
                comfort_level += " & Windy"
            
            metrics["comfort_level"] = comfort_level
            
            # Wind direction description
            if wind_direction is not None:
                wind_dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                wind_index = int((wind_direction + 11.25) / 22.5) % 16
                metrics["wind_direction_text"] = wind_dirs[wind_index]
            else:
                metrics["wind_direction_text"] = "Unknown"
            
            logger.debug("Calculated weather metrics: %s", metrics)
            return metrics
            
        except Exception as e:
            logger.error("Weather metrics calculation failed: %s", e)
            raise ValueError(f"Metrics calculation failed: {str(e)}") from e
    
    async def generate_weather_prompt(
        self,
        current_weather: Dict[str, Any],
        forecast_data: Optional[list] = None,
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
        try:
            location = current_weather.get('location', 'this location')
            
            # Base prompt with current weather
            prompt_parts = [
                f"Analyze the weather for {location}.",
                f"Current conditions: {current_weather}"
            ]
            
            # Add forecast if available
            if forecast_data:
                prompt_parts.append(f"5-day forecast: {forecast_data}")
            
            # Customize prompt based on insight type
            if insight_type == "clothing":
                prompt_parts.append(
                    "Provide specific clothing recommendations based on the weather conditions. "
                    "Consider temperature, precipitation, wind, and humidity. "
                    "Be practical and specific about layering, footwear, and accessories."
                )
            
            elif insight_type == "activities":
                prompt_parts.append(
                    "Suggest outdoor and indoor activities suitable for these weather conditions. "
                    "Consider safety, comfort, and seasonal appropriateness. "
                    "Mention any activities to avoid due to weather."
                )
            
            elif insight_type == "travel":
                prompt_parts.append(
                    "Provide travel advice based on these weather conditions. "
                    "Include transportation considerations, packing suggestions, "
                    "and any weather-related travel alerts or precautions."
                )
            
            elif insight_type == "health":
                prompt_parts.append(
                    "Analyze health implications of these weather conditions. "
                    "Consider air quality, UV index, temperature effects, "
                    "and provide health and wellness recommendations."
                )
            
            else:  # general
                prompt_parts.append(
                    "Provide a comprehensive weather analysis including trends, "
                    "comfort levels, and general recommendations for the next few days."
                )
            
            # Final formatting instruction
            prompt_parts.append(
                "Keep your response concise, practical, and informative. "
                "Focus on actionable insights."
            )
            
            prompt = "\n\n".join(prompt_parts)
            logger.debug("Generated %s weather prompt, length: %d", insight_type, len(prompt))
            
            return prompt
            
        except Exception as e:
            logger.error("Weather prompt generation failed: %s", e)
            raise ValueError(f"Prompt generation failed: {str(e)}") from e
    
    async def validate_location(self, location: str) -> Dict[str, Any]:
        """
        Validate and standardize location input.
        
        Args:
            location: User-provided location string
        
        Returns:
            {"valid": bool, "standardized": str, "suggestions": list}
        """
        try:
            validation_result = {
                "valid": False,
                "standardized": "",
                "suggestions": []
            }
            
            if not location or not isinstance(location, str):
                validation_result["suggestions"] = ["Please provide a valid location name"]
                return validation_result
            
            # Clean up the location string
            cleaned_location = location.strip()
            
            # Basic validation rules
            if len(cleaned_location) < 2:
                validation_result["suggestions"] = ["Location name too short"]
                return validation_result
            
            if len(cleaned_location) > 100:
                validation_result["suggestions"] = ["Location name too long"]
                return validation_result
            
            # Check for valid characters (letters, numbers, spaces, hyphens, apostrophes)
            if not re.match(r"^[a-zA-Z0-9\s\-',\.]+$", cleaned_location):
                validation_result["suggestions"] = ["Location contains invalid characters"]
                return validation_result
            
            # Standardize common formats
            standardized = cleaned_location.title()
            
            # Handle common abbreviations
            abbreviations = {
                " Usa": " USA",
                " Uk": " UK",
                " Us": " US",
                "Nyc": "NYC",
                "La ": "LA "
            }
            
            for abbrev, replacement in abbreviations.items():
                standardized = standardized.replace(abbrev, replacement)
            
            validation_result["valid"] = True
            validation_result["standardized"] = standardized
            
            logger.debug("Location validation successful: %s -> %s", location, standardized)
            return validation_result
            
        except Exception as e:
            logger.error("Location validation failed: %s", e)
            return {
                "valid": False,
                "standardized": "",
                "suggestions": [f"Validation error: {str(e)}"]
            }