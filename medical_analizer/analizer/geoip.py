# analizer/geo_utils.py
import geoip2.database
import os
from django.conf import settings

def get_region_from_ip(ip_address):
    try:
        # Указываем прямой путь к файлу
        geoip_path = os.path.join(settings.BASE_DIR, 'analizer/geoip_data/GeoLite2-City.mmdb')
        with geoip2.database.Reader(geoip_path) as reader:
            response = reader.city(ip_address)
            return {
                'country': response.country.name,
                'city': response.city.name
            }
    except Exception as e:
        print(f"GeoIP error: {str(e)}")  # Для логирования ошибок
        return {'country': 'Unknown', 'city': 'Unknown'}
