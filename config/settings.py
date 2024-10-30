import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Data files
CITY_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cities.csv')
GA4_DATA_PATH = os.path.join(BASE_DIR, 'data', 'ga4data.csv')

# API Keys (load from environment variables in production)
SERPER_API_KEY = os.getenv('SERPER_API_KEY', '')
SEMRUSH_API_KEY = os.getenv('SEMRUSH_API_KEY', '')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}