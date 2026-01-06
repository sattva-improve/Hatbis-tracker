# OpenAPI → Django 自動変換プロンプト

AIにOpenAPI仕様書からDjangoコードを生成させる際に使用するプロンプトテンプレートです。

---

## モデル生成プロンプト

```
以下のOpenAPI仕様書のschemasセクションを読み、Django ORMモデルに変換してください。

変換ルール:
1. type: string, format: uuid → UUIDField(primary_key=True, default=uuid.uuid4)
2. type: string → CharField(max_length=X)
3. type: string, format: email → EmailField
4. type: string, format: date-time → DateTimeField
5. type: integer → IntegerField
6. type: boolean → BooleanField
7. type: string, enum: [...] → CharField(choices=CHOICES)
8. $ref: "#/components/schemas/X" → ForeignKey(X)
9. readOnly: true + format: date-time → auto_now_add=True または auto_now=True
10. required配列に含まれない → blank=True, default=''

OpenAPI仕様書:
{openapi_schemas}

出力形式:
- Pythonコードのみ
- 各モデルにdocstringを付与
- verbose_name を日本語で設定
- class Meta に db_table, ordering を設定
```

---

## シリアライザー生成プロンプト

```
以下のOpenAPI仕様書のschemasセクションとpathsセクションを読み、DRFシリアライザーを生成してください。

変換ルール:
1. {Model}Request → Create{Model}Serializer / Update{Model}Serializer
2. {Model}Response → {Model}Serializer
3. camelCase → snake_case (source属性で対応)
4. required配列 → required=True
5. minLength/maxLength → バリデーター
6. $ref → ネストしたシリアライザー
7. 外部キーID (例: assigneeId) → UUIDField + validate_XXX メソッド

OpenAPI仕様書:
{openapi_spec}

Django モデル:
{django_models}

出力形式:
- 作成用、更新用、レスポンス用を分離
- camelCaseフィールドは source 属性で対応
- バリデーションメソッドを実装
```

---

## ビュー生成プロンプト

```
以下のOpenAPI仕様書のpathsセクションを読み、DRF ViewSetを生成してください。

変換ルール:
1. GET (list) → list() / get_queryset()
2. GET (detail) → retrieve()
3. POST → create()
4. PUT → update()
5. PATCH → partial_update()
6. DELETE → destroy()
7. カスタムパス (例: /status) → @action デコレータ
8. クエリパラメータ → get_queryset() でフィルター
9. パスパラメータ (例: {projectId}) → kwargs.get('project_pk')

OpenAPI仕様書:
{openapi_paths}

シリアライザー:
{serializers}

出力形式:
- ViewSetベース
- get_serializer_class() でアクション別シリアライザー
- レスポンスは {'data': ...} 形式でラップ
- 権限チェックを実装
```

---

## URL生成プロンプト

```
以下のOpenAPI仕様書のpathsセクションを読み、DRF URLルーティングを生成してください。

変換ルール:
1. /resource → router.register('resource', ViewSet)
2. /resource/{id}/sub → NestedDefaultRouter
3. 認証エンドポイント → path() で個別定義

OpenAPI仕様書:
{openapi_paths}

出力形式:
- rest_framework_nested を使用
- 認証系は path() で定義
- namespaceを設定
```

---

## テスト生成プロンプト

```
以下のDjangoモデルとビューに対するpytestテストを生成してください。

テスト対象:
{models}
{views}
{urls}

生成ルール:
1. 各エンドポイントに対して正常系と異常系
2. 認証が必要なエンドポイントは authenticated_client を使用
3. fixtureでテストデータを準備
4. @pytest.mark.django_db デコレータを使用
5. assert でステータスコードとレスポンス形式を検証

出力形式:
- test_{resource}.py 形式
- クラスベース (Test{Model}List, Test{Model}Create など)
- 日本語でテストの説明をdocstringに記載
```

---

## 全体変換プロンプト（一括生成用）

```
以下のOpenAPI仕様書を読み、Django + Django REST Framework プロジェクトを生成してください。

OpenAPI仕様書:
{openapi_full_spec}

生成するファイル:
1. api/models.py - データモデル
2. api/serializers.py - シリアライザー
3. api/views.py - ビュー
4. api/urls.py - URLルーティング
5. api/pagination.py - ページネーション
6. api/exceptions.py - 例外ハンドラー
7. api/permissions.py - 権限クラス
8. config/settings.py の追加設定

変換ルール:
1. OpenAPIのschemasをDjangoモデルに変換
2. レスポンス形式は {'data': ...} でラップ
3. エラー形式は {'error': {'code': ..., 'message': ...}} 
4. JWT認証を使用
5. camelCaseフィールドはsource属性で対応
6. ページネーションはOpenAPI仕様に準拠

出力形式:
- 各ファイルを ```python ``` ブロックで区切って出力
- コメントで説明を追加
```
