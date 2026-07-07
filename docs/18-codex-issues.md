# 18. Codex Issue 拆分

## 使用方式

不要让 Codex 一次性开发整个系统。按下面 Issue 顺序逐个开发。每个 Issue 必须满足 Done Definition。

## Issue 模板

```text
Title:

Goal:

Context:

Requirements:

Files/Modules:

Done When:

Tests:

Notes:
```

---

## 阶段 0：工程骨架

### Issue 001：初始化 monorepo 与基础文档

Goal：创建仓库结构、README、AGENTS.md、Makefile、.env.example。

Requirements：

1. 按 docs/03-repo-structure.md 创建目录。
2. 添加 README.md。
3. 添加 AGENTS.md。
4. 添加 Makefile 占位命令。
5. 添加 .env.example。
6. 不引入真实密钥。

Done When：

- 仓库结构完整。
- `make help` 可运行。

### Issue 002：创建 FastAPI api-server 骨架

Requirements：

1. 使用 Python 3.11+。
2. FastAPI app。
3. `/api/v1/healthz`。
4. pydantic-settings 配置。
5. structlog JSON 日志。
6. 统一响应结构。
7. pytest 基础测试。

### Issue 003：创建 Vue3 admin-web/control-web 骨架

Requirements：

1. Vite + Vue3 + TypeScript。
2. Element Plus。
3. Pinia。
4. Router。
5. 基础布局。
6. API client。
7. control-web 预留 WebSocket client。

### Issue 004：接入 PostgreSQL、Redis、Qdrant、MinIO、SRS Docker Compose

Requirements：

1. 编写 infra/docker-compose.yml。
2. 添加 postgres、redis、qdrant、minio、srs。
3. api-server 可读取连接配置。
4. health check 验证连接。

### Issue 005：实现 SQLAlchemy + Alembic 迁移框架

Requirements：

1. 配置 SQLAlchemy async engine。
2. 配置 Alembic。
3. 创建第一版 merchant/app_user/product/live_session 基础表。
4. `make migrate` 可执行。

---

## 阶段 1：Mock 主链路

### Issue 006：实现统一 PlatformEvent Schema

Requirements：

1. 在 packages/event-schema 定义 Pydantic schema。
2. 支持事件类型枚举。
3. 支持 JSON 序列化。
4. 添加单元测试。

### Issue 007：实现 LiveSession 状态机

Requirements：

1. 实现 docs/06-live-state-machine.md 中状态和转移。
2. 非法转移抛异常。
3. 每次转移写入 live_state_log。
4. 覆盖所有合法/非法转移测试。

### Issue 008：实现 ProductService 商品 CRUD

Requirements：

1. 商品 CRUD。
2. SKU CRUD。
3. 价格 CRUD。
4. FAQ CRUD。
5. 卖点 CRUD。
6. Alembic migration。
7. pytest。

### Issue 009：实现 ProductRAG 基础索引

Requirements：

1. knowledge_chunk 生成。
2. Qdrant collection 初始化。
3. FAQ/卖点 upsert。
4. 检索接口。
5. Mock embedding 或简单 embedding provider。
6. 测试检索命中。

### Issue 010：实现 MockPlatformAdapter

Requirements：

1. 模拟 LiveStarted。
2. 模拟 CommentReceived。
3. 模拟 OrderCreated。
4. 模拟 PlatformWarningReceived。
5. 输出 PlatformEvent。
6. 写入 platform_event_log。

### Issue 011：实现 CommentRouter

Requirements：

1. 消费 PlatformEvent。
2. 只处理 CommentReceived/ManualCommentEntered。
3. 去重。
4. 黑名单过滤。
5. 简单 intent 分类。
6. 绑定当前商品。
7. 创建 comment_task。

### Issue 012：实现 LLMGateway MockProvider

Requirements：

1. classify_comment。
2. generate_product_answer。
3. rewrite_for_platform。
4. compliance_review mock。
5. 支持模拟超时和错误。
6. 记录调用日志。

### Issue 013：实现商品问答 Prompt 模板

Requirements：

1. 创建 product_answer_v1.md。
2. 创建 comment_classify_v1.md。
3. Prompt 禁止编造价格和库存。
4. 单元测试验证模板变量完整。

### Issue 014：实现 ComplianceService 基础规则

Requirements：

1. SensitiveWordChecker。
2. AbsoluteClaimChecker。
3. PriceConsistencyChecker 基础版。
4. 风险等级输出。
5. need_human_review。
6. 测试低/中/高/blocked。

### Issue 015：实现 HumanReviewService

Requirements：

1. 创建 review task。
2. approve。
3. reject。
4. rewrite。
5. manual answer。
6. 写 audit_log。
7. WebSocket 事件预留。

### Issue 016：实现 TTSService MockProvider

Requirements：

1. generate 返回 fake audio_url。
2. precache。
3. cache key。
4. tts_asset 入库。
5. 支持模拟失败。

### Issue 017：实现 AvatarGateway MockProvider

Requirements：

1. speak_audio。
2. speak_text。
3. interrupt。
4. idle。
5. avatar_command_log。
6. 支持模拟失败。

### Issue 018：实现 SpeechQueueService

Requirements：

1. enqueue_speech。
2. 取下一条。
3. 标记 speaking/finished/interrupted/failed。
4. 优先级排序。
5. 接入 TTSService 和 AvatarGateway mock。

### Issue 019：实现 control-web 场控台 MVP

Requirements：

1. 直播状态显示。
2. 当前商品显示。
3. 评论模拟输入。
4. 评论队列。
5. 候选回答。
6. 合规风险。
7. 审核通过/拒绝/改写。
8. 播报状态。
9. 人工接管按钮。

### Issue 020：实现 E2E Mock 评论到数字人播报

Requirements：

1. 创建测试数据。
2. 启动 Mock 直播。
3. 模拟评论。
4. 生成候选回答。
5. 合规审核。
6. 人工通过。
7. MockTTS。
8. MockAvatar。
9. 断言日志完整。

---

## 阶段 2：真实 TTS + LiveTalking

### Issue 021：实现 VoiceProfile 与 VoiceLicense

### Issue 022：实现 EdgeTTSProvider

### Issue 023：预留 CosyVoiceProvider 接口

### Issue 024：预留 GPTSoVITSProvider 接口

### Issue 025：实现 LiveTalkingProvider

### Issue 026：实现 Avatar interrupt 真实链路

### Issue 027：实现 MediaService SRS 预览 URL

### Issue 028：编写 OBS 推流操作文档

---

## 阶段 3：淘宝 Adapter

### Issue 029：实现 TaobaoLiveAdapter 配置模型

### Issue 030：实现淘宝事件验签占位与 raw log

### Issue 031：实现淘宝评论事件 normalize_event

### Issue 032：实现淘宝上下播事件 normalize_event

### Issue 033：实现淘宝订单事件 normalize_event

### Issue 034：实现平台商品 ID 映射

### Issue 035：淘宝 Adapter 契约测试

---

## 阶段 4：抖音 Adapter

### Issue 036：实现 DouyinAdapter 配置模型

### Issue 037：实现评论任务启动/停止/查询状态接口封装

### Issue 038：实现抖音评论事件 normalize_event

### Issue 039：实现平台警告事件处理

### Issue 040：实现抖音高风险默认人审策略

---

## 阶段 5：合规强化

### Issue 041：敏感词后台

### Issue 042：绝对化用语规则后台

### Issue 043：类目规则后台

### Issue 044：平台规则后台

### Issue 045：价格一致性强校验

### Issue 046：AI 标识配置

### Issue 047：合规审核看板

---

## 阶段 6：小红书 / 视频号

### Issue 048：ManualInputAdapter 强化

### Issue 049：XiaohongshuAdapter 基础配置

### Issue 050：WeChatChannelsAdapter 基础配置

### Issue 051：保守模式策略开关

---

## 阶段 7：TikTok 国际化

### Issue 052：TikTokAdapter 基础配置

### Issue 053：多语言商品知识库字段

### Issue 054：英文 Prompt 模板

### Issue 055：多币种价格话术

### Issue 056：海外物流 FAQ 模板

---

## 阶段 8：规模化

### Issue 057：多直播间并发隔离

### Issue 058：排班系统

### Issue 059：多账号配置

### Issue 060：数据看板

### Issue 061：成本统计

### Issue 062：监控告警

### Issue 063：权限系统强化

### Issue 064：生产部署脚本
