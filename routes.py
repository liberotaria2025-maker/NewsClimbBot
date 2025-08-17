from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from app import app, db
from models import Tweet, Configuration, ApiLog
from twitter_bot import TwitterBot
from api_services import WeatherService, CurrencyService, NewsService
import logging

logger = logging.getLogger(__name__)

def get_config(key, default=None):
    """Obtener configuración de la base de datos"""
    config = Configuration.query.filter_by(key=key).first()
    return config.value if config else default

def set_config(key, value, description=None):
    """Establecer configuración en la base de datos"""
    config = Configuration.query.filter_by(key=key).first()
    if config:
        config.value = value
        config.updated_at = datetime.utcnow()
    else:
        config = Configuration(key=key, value=value, description=description)
        db.session.add(config)
    db.session.commit()

@app.route('/')
def index():
    """Página principal con dashboard"""
    # Inicializar scheduler si no está iniciado
    try:
        from scheduler import init_scheduler
        init_scheduler()
    except Exception as e:
        logger.warning(f"No se pudo inicializar scheduler: {e}")
    
    # Estadísticas de tweets
    total_tweets = Tweet.query.count()
    today_tweets = Tweet.query.filter(
        Tweet.posted_at >= datetime.utcnow().date()
    ).count()
    
    successful_tweets = Tweet.query.filter_by(success=True).count()
    failed_tweets = Tweet.query.filter_by(success=False).count()
    
    # Últimos tweets
    recent_tweets = Tweet.query.order_by(Tweet.posted_at.desc()).limit(10).all()
    
    # Logs de APIs recientes
    recent_api_logs = ApiLog.query.order_by(ApiLog.created_at.desc()).limit(5).all()
    
    return render_template('index.html',
                         total_tweets=total_tweets,
                         today_tweets=today_tweets,
                         successful_tweets=successful_tweets,
                         failed_tweets=failed_tweets,
                         recent_tweets=recent_tweets,
                         recent_api_logs=recent_api_logs)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Página de configuración"""
    if request.method == 'POST':
        # Guardar configuraciones
        configs = [
            ('twitter_consumer_key', 'API Key de Twitter'),
            ('twitter_consumer_secret', 'API Secret de Twitter'),
            ('twitter_access_token', 'Access Token de Twitter'),
            ('twitter_access_token_secret', 'Access Token Secret de Twitter'),
            ('openweather_api_key', 'API Key de OpenWeatherMap'),
            ('news_api_key', 'API Key de NewsAPI'),
            ('weather_city', 'Ciudad para el clima'),
            ('currency_from', 'Moneda base (ej: USD)'),
            ('currency_to', 'Moneda destino (ej: ARS)'),
            ('news_category', 'Categoría de noticias'),
            ('news_country', 'País para noticias'),
            ('tweet_schedule_weather', 'Horarios para clima (separados por coma)'),
            ('tweet_schedule_currency', 'Horarios para moneda (separados por coma)'),
            ('tweet_schedule_news', 'Horarios para noticias (separados por coma)'),
        ]
        
        for key, description in configs:
            value = request.form.get(key, '')
            if value:
                set_config(key, value, description)
        
        flash('Configuración guardada exitosamente', 'success')
        return redirect(url_for('config'))
    
    # Obtener configuraciones actuales
    current_config = {}
    config_keys = [
        'twitter_consumer_key', 'twitter_consumer_secret', 
        'twitter_access_token', 'twitter_access_token_secret',
        'openweather_api_key', 'news_api_key',
        'weather_city', 'currency_from', 'currency_to',
        'news_category', 'news_country',
        'tweet_schedule_weather', 'tweet_schedule_currency', 'tweet_schedule_news'
    ]
    
    for key in config_keys:
        current_config[key] = get_config(key, '')
    
    return render_template('config.html', config=current_config)

@app.route('/logs')
def logs():
    """Página de logs y historial"""
    page = request.args.get('page', 1, type=int)
    tweets = Tweet.query.order_by(Tweet.posted_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    api_logs = ApiLog.query.order_by(ApiLog.created_at.desc()).limit(50).all()
    
    return render_template('logs.html', tweets=tweets, api_logs=api_logs)

@app.route('/test_tweet', methods=['POST'])
def test_tweet():
    """Endpoint para probar la publicación de tweets"""
    tweet_type = request.form.get('type')
    
    try:
        bot = TwitterBot()
        
        if tweet_type == 'weather':
            service = WeatherService()
            data = service.get_weather(get_config('weather_city', 'Buenos Aires'))
            content = bot.format_weather_tweet(data)
        elif tweet_type == 'currency':
            service = CurrencyService()
            from_currency = get_config('currency_from', 'USD')
            to_currency = get_config('currency_to', 'ARS')
            data = service.get_exchange_rate(from_currency, to_currency)
            content = bot.format_currency_tweet(data, from_currency, to_currency)
        elif tweet_type == 'news':
            service = NewsService()
            category = get_config('news_category', 'general')
            country = get_config('news_country', 'ar')
            data = service.get_news(category, country)
            content = bot.format_news_tweet(data)
        else:
            flash('Tipo de tweet inválido', 'error')
            return redirect(url_for('index'))
        
        # Publicar tweet de prueba
        success = bot.post_tweet(content)
        
        if success:
            flash(f'Tweet de prueba publicado: {content[:50]}...', 'success')
        else:
            flash('Error al publicar tweet de prueba', 'error')
            
    except Exception as e:
        logger.error(f"Error en tweet de prueba: {e}")
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    """API endpoint para estadísticas en tiempo real"""
    stats = {
        'total_tweets': Tweet.query.count(),
        'today_tweets': Tweet.query.filter(
            Tweet.posted_at >= datetime.utcnow().date()
        ).count(),
        'success_rate': 0,
        'last_tweet': None
    }
    
    total = Tweet.query.count()
    if total > 0:
        successful = Tweet.query.filter_by(success=True).count()
        stats['success_rate'] = round((successful / total) * 100, 2)
    
    last_tweet = Tweet.query.order_by(Tweet.posted_at.desc()).first()
    if last_tweet:
        stats['last_tweet'] = {
            'content': last_tweet.content[:100] + '...' if len(last_tweet.content) > 100 else last_tweet.content,
            'type': last_tweet.tweet_type,
            'posted_at': last_tweet.posted_at.strftime('%H:%M:%S')
        }
    
    return jsonify(stats)
