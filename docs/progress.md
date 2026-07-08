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

## Issue 017-020 Mock 主链路强化
- 已完善 AvatarGateway MockProvider：speak_audio、speak_text、interrupt、idle、失败模拟和 avatar_command_log。
- 已完善 SpeechQueueService：enqueue、next_task、speaking/finished/interrupted/failed 状态、优先级排序、TTS/Avatar 错误落盘到任务状态。
- 已强化 blocked 防护：blocked answer 或未完成人审的 candidate 不能进入 speech queue。
- 已强化 Mock E2E：通过 reviewed candidate 创建播报任务，并新增 blocked answer 不创建 speech_task 的断言。
- 已强化 control-web 场控台 MVP：直播状态、当前商品、评论队列、候选回答、合规风险、审核按钮、人工接管按钮、播报历史。

## 阶段 2：接口骨架
- 已完成 VoiceProfile 与 VoiceLicense 内存模型、SQLAlchemy 模型和 Alembic migration。
- 已完成 EdgeTTSProvider、CosyVoiceProvider、GPTSoVITSProvider 禁用占位。
- 已完成 LiveTalkingProvider 禁用占位和 AvatarProvider 协议。
- 已完成 MediaService SRS 预览 URL 占位。
- 已更新 OBS/SRS 使用文档占位。
- 真实 Provider 后续接入前仍必须保留 Mock 契约测试。
