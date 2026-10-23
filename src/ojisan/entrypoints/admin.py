from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from ojisan.admin.router import router as admin_router
from ojisan.database.models import init_db

# 管理ダッシュボード専用のASGIアプリ。main.py(YouTube Webhook受信用)とは
# 別プロセス/別ポートで動かす想定(docker-compose.yml の admin サービスを参照)。
# 平文HTTPの公開ポートに認証キーを流したくないため、あえてアプリごと分離し、
# 127.0.0.1限定公開(SSHトンネル経由)にできるようにしている。
app = FastAPI(title="YouTube通知Bot 管理ダッシュボード")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(admin_router)
# The upstream snapshot does not contain the dashboard assets. Keep the API
# available when those optional files are absent, regardless of working directory.
static_dir = Path(__file__).resolve().parents[1] / "admin" / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
