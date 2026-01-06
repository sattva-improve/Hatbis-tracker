# OpenAPI仕様書生成プロンプト

## コンテキスト

あなたはOpenAPI仕様書生成のエキスパートです。
詳細設計書を基に、OpenAPI 3.1仕様書を生成してください。

## 入力情報

### 詳細設計書
```
{{DETAILED_DESIGN_DOC}}
```

### プロジェクト情報
- プロジェクト名: {{PROJECT_NAME}}
- 作成日: {{DATE}}
- 詳細設計書パス: {{DETAILED_DESIGN_PATH}}

## 指示

以下の手順でOpenAPI仕様書を生成してください：

### Step 1: メタ情報定義

```yaml
openapi: 3.1.0
info:
  title: "{{PROJECT_NAME}} API"
  description: "{{PROJECT_DESCRIPTION}}"
  version: "1.0.0"
  contact:
    name: "API Support"
    email: "support@example.com"
```

### Step 2: サーバー定義

```yaml
servers:
  - url: "http://localhost:3000/api/v1"
    description: "開発環境"
  - url: "https://staging-api.example.com/api/v1"
    description: "ステージング環境"
  - url: "https://api.example.com/api/v1"
    description: "本番環境"
```

### Step 3: セキュリティスキーム定義

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### Step 4: パス定義

詳細設計書の各エンドポイントをOpenAPI形式に変換してください：

```yaml
paths:
  /users:
    get:
      tags:
        - users
      summary: "ユーザー一覧取得"
      operationId: listUsers
      security:
        - bearerAuth: []
      parameters:
        - $ref: "#/components/parameters/PageParam"
      responses:
        "200":
          description: "取得成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserListResponse"
```

### Step 5: スキーマ定義

詳細設計書のスキーマをOpenAPI形式に変換してください：

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
        email:
          type: string
          format: email
          maxLength: 255
      required:
        - email
```

### Step 6: 共通コンポーネント定義

#### パラメータ
```yaml
components:
  parameters:
    IdParam:
      name: id
      in: path
      required: true
      schema:
        type: string
        format: uuid
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        minimum: 1
        default: 1
```

#### レスポンス
```yaml
components:
  responses:
    NotFound:
      description: "リソース未存在"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
```

### Step 7: バリデーション

生成したOpenAPI仕様書が有効であることを確認してください：
- 全てのパスが定義されている
- 全ての$refが解決可能である
- 必須フィールドが定義されている
- スキーマが正しい形式である

### Step 8: OpenAPI仕様書出力

`specs/openapi/_template.yaml`をベースに、完全なOpenAPI仕様書を生成してください。

## 出力形式

生成したOpenAPI仕様書は以下のパスに保存してください：
`specs/openapi/projects/{{PROJECT_NAME}}/openapi.yaml`

## OpenAPI仕様書チェックリスト

- [ ] OpenAPI 3.1.0 形式に準拠している
- [ ] info セクションが完全に定義されている
- [ ] servers が定義されている
- [ ] 全エンドポイントがpathsに定義されている
- [ ] 全スキーマがcomponents/schemasに定義されている
- [ ] 認証が正しく定義されている
- [ ] エラーレスポンスが定義されている
- [ ] サンプルデータ（examples）が含まれている

## 変換ルール

### HTTPメソッドとoperationId

| メソッド | パターン | operationId例 |
|---------|---------|--------------|
| GET (一覧) | /resources | listResources |
| GET (詳細) | /resources/{id} | getResource |
| POST | /resources | createResource |
| PUT | /resources/{id} | updateResource |
| DELETE | /resources/{id} | deleteResource |

### データ型マッピング

| 設計書の型 | OpenAPI型 | format |
|-----------|-----------|--------|
| UUID | string | uuid |
| 日時 | string | date-time |
| 日付 | string | date |
| メール | string | email |
| URI | string | uri |
| 整数 | integer | - |
| 小数 | number | - |
| 真偽値 | boolean | - |

### バリデーションマッピング

| 設計書のルール | OpenAPIプロパティ |
|---------------|------------------|
| 必須 | required |
| 最大文字数 | maxLength |
| 最小文字数 | minLength |
| 正規表現 | pattern |
| 最大値 | maximum |
| 最小値 | minimum |
| 列挙値 | enum |

## バリデーションコマンド

生成後、以下のコマンドでバリデーションを実行してください：

```bash
# swagger-cli を使用
npx @apidevtools/swagger-cli validate openapi.yaml

# spectral を使用
npx @stoplight/spectral-cli lint openapi.yaml
```
