"""
Geocoding Service - GPS to Address Conversion
Handles reverse geocoding and address autocomplete
"""
import os
import logging
from typing import Dict, Optional, List
import aiohttp

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding operations"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        if not self.google_api_key:
            logger.warning("Google Maps API key not configured")
    
    async def reverse_geocode(self, lat: float, lng: float) -> Dict:
        """
        Convert GPS coordinates to address
        
        Args:
            lat: Latitude
            lng: Longitude
        
        Returns:
            {
                "street": "Möwenstraße",
                "house_number": "2",
                "postal_code": "25462",
                "city": "Rellingen",
                "country": "DE",
                "formatted": "Möwenstraße 2, 25462 Rellingen"
            }
        """
        if not self.google_api_key:
            return {"error": "API key not configured"}
        
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "latlng": f"{lat},{lng}",
                "key": self.google_api_key,
                "language": "de",
                "result_type": "street_address|premise"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=8) as response:
                    if response.status != 200:
                        logger.error(f"Geocoding API error: {response.status}")
                        return {"error": "API request failed"}
                    
                    data = await response.json()
                    
                    if data.get('status') != 'OK' or not data.get('results'):
                        logger.warning(f"No results from geocoding: {data.get('status')}")
                        return {"error": "No address found"}
                    
                    # Parse first result
                    result = data['results'][0]
                    components = {c['types'][0]: c for c in result['address_components']}
                    
                    # Extract address parts
                    street = components.get('route', {}).get('long_name', '')
                    house_number = components.get('street_number', {}).get('long_name', '')
                    postal_code = components.get('postal_code', {}).get('long_name', '')
                    city = components.get('locality', {}).get('long_name', '')
                    
                    # Fallbacks
                    if not city:
                        city = components.get('administrative_area_level_3', {}).get('long_name', '')
                    if not city:
                        city = components.get('administrative_area_level_2', {}).get('long_name', '')
                    
                    return {
                        "success": True,
                        "street": street,
                        "house_number": house_number,
                        "postal_code": postal_code,
                        "city": city,
                        "country": "DE",
                        "formatted": result.get('formatted_address', ''),
                        "coordinates": {
                            "lat": lat,
                            "lng": lng
                        }
                    }
        
        except asyncio.TimeoutError:
            logger.error("Geocoding request timeout")
            return {"error": "Request timeout"}
        except Exception as e:
            logger.error(f"Reverse geocode error: {str(e)}")
            return {"error": str(e)}
    
    async def autocomplete_address(self, input_text: str, location_bias: Dict = None) -> List[Dict]:
        """
        Get address suggestions based on input
        
        Args:
            input_text: User input
            location_bias: Optional {"lat": 53.6, "lng": 9.8} for better results
        
        Returns:
            List of address suggestions
        """
        if not self.google_api_key:
            return []
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
            params = {
                "input": input_text,
                "key": self.google_api_key,
                "language": "de",
                "components": "country:de",
                "types": "address"
            }
            
            if location_bias:
                params["location"] = f"{location_bias['lat']},{location_bias['lng']}"
                params["radius"] = "50000"  # 50km
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    
                    if data.get('status') != 'OK':
                        return []
                    
                    return [
                        {
                            "place_id": p['place_id'],
                            "description": p['description'],
                            "main_text": p['structured_formatting']['main_text'],
                            "secondary_text": p['structured_formatting'].get('secondary_text', '')
                        }
                        for p in data.get('predictions', [])
                    ]
        
        except Exception as e:
            logger.error(f"Autocomplete error: {str(e)}")
            return []
