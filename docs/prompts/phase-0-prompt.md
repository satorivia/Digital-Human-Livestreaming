# Phase 0 Prompt：工程骨架

请实现阶段 0 的工程骨架，范围只包括：

1. monorepo 目录结构。
2. FastAPI api-server 骨架。
3. Vue3 admin-web/control-web 骨架。
4. Docker Compose 依赖服务。
5. Makefile。
6. .env.example。
7. health check。
8. 基础测试。

不要实现业务功能。

验收：

```bash
make up
make test
```

并确认 `/api/v1/healthz` 正常。
