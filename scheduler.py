import schedule
import time
import threading
import logging
from datetime import datetime
from twitter_bot import TwitterBot
from api_services import WeatherService, CurrencyService, NewsService

logger = logging.getLogger(__name__)

class BotScheduler:
    """Manejador de tareas programadas para el bot"""
    
    def __init__(self):
        self.bot = TwitterBot()
        self.weather_service = WeatherService()
        self.currency_service = CurrencyService()
        self.news_service = NewsService()
        self.running = False
        self.thread = None
    
    def start(self):
        """Iniciar el scheduler"""
        if self.running:
            return
        
        self.running = True
        self._setup_schedules()
        
        # Ejecutar en thread separado
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Scheduler iniciado")
    
    def stop(self):
        """Detener el scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler detenido")
    
    def _setup_schedules(self):
        """Configurar horarios de publicación"""
        from routes import get_config
        
        # Limpiar schedules anteriores
        schedule.clear()
        
        # Configurar tweets de clima
        weather_times = get_config('tweet_schedule_weather', '08:00,14:00,20:00')
        for time_str in weather_times.split(','):
            time_str = time_str.strip()
            if time_str:
                schedule.every().day.at(time_str).do(self.post_weather_tweet)
                logger.info(f"Programado tweet de clima a las {time_str}")
        
        # Configurar tweets de moneda
        currency_times = get_config('tweet_schedule_currency', '09:00,15:00')
        for time_str in currency_times.split(','):
            time_str = time_str.strip()
            if time_str:
                schedule.every().day.at(time_str).do(self.post_currency_tweet)
                logger.info(f"Programado tweet de moneda a las {time_str}")
        
        # Configurar tweets de noticias
        news_times = get_config('tweet_schedule_news', '12:00,18:00')
        for time_str in news_times.split(','):
            time_str = time_str.strip()
            if time_str:
                schedule.every().day.at(time_str).do(self.post_news_tweet)
                logger.info(f"Programado tweet de noticias a las {time_str}")
    
    def _run_scheduler(self):
        """Ejecutar el loop del scheduler"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                logger.error(f"Error en scheduler: {e}")
                time.sleep(60)
    
    def post_weather_tweet(self):
        """Publicar tweet de clima programado"""
        try:
            from routes import get_config
            city = get_config('weather_city', 'Buenos Aires')
            
            weather_data = self.weather_service.get_weather(city)
            if weather_data:
                content = self.bot.format_weather_tweet(weather_data)
                success = self.bot.post_tweet(content, 'weather')
                
                if success:
                    logger.info(f"Tweet de clima publicado: {city}")
                else:
                    logger.error(f"Error publicando tweet de clima: {city}")
            else:
                logger.error(f"No se pudo obtener datos de clima para {city}")
                
        except Exception as e:
            logger.error(f"Error en tweet programado de clima: {e}")
    
    def post_currency_tweet(self):
        """Publicar tweet de moneda programado"""
        try:
            from routes import get_config
            from_currency = get_config('currency_from', 'USD')
            to_currency = get_config('currency_to', 'ARS')
            
            rate_data = self.currency_service.get_exchange_rate(from_currency, to_currency)
            if rate_data:
                content = self.bot.format_currency_tweet(rate_data, from_currency, to_currency)
                success = self.bot.post_tweet(content, 'currency')
                
                if success:
                    logger.info(f"Tweet de moneda publicado: {from_currency}/{to_currency}")
                else:
                    logger.error(f"Error publicando tweet de moneda: {from_currency}/{to_currency}")
            else:
                logger.error(f"No se pudo obtener cotización {from_currency}/{to_currency}")
                
        except Exception as e:
            logger.error(f"Error en tweet programado de moneda: {e}")
    
    def post_news_tweet(self):
        """Publicar tweet de noticias programado"""
        try:
            from routes import get_config
            category = get_config('news_category', 'general')
            country = get_config('news_country', 'ar')
            
            news_data = self.news_service.get_news(category, country)
            if news_data:
                content = self.bot.format_news_tweet(news_data)
                success = self.bot.post_tweet(content, 'news')
                
                if success:
                    logger.info(f"Tweet de noticias publicado: {category}")
                else:
                    logger.error(f"Error publicando tweet de noticias: {category}")
            else:
                logger.error(f"No se pudieron obtener noticias de {category}")
                
        except Exception as e:
            logger.error(f"Error en tweet programado de noticias: {e}")
    
    def refresh_schedules(self):
        """Refrescar configuración de horarios"""
        if self.running:
            self._setup_schedules()
            logger.info("Horarios de publicación actualizados")

# Instancia global del scheduler
bot_scheduler = None

def init_scheduler():
    """Inicializar el scheduler"""
    global bot_scheduler
    if bot_scheduler is None:
        bot_scheduler = BotScheduler()
    bot_scheduler.start()

def refresh_scheduler():
    """Refrescar la configuración del scheduler"""
    if bot_scheduler is not None:
        bot_scheduler.refresh_schedules()
