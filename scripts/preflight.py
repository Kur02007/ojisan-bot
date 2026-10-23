"""Validate a service environment without printing values or opening connections."""
import os
from urllib.parse import urlsplit
from dotenv import load_dotenv

load_dotenv()
errors=[]
for name in ('DISCORD_BOT_TOKEN','DATABASE_URL','CELERY_BROKER_URL',
             'YOUTUBE_WEBHOOK_SECRET','POSTGRES_PASSWORD'):
    value=os.getenv(name,'').strip()
    if not value or value in ('test','password','changeme'):
        errors.append(name+': missing or unsafe sample value')
url=os.getenv('CALLBACK_URL','')
if not url.startswith('https://') or '.invalid' in url:
    errors.append('CALLBACK_URL: configure a dedicated HTTPS development callback')
twitch=('TWITCH_CLIENT_ID','TWITCH_CLIENT_SECRET','TWITCH_WEBHOOK_SECRET','TWITCH_CALLBACK_URL')
if any(os.getenv(k) for k in twitch) and not all(os.getenv(k) for k in twitch):
    errors.append('Twitch: all four settings are required together')
if all(os.getenv(k) for k in twitch):
    secret=os.environ['TWITCH_WEBHOOK_SECRET']
    callback=os.environ['TWITCH_CALLBACK_URL']
    parsed=urlsplit(callback)
    try: valid_port=parsed.port in (None,443)
    except ValueError: valid_port=False
    if not (10<=len(secret)<=100 and secret.isascii()):errors.append('TWITCH_WEBHOOK_SECRET: invalid format')
    if parsed.scheme!='https' or not valid_port or not parsed.hostname or '.invalid' in callback:
        errors.append('TWITCH_CALLBACK_URL: valid HTTPS/443 callback required')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('Required service configuration is present; no connection was made.')
