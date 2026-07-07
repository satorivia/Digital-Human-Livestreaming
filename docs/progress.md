# 开发进度

## 阶段 0：工程骨架
- 已完成 monorepo 目录、Makefile、`.env.example`。
- 已完成 FastAPI `/api/v1/healthz`、pydantic-settings 配置、structlog JSON 日志、统一错误响应。
- 已完成 Docker Compose：PostgreSQL、Redis、Qdrant、MinIO、SRS。
- 已完成 SQLAlchemy 2.x declarative base、async session 配置和 Alembic 初始迁移骨架。
- 已完成 admin-web/control-web Vue3 MVP 页面骨架。

## 阶段 1：Mock 主链路
- 已完成 PlatformEvent Pydantic schema、MockPlatformAdapter、LiveSession 状态机。
- 已完成 ProductService、ProductRAG 简易索引检索、CommentRouter。
- 已完成 LLMGateway Mock、ComplianceService、HumanReviewService。
- 已完成 TTSService Mock、AvatarGateway Mock、SpeechQueueService。
- 已完成评论到 MockAvatar 播报的 E2E 测试。

## Issue 013-016 质量修复
- 已完成 prompt 模板变量测试，并验证商品回答模板禁止编造价格和库存。
- 已将上一轮单文件 `domain.py` 拆分为 product、rag、platform、live、comment、llm、compliance、review、tts、avatar、speech、media 等服务模块。
- 已恢复真实 FastAPI/Pydantic/SQLAlchemy 结构，移除无依赖 fallback 实现。
- 已将 ComplianceService 拆分为 SensitiveWordChecker、AbsoluteClaimChecker、PriceConsistencyChecker。
- 已补齐 HumanReviewService 的 approve、reject、rewrite、manual answer 与 audit_log 测试。
- 已补齐 TTSService Mock cache key、precache、缓存命中和模拟失败测试。
- 已恢复严格 ruff lint 命令，不再通过忽略 E701/E702 掩盖一行式代码问题。

## 阶段 2：接口骨架
- 已完成 MediaService SRS 预览 URL 占位。
- TTS/Avatar 真实 Provider 保持占位，后续接入前仍必须保留 Mock 契约测试。
