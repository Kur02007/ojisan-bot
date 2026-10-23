"""Redact configured secrets before messages reach stream or Discord handlers."""
import logging
import traceback
from urllib.parse import unquote, urlsplit


def install_secret_redaction(config):
    if getattr(logging.getLogRecordFactory(), '_ojisan_redaction', False):
        return
    previous = logging.getLogRecordFactory()

    def redact(value):
        text = str(value)
        names = ('DISCORD_BOT_TOKEN', 'YOUTUBE_API_KEY', 'YOUTUBE_WEBHOOK_SECRET',
                 'TWITCH_CLIENT_SECRET', 'TWITCH_WEBHOOK_SECRET', 'ADMIN_API_KEY',
                 'DATABASE_URL', 'CELERY_BROKER_URL')
        secrets = [getattr(config, name, None) for name in names]
        for name in ('DATABASE_URL', 'CELERY_BROKER_URL'):
            try:
                password = urlsplit(getattr(config, name, '') or '').password
                if password:
                    secrets.extend((password, unquote(password)))
            except ValueError:
                pass
        for secret in sorted({s for s in secrets if s}, key=len, reverse=True):
            text = text.replace(secret, '[REDACTED]')
        return text

    def factory(*args, **kwargs):
        record = previous(*args, **kwargs)
        record.msg = redact(record.getMessage())
        record.args = ()
        if record.exc_info:
            record.exc_text = redact(''.join(traceback.format_exception(*record.exc_info)))
        if record.stack_info:
            record.stack_info = redact(record.stack_info)
        return record

    factory._ojisan_redaction = True
    logging.setLogRecordFactory(factory)
