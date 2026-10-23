import io
import logging
import unittest
from unittest.mock import patch
from ojisan.core.config import Config


class LogSecurity(unittest.TestCase):
    def test_configured_secret_redacted_in_message_and_traceback(self):
        stream=io.StringIO()
        handler=logging.StreamHandler(stream)
        logger=logging.getLogger('ojisan-security-test')
        logger.addHandler(handler)
        try:
            with patch.object(Config,'TWITCH_CLIENT_SECRET','offline-private-value'):
                try:
                    raise ValueError('offline-private-value')
                except ValueError:
                    logger.error('Rejected %s', 'offline-private-value', exc_info=True)
            self.assertNotIn('offline-private-value',stream.getvalue())
            self.assertIn('[REDACTED]',stream.getvalue())
        finally:
            logger.removeHandler(handler)

    def test_raw_logs_off_by_default_do_not_create_files(self):
        from ojisan.platforms.youtube import feed_logger
        with patch.object(Config,'ENABLE_RAW_FEED_LOGS',False), patch('builtins.open') as output:
            feed_logger.append_raw_feed_log('<feed/>')
            feed_logger.append_structured_feed_log({'raw_xml':'<feed/>'})
            output.assert_not_called()
