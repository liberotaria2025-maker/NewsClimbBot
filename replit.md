# Overview

This is a Python Flask-based Twitter bot application that automatically posts weather updates, currency exchange rates, and news content to Twitter on a scheduled basis. The bot features a web dashboard for monitoring, configuration management, and API integration logging.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Core web framework with SQLAlchemy ORM for database operations
- **SQLite**: Lightweight database for storing tweets, configurations, and API logs
- **Modular Design**: Separate modules for Twitter integration, API services, and scheduling

## Database Schema
- **Tweet Model**: Stores tweet history with content, type, timestamps, and success status
- **Configuration Model**: Key-value store for bot settings and API credentials
- **ApiLog Model**: Tracks external API calls with response times and error logging

## External API Integration
- **Base APIService Class**: Common interface for external API calls with automatic logging
- **Service Classes**: WeatherService, CurrencyService, and NewsService for different content types
- **Error Handling**: Comprehensive logging and retry mechanisms for API failures

## Twitter Integration
- **Dual API Support**: Uses both Twitter API v1.1 (tweepy.API) and v2 (tweepy.Client)
- **OAuth Authentication**: Supports both environment variables and database-stored credentials
- **Rate Limiting**: Built-in respect for Twitter's rate limits

## Scheduling System
- **Background Scheduler**: Thread-based task scheduler using the `schedule` library
- **Configurable Timing**: Database-driven schedule configuration for different content types
- **Graceful Shutdown**: Proper thread management and cleanup

## Web Interface
- **Bootstrap Dashboard**: Dark-themed responsive interface with real-time statistics
- **Configuration Management**: Web forms for API credentials and scheduling settings
- **Logging Interface**: Comprehensive view of tweet history and API call logs

## Security Considerations
- **Environment Variables**: Primary credential storage method
- **Database Fallback**: Secondary credential storage for persistent configuration
- **ProxyFix Middleware**: Proper handling of proxy headers for deployment

# External Dependencies

## Twitter API
- **tweepy**: Python Twitter API wrapper
- **Required Credentials**: Consumer Key/Secret, Access Token/Token Secret
- **API Versions**: Both v1.1 and v2 support for maximum compatibility

## External APIs
- **Weather Service**: Integration for weather data (implementation details in api_services.py)
- **Currency Service**: Exchange rate API integration
- **News Service**: News content API integration

## Python Packages
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: ORM and database management
- **requests**: HTTP client for external API calls
- **schedule**: Task scheduling library
- **werkzeug**: WSGI utilities and middleware

## Frontend Dependencies
- **Bootstrap**: UI framework with dark theme
- **Font Awesome**: Icon library
- **JavaScript**: Client-side functionality and dashboard updates

## Development Environment
- **SQLite**: Development database (can be upgraded to PostgreSQL)
- **Logging**: Comprehensive file and console logging
- **Debug Mode**: Flask development server configuration