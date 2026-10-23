"""Public service contracts after module relocation; never connects to Discord."""
import os
os.environ.update(DISCORD_BOT_TOKEN="test", DATABASE_URL="sqlite://",
                  CELERY_BROKER_URL="memory://", PYTHON_DOTENV_DISABLED="1",
                  YOUTUBE_WEBHOOK_SECRET="test-secret")
import ast
import hashlib
import hmac
import importlib
from pathlib import Path
import unittest
from unittest.mock import patch
from fastapi import HTTPException


class PackagingContracts(unittest.TestCase):
    def test_every_module_imports_without_network_or_database_connection(self):
        import ojisan
        with patch('requests.sessions.Session.request', side_effect=AssertionError('Network forbidden')):
            for file in Path(ojisan.__file__).parent.rglob('*.py'):
                if file.name == '__init__.py': continue
                module = 'ojisan.' + '.'.join(file.relative_to(Path(ojisan.__file__).parent).with_suffix('').parts)
                importlib.import_module(module)

    def test_legacy_celery_names_and_schedule_targets(self):
        from ojisan.workers.celery_app import celery_app
        from ojisan.workers import youtube_tasks, twitch_tasks, polling_tasks
        from ojisan.subscriptions import tasks as subscription_tasks
        expected = set()
        for old, module in [('tasks',youtube_tasks), ('twitch_tasks',twitch_tasks),
                            ('polling_tasks',polling_tasks), ('subscription_tasks',subscription_tasks)]:
            tree=ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.FunctionDef) and any(
                    isinstance(d,ast.Call) and ast.unparse(d.func)=='celery_app.task'
                    for d in node.decorator_list):
                    task=getattr(module,node.name)
                    self.assertEqual(task.name, old+'.'+node.name)
                    expected.add(task.name)
        self.assertGreater(len(expected), 10)
        for item in celery_app.conf.beat_schedule.values():
            self.assertIn(item['task'], expected)
        for name in celery_app.conf.imports: importlib.import_module(name)

    def test_slash_commands_registered_offline(self):
        from ojisan.discord.bot import bot
        names={c.name for c in bot.tree.get_commands()}
        self.assertTrue({'add_youtube','add_twitch','remove_youtube','remove_twitch','language'} <= names)

    def test_admin_auth_fail_closed(self):
        from ojisan.admin.auth import require_admin_api_key
        from ojisan.core.config import Config
        with patch.object(Config,'ADMIN_API_KEY',None):
            with self.assertRaises(HTTPException) as ctx: require_admin_api_key('x')
            self.assertEqual(ctx.exception.status_code,503)
        with patch.object(Config,'ADMIN_API_KEY','offline-admin-key'):
            with self.assertRaises(HTTPException) as ctx: require_admin_api_key('wrong')
            self.assertEqual(ctx.exception.status_code,401)
            require_admin_api_key('offline-admin-key')

    def test_youtube_signature_checks(self):
        from ojisan.core.config import Config
        from ojisan.platforms.youtube.webhook_security import verify_signature
        body=b'<feed/>'
        with patch.object(Config,'YOUTUBE_WEBHOOK_SECRET','offline-secret'):
            signature='sha1='+hmac.new(b'offline-secret',body,hashlib.sha1).hexdigest()
            self.assertTrue(verify_signature(body,signature))
            self.assertFalse(verify_signature(body+b'changed',signature))
            self.assertFalse(verify_signature(body,''))
            self.assertFalse(verify_signature(body,'invalid'))

    def test_admin_routes_import_without_missing_static_directory(self):
        from ojisan.entrypoints.admin import app
        paths=set(app.openapi()['paths'])
        self.assertIn('/admin/api/channels',paths)


if __name__ == '__main__': unittest.main()
