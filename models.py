from datetime import datetime
from app import db

class Tweet(db.Model):
    """Modelo para almacenar el historial de tweets publicados"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    tweet_type = db.Column(db.String(50), nullable=False)  # 'news', 'weather', 'currency'
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Tweet {self.id}: {self.tweet_type}>'

class Configuration(db.Model):
    """Modelo para almacenar configuraciones del bot"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.key}: {self.value}>'

class ApiLog(db.Model):
    """Modelo para logs de llamadas a APIs"""
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(200))
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ApiLog {self.api_name}: {self.status_code}>'
