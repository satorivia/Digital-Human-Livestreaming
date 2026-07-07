# 03. 仓库结构与工程规范

## 1. Monorepo 结构

```text
digital-human-live/
├── apps/
│   ├── api-server/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── dependencies/
│   │   │   └── workers/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── admin-web/
│   ├── control-web/
│   └── monitor-web/
│
├── services/
│   ├── platform-adapter/
│   ├── live-control/
│   ├── product-rag/
│   ├── llm-gateway/
│   ├── compliance/
│   ├── tts-service/
│   ├── avatar-gateway/
│   └── media-service/
│
├── packages/
│   ├── shared-types/
│   ├── event-schema/
│   ├── prompt-templates/
│   ├── platform-sdk/
│   └── compliance-rules/
│
├── infra/
│   ├── docker-compose.yml
│   ├── postgres/
│   ├── redis/
│   ├── qdrant/
│   ├── minio/
│   ├── srs/
│   └── nginx/
│
├── docs/
├── tests/
├── AGENTS.md
├── README.md
├── Makefile
└── .env.example
```

## 2. 后端工程规范

### 2.1 推荐依赖

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlalchemy
alembic
asyncpg
redis
qdrant-client
boto3 or minio
httpx
structlog
python-jose / authlib
pytest
pytest-asyncio
ruff
mypy
```

### 2.2 分层结构

每个业务模块建议采用：

```text
module/
├── models.py        SQLAlchemy models
├── schemas.py       Pydantic request/response schemas
├── repository.py    DB access
├── service.py       business logic
├── router.py        FastAPI routes
├── events.py        event definitions
└── tests/
```

### 2.3 API 规范

- 所有 API 使用 `/api/v1` 前缀。
- 返回结构统一：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "req_xxx"
}
```

错误结构：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product not found",
    "details": {}
  },
  "request_id": "req_xxx"
}
```

### 2.4 日志规范

使用 JSON 日志，字段包括：

```text
timestamp
level
service
module
request_id
session_id
merchant_id
platform
event_type
message
extra
```

不得记录：

- 明文 token。
- API key。
- 未脱敏手机号。
- 完整身份证件。
- 无必要的平台用户唯一标识。

## 3. 前端工程规范

### 3.1 推荐结构

```text
control-web/
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── stores/
│   ├── router/
│   ├── types/
│   ├── utils/
│   └── main.ts
├── package.json
└── vite.config.ts
```

### 3.2 页面规范

- 管理后台用于配置。
- 场控台用于实时操作。
- 审核台可先合并进场控台。
- 直播中控必须使用 WebSocket 实时刷新。

## 4. Makefile 命令

必须提供：

```bash
make install       # 安装依赖
make up            # 启动依赖服务
make down          # 停止依赖服务
make migrate       # 执行数据库迁移
make seed          # 初始化测试数据
make test          # 运行后端单元测试
make lint          # 运行 lint
make typecheck     # 类型检查
make e2e           # 运行 E2E 测试
make docs          # 检查文档/生成 API 文档
```

## 5. 环境变量

`.env.example` 必须包含：

```env
APP_ENV=local
APP_NAME=digital-human-live
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dhlive
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
SRS_HTTP_API=http://localhost:1985
SRS_RTMP_URL=rtmp://localhost/live
LLM_PROVIDER=mock
TTS_PROVIDER=mock
AVATAR_PROVIDER=mock
PLATFORM_PROVIDER=mock
LOG_LEVEL=INFO
```

## 6. 分支与 PR

建议：

```text
main          稳定分支
develop       集成分支
feature/*     功能分支
fix/*         修复分支
```

PR 必须包含：

- 变更说明。
- 测试说明。
- 数据库迁移说明。
- 风险说明。
- 截图或录屏，如果涉及前端。
