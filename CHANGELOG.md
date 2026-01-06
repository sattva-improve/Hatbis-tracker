# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-29

### Added

#### サンプルプロジェクト: タスク管理API

全4フェーズを実行し、完全なAPI仕様書を生成しました。

**Phase 1: 要件定義** (`requirements/projects/task-management-api/`)
- 機能要件15項目（ユーザー認証、プロジェクト管理、タスク管理、コメント機能）
- 非機能要件（性能、可用性、セキュリティ）
- データエンティティとER図
- API要件概要

**Phase 2: 基本設計** (`design/basic/projects/task-management-api/`)
- システムアーキテクチャ図
- API設計方針とURL設計規則
- 21エンドポイント設計
- データモデル設計（ER図）
- JWT認証・RBAC認可設計
- エラーコード設計

**Phase 3: 詳細設計** (`design/detailed/projects/task-management-api/`)
- 全エンドポイントの詳細仕様
- リクエスト/レスポンススキーマ定義
- バリデーションルール詳細
- 処理フロー図（シーケンス図）
- データベースDDL（PostgreSQL）

**Phase 4: OpenAPI仕様書** (`specs/openapi/projects/task-management-api/`)
- OpenAPI 3.1準拠の完全な仕様書
- 21エンドポイント、認証・エラー定義を含む

---

## [1.0.0] - 2024-12-29

### Added

#### システム基盤
- Gitリポジトリの初期化
- mainブランチの作成

#### ドキュメント
- `docs/overview.md` - システム全体像、アーキテクチャ、処理フロー
- `README.md` - プロジェクト説明、使い方ガイド

#### ディレクトリ構造
- `requirements/` - 要件定義書格納ディレクトリ
- `design/basic/` - 基本設計書格納ディレクトリ
- `design/detailed/` - 詳細設計書格納ディレクトリ
- `specs/openapi/` - OpenAPI仕様書格納ディレクトリ
- `ai/prompts/` - AIプロンプトテンプレートディレクトリ
- `ai/instructions/` - AI指示ファイルディレクトリ
- `scripts/` - 自動化スクリプトディレクトリ

#### テンプレート
- `requirements/_template.md` - 要件定義書テンプレート
  - プロジェクト概要
  - 機能要件・非機能要件
  - データ要件
  - 外部インターフェース要件
  - 制約条件・前提条件

- `design/basic/_template.md` - 基本設計書テンプレート
  - システム構成・アーキテクチャ
  - API設計（URL設計、HTTPメソッド）
  - データモデル設計（ER図）
  - 認証・認可設計
  - エラー設計

- `design/detailed/_template.md` - 詳細設計書テンプレート
  - API詳細設計（リクエスト/レスポンス定義）
  - スキーマ定義（JSON Schema）
  - バリデーション詳細
  - 処理フロー（シーケンス図）
  - データベース詳細設計

- `specs/openapi/_template.yaml` - OpenAPI 3.1仕様書テンプレート
  - 認証API
  - CRUD API
  - 共通コンポーネント（パラメータ、スキーマ、レスポンス）

#### AI駆動開発ツール
- `ai/instructions/workflow.md` - ワークフロー指示書
  - 4フェーズの処理フロー定義
  - ファイル命名規則
  - 品質チェックリスト

- `ai/prompts/requirements.md` - 要件定義生成プロンプト
- `ai/prompts/basic_design.md` - 基本設計生成プロンプト
- `ai/prompts/detailed_design.md` - 詳細設計生成プロンプト
- `ai/prompts/openapi_gen.md` - OpenAPI仕様書生成プロンプト

### Technical Details

- OpenAPI バージョン: 3.1.0
- 認証方式: JWT Bearer Token
- API設計: RESTful設計原則準拠
- ドキュメント形式: Markdown
- 図表形式: Mermaid

---

## 実績サマリー

| 項目 | 数量 |
|------|------|
| 作成ディレクトリ | 9 |
| 作成ファイル | 13 |
| テンプレート | 4 |
| AIプロンプト | 4 |

## 次回リリース予定

### [1.1.0] - 予定

- [ ] 実装コード自動生成機能
- [ ] 自動テスト生成機能
- [ ] バリデーションスクリプト
