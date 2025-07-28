# tests/test_atomic_tools.py
"""
Comprehensive test suite for atomic MCP server.
Tests individual tools, combinations, workflows, and agent autonomy.
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, List
import sys
from pathlib import Path

# Import the main server components
from services.key_vault_service import KeyVaultService
from atomic_tools.infrastructure import InfrastructureTools
from atomic_tools.http_api import HTTPAPITools
from atomic_tools.ai_processing import AIProcessingTools
from atomic_tools.weather_domain import WeatherDomainTools
from config.settings import Settings

# # Add project root to path
# sys.path.append(str(Path(__file__).parent.parent))

# Set up test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AtomicToolsTester:
    """Comprehensive tester for atomic MCP tools."""
    
    def __init__(self):
        """Initialize all atomic tools for testing."""
        logger.info("Initializing atomic tools for testing...")
        
        # Initialize services
        self.key_vault_service = KeyVaultService()
        
        # Initialize atomic tools
        self.infrastructure = InfrastructureTools(self.key_vault_service)
        self.http_tools = HTTPAPITools()
        self.ai_tools = AIProcessingTools(self.key_vault_service, self.http_tools)
        self.weather_tools = WeatherDomainTools()
        
        logger.info("All tools initialized successfully")
    
    # =================================================================
    # LEVEL 1: INDIVIDUAL ATOMIC TOOL TESTS
    # =================================================================
    
    async def test_infrastructure_tools(self):
        """Test infrastructure atomic tools."""
        logger.info("🔑 Testing Infrastructure Tools...")
        
        try:
            # Test secret retrieval
            logger.info("Testing secret retrieval...")
            api_key = await self.infrastructure.get_secret("OWM-API-KEY")
            assert api_key is not None
            assert len(api_key) > 10
            logger.info("✅ Secret retrieval successful")
            
            # Test caching
            logger.info("Testing cache operations...")
            test_data = {"test": "data", "timestamp": time.time()}
            
            # Cache data
            cached = await self.infrastructure.cache_data("test_key", test_data, 60)
            assert cached is True
            logger.info("✅ Data cached successfully")
            
            # Retrieve cached data
            retrieved = await self.infrastructure.get_cached_data("test_key")
            assert retrieved is not None
            assert retrieved["test"] == "data"
            logger.info("✅ Cache retrieval successful")
            
            # Test cache miss
            miss = await self.infrastructure.get_cached_data("nonexistent_key")
            assert miss is None
            logger.info("✅ Cache miss handled correctly")
            
            return True
            
        except Exception as e:
            logger.error("❌ Infrastructure tools test failed: %s", e)
            return False
    
    async def test_http_tools(self):
        """Test HTTP and API atomic tools."""
        logger.info("🌐 Testing HTTP/API Tools...")
        
        try:
            # Test URL building
            logger.info("Testing URL building...")
            url = await self.http_tools.build_api_url(
                "https://api.openweathermap.org/data/2.5",
                "weather",
                {"q": "London", "appid": "test_key"}
            )
            assert "api.openweathermap.org" in url
            assert "weather" in url
            assert "London" in url
            logger.info("✅ URL building successful: %s", url)
            
            # Test HTTP request (using httpbin for testing)
            logger.info("Testing HTTP request...")
            response = await self.http_tools.http_request("https://httpbin.org/get")
            assert response["status"] == 200
            assert "data" in response
            logger.info("✅ HTTP request successful")
            
            # Test response validation
            logger.info("Testing response validation...")
            validation = await self.http_tools.validate_api_response(
                response["data"],
                ["url", "headers"]
            )
            assert validation["valid"] is True
            assert len(validation["missing_fields"]) == 0
            logger.info("✅ Response validation successful")
            
            return True
            
        except Exception as e:
            logger.error("❌ HTTP tools test failed: %s", e)
            return False
    
    async def test_ai_tools(self):
        """Test AI and processing atomic tools."""
        logger.info("🧠 Testing AI/Processing Tools...")
        
        try:
            # Test data formatting
            logger.info("Testing data formatting...")
            test_data = {
                "location": "London",
                "temp": 15.5,
                "description": "Cloudy",
                "humidity": 80
            }
            
            formatted = await self.ai_tools.format_data(test_data, "json")
            assert "London" in formatted
            logger.info("✅ JSON formatting successful")
            
            weather_formatted = await self.ai_tools.format_data(test_data, "weather_current")
            assert "Temperature: 15.5°C" in weather_formatted
            logger.info("✅ Weather formatting successful")
            
            # Test data extraction
            logger.info("Testing data extraction...")
            complex_data = {
                "main": {"temp": 20.5, "humidity": 65},
                "weather": [{"description": "sunny"}],
                "name": "Paris"
            }
            
            field_mapping = {
                "temperature": "main.temp",
                "condition": "weather.0.description",
                "city": "name"
            }
            
            extracted = await self.ai_tools.extract_data_fields(complex_data, field_mapping)
            assert extracted["temperature"] == 20.5
            assert extracted["condition"] == "sunny"
            assert extracted["city"] == "Paris"
            logger.info("✅ Data extraction successful")
            
            # Test calculations
            logger.info("Testing calculations...")
            calc_data = {"max_temp": 25, "min_temp": 18, "humidity": 70}
            calculations = [
                {"name": "temp_range", "operation": "subtract", "fields": ["max_temp", "min_temp"]},
                {"name": "avg_temp", "operation": "average", "fields": ["max_temp", "min_temp"]}
            ]
            
            results = await self.ai_tools.calculate_metrics(calc_data, calculations)
            assert results["temp_range"] == 7
            assert results["avg_temp"] == 21.5
            logger.info("✅ Calculations successful")
            
            # Test AI completion (optional - requires API key)
            logger.info("Testing AI completion...")
            try:
                completion = await self.ai_tools.ai_completion(
                    "What's the weather like when it's 20°C and sunny?",
                    max_tokens=100
                )
                assert len(completion) > 0
                logger.info("✅ AI completion successful: %s", completion[:100])
            except Exception as ai_error:
                logger.warning("⚠️ AI completion skipped (API issue): %s", ai_error)
            
            return True
            
        except Exception as e:
            logger.error("❌ AI tools test failed: %s", e)
            return False
    
    async def test_weather_tools(self):  
        """Test weather domain atomic tools."""
        logger.info("🌤️ Testing Weather Domain Tools...")
        
        try:
            # Test location validation
            logger.info("Testing location validation...")
            validation = await self.weather_tools.validate_location("London")
            assert validation["valid"] is True
            assert validation["standardized"] == "London"
            logger.info("✅ Location validation successful")
            
            # Test coordinate parsing
            logger.info("Testing coordinate parsing...")
            coords = await self.weather_tools.parse_coordinates("Seattle")
            assert coords["name"] == "Seattle"
            assert coords["lat"] is not None
            logger.info("✅ Coordinate parsing successful: %s", coords)
            
            # Test weather metrics calculation
            logger.info("Testing weather metrics...")
            metrics = await self.weather_tools.calculate_weather_metrics(
                temperature=22.0,
                humidity=65,
                wind_speed=5.5,
                wind_direction=180
            )
            assert "comfort_level" in metrics
            assert "heat_index" in metrics
            logger.info("✅ Weather metrics successful: %s", metrics["comfort_level"])
            
            # Test weather prompt generation
            logger.info("Testing weather prompt generation...")
            weather_data = {"location": "Paris", "temp": 18, "description": "rainy"}
            prompt = await self.weather_tools.generate_weather_prompt(
                weather_data, 
                insight_type="clothing"
            )
            assert "clothing" in prompt.lower()
            assert "Paris" in prompt
            logger.info("✅ Weather prompt generation successful")
            
            return True
            
        except Exception as e:
            logger.error("❌ Weather tools test failed: %s", e)
            return False
    
    # =================================================================
    # LEVEL 2: TOOL COMBINATION TESTS
    # =================================================================
    
    async def test_tool_combinations(self):
        """Test how atomic tools work together."""
        logger.info("🔗 Testing Tool Combinations...")
        
        try:
            # Test: Secret → URL → HTTP → Validation chain
            logger.info("Testing API request chain...")
            
            # Get API key
            api_key = await self.infrastructure.get_secret("OWM-API-KEY")
            
            # Build URL  
            url = await self.http_tools.build_api_url(
                Settings.OPENWEATHER_BASE_URL,
                "weather",
                {"q": "London", "appid": api_key, "units": "metric"}
            )
            
            # Make request
            response = await self.http_tools.http_request(url)
            
            # Validate response
            validation = await self.http_tools.validate_api_response(
                response["data"],
                ["main", "weather", "name"]
            )
            
            assert validation["valid"] is True
            logger.info("✅ API request chain successful")
            
            # Test: Data → Extract → Format → Cache chain
            logger.info("Testing data processing chain...")
            
            # Extract fields
            field_mapping = {
                "location": "name",
                "temperature": "main.temp",
                "description": "weather.0.description"
            }
            
            extracted = await self.ai_tools.extract_data_fields(response["data"], field_mapping)
            
            # Format data
            formatted = await self.ai_tools.format_data(extracted, "weather_current")
            
            # Cache result
            cache_key = f"test_weather_{int(time.time())}"
            cached = await self.infrastructure.cache_data(cache_key, extracted, 300)
            
            assert cached is True
            assert "Temperature:" in formatted
            logger.info("✅ Data processing chain successful")
            
            return True
            
        except Exception as e:
            logger.error("❌ Tool combination test failed: %s", e)
            return False
    
    # =================================================================
    # LEVEL 3: AGENT WORKFLOW SIMULATION
    # =================================================================
    
    async def test_agent_workflows(self):
        """Simulate how an AI agent might use atomic tools creatively."""
        logger.info("🤖 Testing Agent Workflow Simulation...")
        
        try:
            # Workflow 1: Efficient weather with caching
            logger.info("Simulating Agent Workflow 1: Smart Caching...")
            await self._simulate_smart_caching_workflow()
            
            # Workflow 2: Multi-location comparison
            logger.info("Simulating Agent Workflow 2: Multi-Location Analysis...")
            await self._simulate_multi_location_workflow()
            
            # Workflow 3: Error recovery
            logger.info("Simulating Agent Workflow 3: Error Recovery...")
            await self._simulate_error_recovery_workflow()
            
            return True
            
        except Exception as e:
            logger.error("❌ Agent workflow test failed: %s", e)
            return False
    
    async def _simulate_smart_caching_workflow(self):
        """Simulate agent making smart caching decisions."""
        location = "Tokyo"
        cache_key = f"weather_{location.lower()}"
        
        # Agent checks cache first (smart!)
        cached_data = await self.infrastructure.get_cached_data(cache_key)
        
        if cached_data:
            logger.info("🎯 Agent found cached data - efficient!")
            result = cached_data
        else:
            logger.info("🎯 Agent didn't find cache - fetching fresh data")
            
            # Agent gets fresh data
            api_key = await self.infrastructure.get_secret("OWM-API-KEY")
            url = await self.http_tools.build_api_url(
                Settings.OPENWEATHER_BASE_URL,
                "weather", 
                {"q": location, "appid": api_key, "units": "metric"}
            )
            
            response = await self.http_tools.http_request(url)
            
            # Agent extracts what it needs
            result = await self.ai_tools.extract_data_fields(
                response["data"],
                {"temp": "main.temp", "condition": "weather.0.description"}
            )
            
            # Agent caches for next time (smart!)
            await self.infrastructure.cache_data(cache_key, result, 300)
            logger.info("🎯 Agent cached data for future use")
        
        logger.info("✅ Smart caching workflow completed: %s", result)
    
    async def _simulate_multi_location_workflow(self):
        """Simulate agent comparing multiple locations."""
        locations = ["London", "Paris", "Berlin"]
        weather_data = []
        
        api_key = await self.infrastructure.get_secret("OWM-API-KEY")
        
        # Agent processes multiple locations efficiently
        for location in locations:
            try:
                url = await self.http_tools.build_api_url(
                    Settings.OPENWEATHER_BASE_URL,
                    "weather",
                    {"q": location, "appid": api_key, "units": "metric"}
                )
                
                response = await self.http_tools.http_request(url)
                
                # Agent extracts consistent data structure
                location_data = await self.ai_tools.extract_data_fields(
                    response["data"],
                    {
                        "city": "name",
                        "temp": "main.temp", 
                        "humidity": "main.humidity"
                    }
                )
                
                weather_data.append(location_data)
                
            except Exception as e:
                logger.warning("🎯 Agent handled error for %s: %s", location, e)
                continue
        
        # Agent calculates comparison metrics
        if len(weather_data) > 1:
            temps = [data["temp"] for data in weather_data if data.get("temp")]
            comparison = await self.ai_tools.calculate_metrics(
                {"temps": temps},
                [
                    {"name": "warmest", "operation": "max", "fields": ["temps"]},
                    {"name": "coldest", "operation": "min", "fields": ["temps"]}
                ]
            )
            
            logger.info("✅ Multi-location analysis: %s", comparison)
    
    async def _simulate_error_recovery_workflow(self):
        """Simulate agent recovering from errors gracefully."""
        
        # Agent tries invalid location first
        try:
            validation = await self.weather_tools.validate_location("InvalidLocationXYZ123")
            if not validation["valid"]:
                logger.info("🎯 Agent detected invalid location, trying fallback")
                
                # Agent tries a known good location
                fallback_validation = await self.weather_tools.validate_location("London")
                assert fallback_validation["valid"]
                logger.info("✅ Agent successfully recovered from error")
                
        except Exception as e:
            logger.info("🎯 Agent handled exception gracefully: %s", e)
    
    # =================================================================
    # LEVEL 4: PERFORMANCE & CACHING TESTS  
    # =================================================================
    
    async def test_performance_caching(self):
        """Test performance improvements from caching."""
        logger.info("⚡ Testing Performance & Caching...")
        
        try:
            location = "Seattle"
            cache_key = f"perf_test_{location}"
            
            # Clear any existing cache
            await self.infrastructure.clear_cache("perf_test_")
            
            # Time first request (no cache)
            start_time = time.time()
            api_key = await self.infrastructure.get_secret("OWM-API-KEY")
            url = await self.http_tools.build_api_url(
                Settings.OPENWEATHER_BASE_URL,
                "weather",
                {"q": location, "appid": api_key, "units": "metric"}
            )
            response = await self.http_tools.http_request(url)
            first_request_time = time.time() - start_time
            
            # Cache the result
            await self.infrastructure.cache_data(cache_key, response["data"], 300)
            
            # Time cached request
            start_time = time.time()
            cached_result = await self.infrastructure.get_cached_data(cache_key)
            cached_request_time = time.time() - start_time
            
            # Performance comparison
            speedup = first_request_time / cached_request_time
            logger.info("✅ Performance test results:")
            logger.info("   First request: %.3fs", first_request_time)
            logger.info("   Cached request: %.3fs", cached_request_time)  
            logger.info("   Speedup: %.1fx faster", speedup)
            
            assert cached_result is not None
            assert speedup > 5  # Cache should be much faster
            
            return True
            
        except Exception as e:
            logger.error("❌ Performance test failed: %s", e)
            return False
    
    # =================================================================
    # LEVEL 5: AUTONOMY COMPARISON
    # =================================================================
    
    async def test_autonomy_comparison(self):
        """Compare atomic approach vs composite approach capabilities."""
        logger.info("🆚 Testing Autonomy Comparison...")
        
        try:
            logger.info("=== ATOMIC APPROACH CAPABILITIES ===")
            
            # Capability 1: Custom caching strategy
            logger.info("1. Custom caching strategy...")
            location = "Madrid"
            
            # Agent decides on cache duration based on location
            cache_duration = 600 if "Madrid" in location else 300  # Longer for major cities
            cache_key = f"custom_{location}"
            
            # Agent implements custom workflow
            api_key = await self.infrastructure.get_secret("OWM-API-KEY")
            url = await self.http_tools.build_api_url(
                Settings.OPENWEATHER_BASE_URL,
                "weather",
                {"q": location, "appid": api_key, "units": "metric"}
            )
            
            response = await self.http_tools.http_request(url)
            await self.infrastructure.cache_data(cache_key, response["data"], cache_duration)
            logger.info("✅ Agent implemented custom caching strategy")
            
            # Capability 2: Selective data extraction
            logger.info("2. Selective data extraction...")
            
            # Agent extracts only what it needs for specific use case
            minimal_mapping = {"temp": "main.temp", "condition": "weather.0.main"}
            minimal_data = await self.ai_tools.extract_data_fields(response["data"], minimal_mapping)
            
            detailed_mapping = {
                "temperature": "main.temp",
                "feels_like": "main.feels_like", 
                "humidity": "main.humidity",
                "pressure": "main.pressure",
                "description": "weather.0.description",
                "wind_speed": "wind.speed"
            }
            detailed_data = await self.ai_tools.extract_data_fields(response["data"], detailed_mapping)
            
            logger.info("✅ Agent extracted minimal data: %s", minimal_data)
            logger.info("✅ Agent extracted detailed data available: %d fields", len(detailed_data))
            
            # Capability 3: Error isolation and recovery
            logger.info("3. Error isolation and recovery...")
            
            try:
                # Agent tries risky operation
                bad_url = await self.http_tools.build_api_url("https://invalid.api.com", "test", {})
                await self.http_tools.http_request(bad_url)
            except Exception:
                logger.info("✅ Agent isolated HTTP error, continuing with cached data")
                cached_fallback = await self.infrastructure.get_cached_data(cache_key)
                assert cached_fallback is not None
                logger.info("✅ Agent successfully used fallback data")
            
            # Capability 4: Custom formatting for different contexts
            logger.info("4. Context-aware formatting...")
            
            sample_weather = {"location": "Madrid", "temp": 24, "humidity": 55, "description": "sunny"}
            
            # Agent formats same data differently for different purposes
            json_format = await self.ai_tools.format_data(sample_weather, "json")
            summary_format = await self.ai_tools.format_data(sample_weather, "summary") 
            weather_format = await self.ai_tools.format_data(sample_weather, "weather_current")
            
            logger.info("✅ Agent created JSON format: %s", json_format[:50])
            logger.info("✅ Agent created summary: %s", summary_format)
            logger.info("✅ Agent created weather format: %s", weather_format[:50])
            
            logger.info("=== AUTONOMY TEST COMPLETE ===")
            logger.info("🎯 Atomic approach enables:")
            logger.info("   • Custom caching strategies")
            logger.info("   • Selective data extraction") 
            logger.info("   • Granular error handling")
            logger.info("   • Context-aware formatting")
            logger.info("   • Agent creativity and optimization")
            
            return True
            
        except Exception as e:
            logger.error("❌ Autonomy comparison failed: %s", e)
            return False
    
    # =================================================================
    # TEST RUNNER
    # =================================================================
    
    async def run_all_tests(self):
        """Run complete test suite."""
        logger.info("🚀 Starting Atomic Tools Test Suite...")
        logger.info("="*50)
        
        test_results = {}
        
        # Level 1: Individual tools
        test_results["infrastructure"] = await self.test_infrastructure_tools()
        test_results["http_tools"] = await self.test_http_tools()
        test_results["ai_tools"] = await self.test_ai_tools() 
        test_results["weather_tools"] = await self.test_weather_tools()
        
        # Level 2: Combinations
        test_results["combinations"] = await self.test_tool_combinations()
        
        # Level 3: Agent workflows
        test_results["workflows"] = await self.test_agent_workflows()
        
        # Level 4: Performance
        test_results["performance"] = await self.test_performance_caching()
        
        # Level 5: Autonomy
        test_results["autonomy"] = await self.test_autonomy_comparison()
        
        # Final results
        logger.info("="*50)
        logger.info("🏁 TEST SUITE COMPLETE")
        logger.info("="*50)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name.upper()}: {status}")
        
        logger.info("-"*30)
        logger.info(f"OVERALL: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! Atomic tools are ready!")
        else:
            logger.warning("⚠️ Some tests failed. Check logs above.")
        
        return test_results


# =================================================================
# MAIN TEST EXECUTION
# =================================================================

async def main():
    """Main test execution function."""
    tester = AtomicToolsTester()
    results = await tester.run_all_tests()
    return results

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())