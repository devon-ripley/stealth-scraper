"""
Geo-location sync for proxy-based location matching.

Maps country codes to StealthLocation presets for consistent
timezone, geolocation, and locale when using geo-targeted proxies.
"""

from typing import Optional, Dict
import sys
import os

# Import StealthLocation from parent module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ..config import StealthLocation


# Comprehensive country code to location mapping
COUNTRY_LOCATIONS: Dict[str, StealthLocation] = {
    # North America
    "US": StealthLocation(
        timezone="America/New_York",
        latitude=40.7128,
        longitude=-74.0060,
        locale="en-US",
        languages=["en-US", "en"],
    ),
    "CA": StealthLocation(
        timezone="America/Toronto",
        latitude=43.6532,
        longitude=-79.3832,
        locale="en-CA",
        languages=["en-CA", "en", "fr-CA"],
    ),
    "MX": StealthLocation(
        timezone="America/Mexico_City",
        latitude=19.4326,
        longitude=-99.1332,
        locale="es-MX",
        languages=["es-MX", "es", "en"],
    ),

    # Europe
    "GB": StealthLocation(
        timezone="Europe/London",
        latitude=51.5074,
        longitude=-0.1278,
        locale="en-GB",
        languages=["en-GB", "en"],
    ),
    "UK": StealthLocation(  # Alias for GB
        timezone="Europe/London",
        latitude=51.5074,
        longitude=-0.1278,
        locale="en-GB",
        languages=["en-GB", "en"],
    ),
    "DE": StealthLocation(
        timezone="Europe/Berlin",
        latitude=52.5200,
        longitude=13.4050,
        locale="de-DE",
        languages=["de-DE", "de", "en"],
    ),
    "FR": StealthLocation(
        timezone="Europe/Paris",
        latitude=48.8566,
        longitude=2.3522,
        locale="fr-FR",
        languages=["fr-FR", "fr", "en"],
    ),
    "ES": StealthLocation(
        timezone="Europe/Madrid",
        latitude=40.4168,
        longitude=-3.7038,
        locale="es-ES",
        languages=["es-ES", "es", "en"],
    ),
    "IT": StealthLocation(
        timezone="Europe/Rome",
        latitude=41.9028,
        longitude=12.4964,
        locale="it-IT",
        languages=["it-IT", "it", "en"],
    ),
    "NL": StealthLocation(
        timezone="Europe/Amsterdam",
        latitude=52.3676,
        longitude=4.9041,
        locale="nl-NL",
        languages=["nl-NL", "nl", "en"],
    ),
    "BE": StealthLocation(
        timezone="Europe/Brussels",
        latitude=50.8503,
        longitude=4.3517,
        locale="nl-BE",
        languages=["nl-BE", "fr-BE", "en"],
    ),
    "CH": StealthLocation(
        timezone="Europe/Zurich",
        latitude=47.3769,
        longitude=8.5417,
        locale="de-CH",
        languages=["de-CH", "fr-CH", "it-CH", "en"],
    ),
    "AT": StealthLocation(
        timezone="Europe/Vienna",
        latitude=48.2082,
        longitude=16.3738,
        locale="de-AT",
        languages=["de-AT", "de", "en"],
    ),
    "PL": StealthLocation(
        timezone="Europe/Warsaw",
        latitude=52.2297,
        longitude=21.0122,
        locale="pl-PL",
        languages=["pl-PL", "pl", "en"],
    ),
    "SE": StealthLocation(
        timezone="Europe/Stockholm",
        latitude=59.3293,
        longitude=18.0686,
        locale="sv-SE",
        languages=["sv-SE", "sv", "en"],
    ),
    "NO": StealthLocation(
        timezone="Europe/Oslo",
        latitude=59.9139,
        longitude=10.7522,
        locale="nb-NO",
        languages=["nb-NO", "no", "en"],
    ),
    "DK": StealthLocation(
        timezone="Europe/Copenhagen",
        latitude=55.6761,
        longitude=12.5683,
        locale="da-DK",
        languages=["da-DK", "da", "en"],
    ),
    "FI": StealthLocation(
        timezone="Europe/Helsinki",
        latitude=60.1699,
        longitude=24.9384,
        locale="fi-FI",
        languages=["fi-FI", "fi", "en"],
    ),
    "PT": StealthLocation(
        timezone="Europe/Lisbon",
        latitude=38.7223,
        longitude=-9.1393,
        locale="pt-PT",
        languages=["pt-PT", "pt", "en"],
    ),
    "IE": StealthLocation(
        timezone="Europe/Dublin",
        latitude=53.3498,
        longitude=-6.2603,
        locale="en-IE",
        languages=["en-IE", "en", "ga"],
    ),
    "RU": StealthLocation(
        timezone="Europe/Moscow",
        latitude=55.7558,
        longitude=37.6173,
        locale="ru-RU",
        languages=["ru-RU", "ru", "en"],
    ),

    # Asia-Pacific
    "JP": StealthLocation(
        timezone="Asia/Tokyo",
        latitude=35.6895,
        longitude=139.6917,
        locale="ja-JP",
        languages=["ja-JP", "ja", "en"],
    ),
    "KR": StealthLocation(
        timezone="Asia/Seoul",
        latitude=37.5665,
        longitude=126.9780,
        locale="ko-KR",
        languages=["ko-KR", "ko", "en"],
    ),
    "CN": StealthLocation(
        timezone="Asia/Shanghai",
        latitude=31.2304,
        longitude=121.4737,
        locale="zh-CN",
        languages=["zh-CN", "zh", "en"],
    ),
    "TW": StealthLocation(
        timezone="Asia/Taipei",
        latitude=25.0330,
        longitude=121.5654,
        locale="zh-TW",
        languages=["zh-TW", "zh", "en"],
    ),
    "HK": StealthLocation(
        timezone="Asia/Hong_Kong",
        latitude=22.3193,
        longitude=114.1694,
        locale="zh-HK",
        languages=["zh-HK", "zh", "en"],
    ),
    "SG": StealthLocation(
        timezone="Asia/Singapore",
        latitude=1.3521,
        longitude=103.8198,
        locale="en-SG",
        languages=["en-SG", "en", "zh", "ms"],
    ),
    "IN": StealthLocation(
        timezone="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
        locale="en-IN",
        languages=["en-IN", "hi-IN", "en"],
    ),
    "AU": StealthLocation(
        timezone="Australia/Sydney",
        latitude=-33.8688,
        longitude=151.2093,
        locale="en-AU",
        languages=["en-AU", "en"],
    ),
    "NZ": StealthLocation(
        timezone="Pacific/Auckland",
        latitude=-36.8485,
        longitude=174.7633,
        locale="en-NZ",
        languages=["en-NZ", "en", "mi"],
    ),
    "TH": StealthLocation(
        timezone="Asia/Bangkok",
        latitude=13.7563,
        longitude=100.5018,
        locale="th-TH",
        languages=["th-TH", "th", "en"],
    ),
    "VN": StealthLocation(
        timezone="Asia/Ho_Chi_Minh",
        latitude=10.8231,
        longitude=106.6297,
        locale="vi-VN",
        languages=["vi-VN", "vi", "en"],
    ),
    "ID": StealthLocation(
        timezone="Asia/Jakarta",
        latitude=-6.2088,
        longitude=106.8456,
        locale="id-ID",
        languages=["id-ID", "id", "en"],
    ),
    "MY": StealthLocation(
        timezone="Asia/Kuala_Lumpur",
        latitude=3.1390,
        longitude=101.6869,
        locale="ms-MY",
        languages=["ms-MY", "en-MY", "zh"],
    ),
    "PH": StealthLocation(
        timezone="Asia/Manila",
        latitude=14.5995,
        longitude=120.9842,
        locale="en-PH",
        languages=["en-PH", "tl-PH", "en"],
    ),

    # South America
    "BR": StealthLocation(
        timezone="America/Sao_Paulo",
        latitude=-23.5505,
        longitude=-46.6333,
        locale="pt-BR",
        languages=["pt-BR", "pt", "en"],
    ),
    "AR": StealthLocation(
        timezone="America/Argentina/Buenos_Aires",
        latitude=-34.6037,
        longitude=-58.3816,
        locale="es-AR",
        languages=["es-AR", "es", "en"],
    ),
    "CL": StealthLocation(
        timezone="America/Santiago",
        latitude=-33.4489,
        longitude=-70.6693,
        locale="es-CL",
        languages=["es-CL", "es", "en"],
    ),
    "CO": StealthLocation(
        timezone="America/Bogota",
        latitude=4.7110,
        longitude=-74.0721,
        locale="es-CO",
        languages=["es-CO", "es", "en"],
    ),

    # Middle East
    "AE": StealthLocation(
        timezone="Asia/Dubai",
        latitude=25.2048,
        longitude=55.2708,
        locale="ar-AE",
        languages=["ar-AE", "en"],
    ),
    "IL": StealthLocation(
        timezone="Asia/Jerusalem",
        latitude=31.7683,
        longitude=35.2137,
        locale="he-IL",
        languages=["he-IL", "he", "en"],
    ),
    "SA": StealthLocation(
        timezone="Asia/Riyadh",
        latitude=24.7136,
        longitude=46.6753,
        locale="ar-SA",
        languages=["ar-SA", "ar", "en"],
    ),
    "TR": StealthLocation(
        timezone="Europe/Istanbul",
        latitude=41.0082,
        longitude=28.9784,
        locale="tr-TR",
        languages=["tr-TR", "tr", "en"],
    ),

    # Africa
    "ZA": StealthLocation(
        timezone="Africa/Johannesburg",
        latitude=-33.9249,
        longitude=18.4241,
        locale="en-ZA",
        languages=["en-ZA", "en", "af", "zu"],
    ),
    "EG": StealthLocation(
        timezone="Africa/Cairo",
        latitude=30.0444,
        longitude=31.2357,
        locale="ar-EG",
        languages=["ar-EG", "ar", "en"],
    ),
    "NG": StealthLocation(
        timezone="Africa/Lagos",
        latitude=6.5244,
        longitude=3.3792,
        locale="en-NG",
        languages=["en-NG", "en"],
    ),
}


def get_location_for_country(country_code: Optional[str]) -> Optional[StealthLocation]:
    """
    Get StealthLocation for a country code.

    Args:
        country_code: ISO 3166-1 alpha-2 code (e.g., "US", "GB", "JP")

    Returns:
        StealthLocation if country is mapped, None otherwise
    """
    if not country_code:
        return None

    # Normalize to uppercase
    code = country_code.upper().strip()
    return COUNTRY_LOCATIONS.get(code)


def get_supported_countries() -> list:
    """Get list of all supported country codes."""
    return sorted(COUNTRY_LOCATIONS.keys())
