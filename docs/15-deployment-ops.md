# 15. 部署与运维

## 1. 本地开发环境

使用 Docker Compose 启动基础依赖：

```text
postgres
redis
qdrant
minio
srs
```

本地命令：

```bash
make install
make up
make migrate
make seed
make test
```

## 2. 测试环境

建议：

```text
CPU 应用服务器
├── api-server
├── admin-web
├── control-web
├── postgres
├── redis
├── qdrant
├── minio
└── srs

GPU 服务器
├── LiveTalking
├── CosyVoice / GPT-SoVITS
└── 可选本地 LLM

直播工作站
├── OBS
└── 平台直播伴侣
```

## 3. 生产环境

```text
入口层
├── Nginx / API Gateway
├── TLS
├── IP 白名单 / WAF
└── 限流

应用层
├── api-server replicas
├── platform-adapter workers
├── live-control workers
├── compliance workers
└── background workers

AI 层
├── llm-gateway
├── tts-service
├── avatar-gateway
└── LiveTalking GPU nodes

数据层
├── PostgreSQL
├── Redis
├── Qdrant
├── MinIO / OSS / COS
└── ClickHouse 可后置

媒体层
├── SRS
├── OBS 工作站
└── 录制存储

监控层
├── Prometheus
├── Grafana
├── Loki / ELK
└── Alertmanager
```

## 4. 环境变量

`.env.example`：

```env
APP_ENV=local
APP_NAME=digital-human-live
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dhlive
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=dhlive
SRS_HTTP_API=http://localhost:1985
SRS_RTMP_URL=rtmp://localhost/live
LLM_PROVIDER=mock
TTS_PROVIDER=mock
AVATAR_PROVIDER=mock
PLATFORM_PROVIDER=mock
JWT_SECRET=change-me
LOG_LEVEL=INFO
```

## 5. 监控指标

```text
live_session_state
platform_event_received_total
platform_event_error_total
comment_task_pending_total
comment_task_processed_total
answer_generation_latency_ms
llm_call_failed_total
compliance_blocked_total
tts_generation_latency_ms
tts_failed_total
speech_queue_pending_total
avatar_command_failed_total
stream_health_status
human_review_pending_total
human_takeover_total
platform_warning_total
```

## 6. 告警规则

| 告警 | 条件 |
|---|---|
| 平台事件中断 | 60 秒无平台事件且直播中 |
| LLM 连续失败 | 5 次连续失败 |
| TTS 连续失败 | 5 次连续失败 |
| Avatar 无响应 | health check 失败 3 次 |
| 推流中断 | stream_health_status != healthy |
| 审核积压 | pending review > 阈值 |
| 播报积压 | pending speech > 阈值 |
| 高风险激增 | high/blocked 数量异常 |
| 平台警告 | 收到 PlatformWarningReceived |

## 7. 日志留存

建议：

| 类型 | 留存 |
|---|---|
| 平台 raw event | 7-30 天，可配置 |
| 评论任务 | 180 天 |
| 播报日志 | 180 天 |
| 合规审核记录 | 1 年 |
| 人工审核记录 | 1 年 |
| 系统日志 | 30-90 天 |
| 录制文件 | 按业务配置 |

## 8. 备份

- PostgreSQL 每日备份。
- MinIO/OSS 对象生命周期管理。
- 合规规则导出备份。
- Prompt 模板版本化。
- 音色授权文件备份。

## 9. 发布流程

```text
feature branch
  ↓
PR
  ↓
lint/test/typecheck
  ↓
Codex review
  ↓
human review
  ↓
staging deploy
  ↓
E2E
  ↓
gray release
  ↓
production
```

## 10. 回滚策略

必须支持：

- API 服务回滚。
- 前端版本回滚。
- Prompt 模板版本回滚。
- 合规规则版本回滚。
- 平台 Adapter 配置回滚。

数据库迁移必须评估是否可逆。
