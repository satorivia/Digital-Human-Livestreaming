# 开发进度

## 阶段 0：工程骨架
- 已完成 monorepo 目录、Makefile、`.env.example`。
- 已完成 FastAPI `/api/v1/healthz`、配置、结构化日志、统一错误响应。
- 已完成 Docker Compose：PostgreSQL、Redis、Qdrant、MinIO、SRS。
- 已完成 Alembic 初始迁移骨架。
- 已完成 admin-web/control-web Vue3 MVP 页面骨架。

## 阶段 1：Mock 主链路
- 已完成 PlatformEvent schema、MockPlatformAdapter、LiveSession 状态机。
- 已完成 ProductService、ProductRAG 简易索引检索、CommentRouter。
- 已完成 LLMGateway Mock、ComplianceService、HumanReviewService。
- 已完成 TTSService Mock、AvatarGateway Mock、SpeechQueueService。
- 已完成评论到 MockAvatar 播报的 E2E 测试。

## 阶段 2：接口骨架
- 已完成 MediaService SRS 预览 URL 占位。
- TTS/Avatar 真实 Provider 保持占位，后续接入前仍必须保留 Mock 契约测试。
