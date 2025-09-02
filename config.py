# Configuration settings for SEO Bot
import os

# API Keys (keep empty for free version)
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY', '')

# Free AI API endpoints
FREE_AI_ENDPOINTS = {
    'huggingface': 'https://api-inference.huggingface.co/models/',
    'local': 'http://localhost:1234/v1/chat/completions'  # For LMStudio
}

# Default settings
DEFAULT_CRAWL_LIMIT = 10
DEFAULT_TIMEOUT = 30
USER_AGENT = 'SEO-Bot/1.0 (Educational Purpose)'

# Output settings
OUTPUT_DIR = 'results'
REPORT_FORMAT = 'json'  # json, csv, html

