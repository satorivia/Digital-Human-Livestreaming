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

## 阶段 3：淘宝 Adapter 保守骨架
- 已完成 TaobaoLiveAdapterConfig Pydantic 配置模型，secret 字段使用 SecretStr。
- 已完成淘宝事件验签占位和 raw payload hash-log，不接真实淘宝 API。
- 已完成淘宝评论、上下播、订单 raw event 到 PlatformEvent 的 normalize_event。
- 已完成平台商品 ID 到内部商品 ID 的映射模型和 Alembic migration。
- 已完成淘宝 Adapter 契约测试，确保用户 ID/订单 ID 仅以 hash 形式保留。

## P0-1：Mock 主链路 API
- 已新增 FastAPI route 层，覆盖商品、SKU、FAQ、卖点、索引、直播场次、Mock 评论、候选回答、人审、speech task 播放/打断。
- 已新增 API ServiceContainer，将现有 Mock services 组合成可由 HTTP 调用的 in-memory MVP 边界。
- 已新增 API-level Mock flow 测试：创建商品 → SKU/FAQ/卖点 → 索引 → 创建并启动直播 → 模拟评论 → 合规/人审 → speech task → MockAvatar 播报完成。
- 已新增 API-level blocked 防护测试，确保 blocked candidate 在 approve 入口不会创建 speech_task。

## P0-2 / P0-3 / P0-4：持久化与前端联动启动
- 已新增 P0 主链路缺失表的 SQLAlchemy models 和 Alembic migration：卖点、禁用表达、知识块、评论任务、候选回答、合规结果、人审任务、播报任务、TTS 资产、Avatar 命令日志、审计日志。
- 已新增 P0 repository 层初版：Product、LiveSession、CommentTask、AnswerCandidate、HumanReviewTask、SpeechTask、AuditLog。
- 已新增 migration/repository 静态测试，确保 P0 表和 repository 边界存在。
- 已启动 control-web API client 和 Pinia store 接入 P0-1 API，覆盖产品加载、创建 Mock session、提交 Mock 评论、审核通过、刷新播报任务。
- 当前 P0 API 尚未完全切换到 repository；下一步应把 Product/LiveSession/Review/Speech API 逐个替换为数据库 repository 实现。
