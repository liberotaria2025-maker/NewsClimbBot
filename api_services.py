import os
import requests
import logging
from datetime import datetime
from app import db
from models import ApiLog

logger = logging.getLogger(__name__)

class APIService:
    """Clase base para servicios de API"""
    
    def __init__(self, api_name):
        self.api_name = api_name
    
    def _log_api_call(self, endpoint, status_code, response_time, error_message=None):
        """Registrar llamada a API en la base de datos"""
        try:
            log = ApiLog(
                api_name=self.api_name,
                endpoint=endpoint,
                status_code=status_code,
                response_time=response_time,
                error_message=error_message
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error registrando log de API: {e}")
    
    def _make_request(self, url, params=None, headers=None):
        """Realizar petición HTTP con logging"""
        start_time = datetime.now()
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response_time = (datetime.now() - start_time).total_seconds()
            
            self._log_api_call(
                endpoint=url,
                status_code=response.status_code,
                response_time=response_time
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            response_time = (datetime.now() - start_time).total_seconds()
            status_code = getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0
            
            self._log_api_call(
                endpoint=url,
                status_code=status_code,
                response_time=response_time,
                error_message=str(e)
            )
            
            logger.error(f"Error en petición a {url}: {e}")
            return None

class WeatherService(APIService):
    """Servicio para obtener información del clima"""
    
    def __init__(self):
        super().__init__('OpenWeatherMap')
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
    
    def get_weather(self, city):
        """Obtener clima actual de una ciudad"""
        # Intentar obtener API key de configuración si no está en env
        if not self.api_key:
            try:
                from routes import get_config
                self.api_key = get_config('openweather_api_key')
            except:
                pass
        
        if not self.api_key:
            logger.error("API key de OpenWeatherMap no configurada")
            return None
        
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'es'
        }
        
        data = self._make_request(url, params)
        if data:
            logger.info(f"Clima obtenido para {city}")
        
        return data
    
    def get_forecast(self, city, days=5):
        """Obtener pronóstico del clima"""
        if not self.api_key:
            logger.error("API key de OpenWeatherMap no configurada")
            return None
        
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'es',
            'cnt': days * 8  # 8 pronósticos por día (cada 3 horas)
        }
        
        return self._make_request(url, params)

class CurrencyService(APIService):
    """Servicio para obtener cotizaciones de monedas"""
    
    def __init__(self):
        super().__init__('ExchangeRate-API')
        self.base_url = 'https://v6.exchangerate-api.com/v6'
        # ExchangeRate-API tiene un tier gratuito sin API key requerida
        self.api_key = os.getenv('EXCHANGE_API_KEY', 'free')
    
    def get_exchange_rate(self, from_currency, to_currency):
        """Obtener tasa de cambio entre dos monedas"""
        if self.api_key == 'free':
            # Usar endpoint gratuito
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        else:
            url = f"{self.base_url}/{self.api_key}/latest/{from_currency}"
        
        data = self._make_request(url)
        
        if data and 'rates' in data:
            rate = data['rates'].get(to_currency)
            if rate:
                logger.info(f"Cotización obtenida: {from_currency}/{to_currency} = {rate}")
                return {'conversion_rate': rate}
        
        logger.error(f"No se pudo obtener cotización {from_currency}/{to_currency}")
        return None
    
    def get_historical_rate(self, from_currency, to_currency, date):
        """Obtener tasa de cambio histórica"""
        if self.api_key == 'free':
            logger.warning("Cotizaciones históricas no disponibles en tier gratuito")
            return None
        
        url = f"{self.base_url}/{self.api_key}/history/{from_currency}/{date}"
        return self._make_request(url)

class NewsService(APIService):
    """Servicio para obtener noticias"""
    
    def __init__(self):
        super().__init__('NewsAPI')
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2'
    
    def get_news(self, category='general', country='ar', page_size=5):
        """Obtener noticias principales"""
        # Intentar obtener API key de configuración si no está en env
        if not self.api_key:
            try:
                from routes import get_config
                self.api_key = get_config('news_api_key')
            except:
                pass
        
        if not self.api_key:
            logger.error("API key de NewsAPI no configurada")
            return None
        
        url = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'category': category,
            'country': country,
            'pageSize': page_size
        }
        
        data = self._make_request(url, params)
        if data:
            logger.info(f"Noticias obtenidas: {len(data.get('articles', []))} artículos")
        
        return data
    
    def search_news(self, query, language='es', sort_by='publishedAt'):
        """Buscar noticias por término"""
        if not self.api_key:
            logger.error("API key de NewsAPI no configurada")
            return None
        
        url = f"{self.base_url}/everything"
        params = {
            'apiKey': self.api_key,
            'q': query,
            'language': language,
            'sortBy': sort_by,
            'pageSize': 5
        }
        
        return self._make_request(url, params)
