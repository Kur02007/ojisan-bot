"""Safe defaults and a network guard for the complete pytest suite."""
import os
from unittest.mock import patch
import pytest

for key in list(os.environ):
    if key.startswith(("DISCORD_", "YOUTUBE_", "TWITCH_", "ADMIN_")):
        del os.environ[key]
os.environ.update(
    DISCORD_BOT_TOKEN="test", DATABASE_URL="sqlite://",
    CELERY_BROKER_URL="memory://", YOUTUBE_WEBHOOK_SECRET="test-secret",
    CALLBACK_URL="https://example.invalid/webhook/youtube",
    PYTHON_DOTENV_DISABLED="1",
)


@pytest.fixture(autouse=True)
def no_external_http():
    with patch("requests.sessions.Session.request", side_effect=AssertionError("External HTTP forbidden")):
        yield
