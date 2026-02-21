import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 1
timeout = 30
keepalive = 5
loglevel = 'info'
accesslog = '-'
errorlog = '-'
