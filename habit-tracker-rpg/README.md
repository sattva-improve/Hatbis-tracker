# Habit Tracker RPG 🎮

習慣管理システムにRPGゲーミフィケーション要素を組み込んだバックエンドAPIです。

## 📋 概要

Habit Tracker RPGは、日々の習慣をRPGのような体験に変換するアプリケーションです。習慣を達成することで経験値を獲得し、6種類のステータスを成長させ、称号（ジョブ）やアチーブメントを解除できます。

### 主な機能

- 🔐 **ユーザー認証**: Amazon Cognito による JWT 認証
- 📝 **習慣管理**: 習慣の作成・編集・削除・アーカイブ
- 📊 **記録管理**: 日々の習慣達成記録
- ⚔️ **RPGシステム**:
  - 6種類のステータス（VIT, INT, MND, DEX, CHA, STR）
  - 総合レベル＆各ステータスレベル
  - ストリークボーナス（連続達成ボーナス）
  - 経験値システム
- 🏆 **アチーブメント**: 条件達成で解除される実績
- 👔 **ジョブシステム**: ステータス条件で解除される称号

## 🛠️ 技術スタック

- **ランタイム**: Python 3.11
- **クラウド**: AWS (Lambda, DynamoDB, API Gateway, Cognito)
- **IaC**: AWS CDK (Python)
- **ローカル開発**: LocalStack
- **テスト**: pytest, moto

## 📁 プロジェクト構造

```
habit-tracker-rpg/
├── src/
│   ├── handlers/          # Lambda ハンドラー
│   │   ├── auth.py        # 認証関連
│   │   ├── users.py       # ユーザー管理
│   │   ├── habits.py      # 習慣管理
│   │   ├── records.py     # 記録管理
│   │   ├── stats.py       # 統計取得
│   │   ├── achievements.py # アチーブメント
│   │   └── jobs.py        # ジョブシステム
│   ├── models/            # データモデル
│   │   ├── gamification.py # ゲーミフィケーション
│   │   ├── user.py        # ユーザー
│   │   ├── habit.py       # 習慣
│   │   ├── record.py      # 記録
│   │   ├── achievement.py # アチーブメント
│   │   └── job.py         # ジョブ
│   └── services/          # ビジネスロジック
│       ├── dynamodb_repository.py
│       ├── user_service.py
│       ├── habit_service.py
│       ├── record_service.py
│       ├── stats_service.py
│       ├── achievement_service.py
│       └── job_service.py
├── cdk/                   # AWS CDK インフラ定義
│   ├── app.py
│   ├── cdk.json
│   └── stacks/
│       └── main_stack.py
├── local/                 # ローカル開発環境
│   ├── docker-compose.yaml
│   ├── start.sh
│   ├── stop.sh
│   └── init-scripts/
│       └── init-aws.sh
├── tests/                 # テスト
│   ├── conftest.py
│   ├── test_gamification.py
│   ├── test_models.py
│   ├── test_handlers.py
│   └── test_services.py
├── docs/
│   └── openapi.yaml       # API仕様書
└── requirements.txt       # Python依存関係
```

## 🚀 セットアップ

### 前提条件

- Python 3.11+
- Docker & Docker Compose
- AWS CLI
- Node.js 18+ (CDK用)

### 1. 依存関係のインストール

```bash
cd habit-tracker-rpg

# Python仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# CDKのインストール (グローバル)
npm install -g aws-cdk
```

### 2. ローカル開発環境の起動

LocalStackを使用してAWSサービスをローカルでエミュレートします。

```bash
cd local

# LocalStackの起動
./start.sh

# 確認
docker compose ps

# 停止
./stop.sh
```

### 3. テストの実行

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 特定のテストファイル
pytest tests/test_gamification.py -v
```

## 📡 API エンドポイント

### 認証

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/auth/signup` | ユーザー登録 |
| POST | `/auth/signin` | ログイン |
| POST | `/auth/signout` | ログアウト |
| POST | `/auth/refresh` | トークンリフレッシュ |
| POST | `/auth/change-password` | パスワード変更 |

### ユーザー

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/users/me` | 自分のプロフィール取得 |
| PUT | `/users/me` | プロフィール更新 |
| GET | `/users/me/stats` | 自分のステータス取得 |

### 習慣

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/habits` | 習慣一覧取得 |
| POST | `/habits` | 習慣作成 |
| GET | `/habits/{habitId}` | 習慣詳細取得 |
| PUT | `/habits/{habitId}` | 習慣更新 |
| DELETE | `/habits/{habitId}` | 習慣削除 |
| POST | `/habits/{habitId}/archive` | 習慣アーカイブ |

### 記録

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/habits/{habitId}/records` | 記録一覧取得 |
| POST | `/habits/{habitId}/records` | 記録作成 |
| PUT | `/records/{recordId}` | 記録更新 |
| DELETE | `/records/{recordId}` | 記録削除 |
| GET | `/records/today` | 今日の記録取得 |

### 統計

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/stats/daily` | 日次統計 |
| GET | `/stats/weekly` | 週次統計 |
| GET | `/stats/monthly` | 月次統計 |

### アチーブメント・ジョブ

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/achievements` | アチーブメント一覧 |
| GET | `/achievements/{achievementId}` | アチーブメント詳細 |
| GET | `/jobs` | ジョブ一覧 |
| GET | `/jobs/{jobId}` | ジョブ詳細 |
| POST | `/jobs/{jobId}/equip` | ジョブ装備 |

## ⚔️ ゲーミフィケーションシステム

### ステータス

| ステータス | 略称 | 関連カテゴリ |
|-----------|------|--------------|
| 体力 (Vitality) | VIT | 運動、睡眠、健康 |
| 知力 (Intelligence) | INT | 読書、勉強、学習 |
| 精神 (Mental) | MND | 瞑想、日記、感謝、マインドフルネス |
| 器用 (Dexterity) | DEX | 音楽、アート、クラフト、趣味 |
| 魅力 (Charisma) | CHA | コミュニケーション、社交、身だしなみ |
| 筋力 (Strength) | STR | 筋トレ、スポーツ、フィットネス |

### 経験値システム

- **基本経験値**: 10 EXP
- **難易度ボーナス**:
  - Easy: 0.5倍
  - Normal: 1.0倍
  - Hard: 1.5倍

### ストリークボーナス

| 連続日数 | ボーナス |
|----------|----------|
| 3日 | 1.1倍 |
| 7日 | 1.25倍 |
| 14日 | 1.5倍 |
| 30日 | 2.0倍 |

### レベルアップ

```
必要経験値 = 基本経験値 × (成長率 ^ (レベル - 1))
```

- 基本経験値: 100
- 成長率: 1.5
- 最大レベル: 99

## ☁️ AWSへのデプロイ

### CDKを使用したデプロイ

```bash
cd cdk

# CDK Bootstrap (初回のみ)
cdk bootstrap aws://ACCOUNT-ID/ap-northeast-1

# スタックの合成確認
cdk synth

# デプロイ
cdk deploy --all

# 削除
cdk destroy --all
```

### 環境変数

| 変数名 | 説明 |
|--------|------|
| `AWS_REGION` | AWSリージョン |
| `USERS_TABLE` | ユーザーテーブル名 |
| `HABITS_TABLE` | 習慣テーブル名 |
| `RECORDS_TABLE` | 記録テーブル名 |
| `USER_ACHIEVEMENTS_TABLE` | ユーザーアチーブメントテーブル名 |
| `USER_JOBS_TABLE` | ユーザージョブテーブル名 |
| `COGNITO_USER_POOL_ID` | Cognitoユーザープール ID |
| `COGNITO_CLIENT_ID` | Cognitoクライアント ID |

## 📄 ライセンス

MIT License

## 📚 ドキュメント

詳細なドキュメントは `docs/` ディレクトリにあります：

| ドキュメント | 説明 |
|-------------|------|
| [docs/index.md](docs/index.md) | ドキュメント一覧 |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | 全APIの詳細リファレンス |
| [docs/openapi.yaml](docs/openapi.yaml) | OpenAPI 3.0 仕様書 |
| [docs/GAMIFICATION.md](docs/GAMIFICATION.md) | ゲーミフィケーションシステム設計書 |
| [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) | ローカル開発環境ガイド |
| [docs/aws-deployment.md](docs/aws-deployment.md) | AWSデプロイガイド |

## 🤝 コントリビューション

Issue や Pull Request を歓迎します！
