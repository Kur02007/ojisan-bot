# 通知・購読・運用

## YouTube

`platforms/youtube/feed_parser.py` がAtom XMLから動画情報を取り出します。Webhookから `tasks.process_livestream_task` が予約され、配信状態やメンバー限定の判定、既存通知の確認、通知先と言語の取得、REST送信を行います。必要な場合、メンバー限定の判定を時間を置いて再確認します。

`workers/polling_tasks.py` は有効なYouTube配信者へ時間をずらしてライブ確認タスクを予約し、動画が本当に該当チャンネルのライブであることをAPIで照合して同じ通知処理へ渡します。

## Twitch

`platforms/twitch/eventsub.py` が署名・鮮度・購読・Message-IDを扱います。`workers/twitch_tasks.py` が開始イベントからタイトルを補完して通知し、終了イベント後にはVODを再照会して既存メッセージのリンクを更新します。YouTubeの動画IDと衝突しないよう `twitch:` 接頭辞の配信キーを保持しています。

## Discord

`discord/bot.py` はコマンド、入力候補、サーバー言語を管理します。`subscriptions/registration.py` は登録上限・登録/削除を共有し、管理APIからも利用されます。`notifications/discord_rest.py` は通知本文・Embedを作り、HTTPで送信・編集します。存在しない送信先の連続失敗カウンタを維持し、元のしきい値で通知登録を整理します。

## 購読更新・再試行

WebSubではPOSTの受理と、Hubが確認した実際の期限延長を区別します。確認済み期限を基準に更新・警告・緊急処理を選び、次回処理日時をDBに保存してワーカー再起動後の回収に備えます。リトライは既存の回数制限・ジッターを保持しています。4xx/deniedを無制限に再試行しません。

Twitchはオンライン/オフライン両方の購読状態を照合し、失効時に再作成します。別コールバック宛ての購読がある場合に無条件で乗っ取らない元の挙動を保持します。

## Celery

15個の旧名は `compatibility-evidence.json` に記録しています。Pythonモジュール名だけを変更し、`tasks.*` / `subscription_tasks.*` / `polling_tasks.*` / `twitch_tasks.*` のタスク名・引数・再試行設定を保持します。Beat設定のタスク名も旧名です。

Celeryアプリはタスクを `conf.imports` で遅延読込するため、worker起動時に解決します。Redisはbrokerであり、通知状態の永続化先はPostgreSQLです。結果backendを新たに追加してはいません。

## トラブルシューティング

- 起動直後の設定エラー: `.env` の空欄、DB URL、Twitch4設定、タイミング制限を確認する。秘密値を貼り付けない。
- Webhookの403: 購読時のsecretと受信側設定、署名ヘッダ、bodyの変換有無を確認する。
- 管理APIの401/503: `X-API-Key` と設定の有無を確認する。管理画面HTMLはこのソースに未収録。
- Twitchが404: Twitchが無効化されていないか、HTTPSコールバック設定を確認する。
- タスクが未登録: `-A ojisan.workers.celery_app:celery_app` で起動し、`conf.imports` と旧タスク名を確認する。
- DBの列不足: `create_all` で既存列は更新されない。元のマイグレーションがこのスナップショットにないため、実スキーマと照合してから手順を決める。
- 二重通知/通知欠落: LiveStream、TwitchメッセージID・通知記録、キュー障害時刻を照合する。通知記録を安易に削除しない。
- Windowsの非同期テストがソケット権限で失敗: ローカルのイベントループ内部通信が許可された環境、またはLinux CIで実行する。
