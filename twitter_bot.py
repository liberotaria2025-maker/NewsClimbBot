import os
import logging
import tweepy
from datetime import datetime
from app import db
from models import Tweet, ApiLog

logger = logging.getLogger(__name__)

class TwitterBot:
    """Clase principal para manejar la integración con Twitter"""
    
    def __init__(self):
        self.consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
        self.consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.api = None
        self.client = None
        
        # Solo cargar credenciales de base de datos si estamos dentro del contexto Flask
        self._load_credentials_safely()
        self._authenticate()
    
    def _load_credentials_safely(self):
        """Cargar credenciales de la base de datos solo si estamos en contexto Flask"""
        try:
            from flask import current_app
            # Verificar si estamos en un contexto de aplicación Flask
            if current_app:
                # Solo cargar de BD si no tenemos credenciales de variables de entorno
                if not self.consumer_key:
                    from routes import get_config
                    self.consumer_key = get_config('twitter_consumer_key')
                    self.consumer_secret = get_config('twitter_consumer_secret')
                    self.access_token = get_config('twitter_access_token')
                    self.access_token_secret = get_config('twitter_access_token_secret')
        except Exception:
            # Si no estamos en contexto Flask o hay error, usar solo variables de entorno
            logger.info("Usando solo credenciales de variables de entorno")
    
    def _authenticate(self):
        """Autenticar con la API de Twitter"""
        try:
            if not all([self.consumer_key, self.consumer_secret, 
                       self.access_token, self.access_token_secret]):
                logger.error("Credenciales de Twitter incompletas")
                return False
            
            # Autenticación OAuth 1.0a para API v1.1
            auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Cliente para API v2
            self.client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Verificar credenciales
            self.api.verify_credentials()
            logger.info("Autenticación con Twitter exitosa")
            return True
            
        except Exception as e:
            logger.error(f"Error en autenticación de Twitter: {e}")
            return False
    
    def post_tweet(self, content, tweet_type="manual"):
        """Publicar un tweet"""
        try:
            if not self.client:
                logger.error("Cliente de Twitter no inicializado")
                return False
            
            # Limitar a 280 caracteres
            if len(content) > 280:
                content = content[:277] + "..."
            
            response = self.client.create_tweet(text=content)
            
            # Guardar en base de datos
            tweet = Tweet(
                content=content,
                tweet_type=tweet_type,
                success=True,
                posted_at=datetime.utcnow()
            )
            db.session.add(tweet)
            db.session.commit()
            
            logger.info(f"Tweet publicado exitosamente: {content[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error al publicar tweet: {e}")
            
            # Guardar error en base de datos
            tweet = Tweet(
                content=content,
                tweet_type=tweet_type,
                success=False,
                error_message=str(e),
                posted_at=datetime.utcnow()
            )
            db.session.add(tweet)
            db.session.commit()
            
            return False
    
    def format_weather_tweet(self, weather_data):
        """Formatear tweet de clima"""
        if not weather_data:
            return "❌ No se pudo obtener información del clima"
        
        try:
            city = weather_data.get('name', 'Ciudad')
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description'].title()
            
            # Emoji según el clima
            weather_main = weather_data['weather'][0]['main'].lower()
            emoji = self._get_weather_emoji(weather_main)
            
            tweet = f"{emoji} Clima en {city}\n"
            tweet += f"🌡️ {temp}°C (sensación: {feels_like}°C)\n"
            tweet += f"💧 Humedad: {humidity}%\n"
            tweet += f"☁️ {description}\n"
            tweet += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formateando tweet de clima: {e}")
            return "❌ Error al formatear información del clima"
    
    def format_currency_tweet(self, rate_data, from_currency, to_currency):
        """Formatear tweet de cotización"""
        if not rate_data:
            return f"❌ No se pudo obtener cotización {from_currency}/{to_currency}"
        
        try:
            rate = rate_data.get('conversion_rate') or rate_data.get('rate')
            if not rate:
                return f"❌ Datos de cotización inválidos para {from_currency}/{to_currency}"
            
            # Emojis según la moneda
            currency_emojis = {
                'USD': '💵', 'EUR': '💶', 'ARS': '🇦🇷', 
                'BRL': '🇧🇷', 'GBP': '💷', 'JPY': '💴'
            }
            
            from_emoji = currency_emojis.get(from_currency, '💰')
            to_emoji = currency_emojis.get(to_currency, '💰')
            
            tweet = f"{from_emoji} Cotización {from_currency}/{to_currency}\n"
            tweet += f"💱 1 {from_currency} = {rate:.2f} {to_currency}\n"
            
            # Añadir contexto para monedas populares
            if from_currency == 'USD' and to_currency == 'ARS':
                tweet += f"💸 Dólar Blue estimado\n"
            
            tweet += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formateando tweet de moneda: {e}")
            return f"❌ Error al formatear cotización {from_currency}/{to_currency}"
    
    def format_news_tweet(self, news_data):
        """Formatear tweet de noticias"""
        if not news_data or not news_data.get('articles'):
            return "❌ No se pudieron obtener noticias"
        
        try:
            article = news_data['articles'][0]  # Tomar la primera noticia
            title = article['title']
            source = article.get('source', {}).get('name', 'Fuente')
            url = article.get('url', '')
            
            # Truncar título si es muy largo
            max_title_length = 200  # Dejar espacio para otros elementos
            if len(title) > max_title_length:
                title = title[:max_title_length-3] + "..."
            
            tweet = f"📰 {title}\n"
            tweet += f"🔗 Fuente: {source}\n"
            
            if url:
                tweet += f"\n{url}"
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formateando tweet de noticias: {e}")
            return "❌ Error al formatear noticias"
    
    def _get_weather_emoji(self, weather_main):
        """Obtener emoji según el tipo de clima"""
        weather_emojis = {
            'clear': '☀️',
            'clouds': '☁️',
            'rain': '🌧️',
            'drizzle': '🌦️',
            'thunderstorm': '⛈️',
            'snow': '❄️',
            'mist': '🌫️',
            'fog': '🌫️',
            'haze': '🌫️'
        }
        return weather_emojis.get(weather_main, '🌤️')
