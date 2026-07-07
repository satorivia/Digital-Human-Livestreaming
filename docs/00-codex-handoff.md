# 00. Codex 总交接说明

## 1. 你要开发什么

你要从零开发一套面向电商直播的数字人直播系统。系统用于支持淘宝直播、抖音、小红书、视频号，后续扩展 TikTok。

系统不是单纯的数字人播放器，而是完整的直播业务系统，必须包含：

```text
平台接入
商品知识库
直播中控
评论处理
AI 问答
合规审核
人工审核
TTS 语音合成
数字人播报
媒体预览 / 推流
人工接管
日志留存
后台管理
场控台
```

## 2. 总体开发策略

必须按照阶段开发，不允许一次性生成全系统。

推荐阶段：

```text
阶段 0：工程骨架
阶段 1：商品库 + Mock 全链路
阶段 2：真实 TTS + AvatarGateway + LiveTalking
阶段 3：淘宝直播 Adapter
阶段 4：抖音 Adapter
阶段 5：合规系统强化
阶段 6：小红书 / 视频号保守接入
阶段 7：TikTok 国际化
阶段 8：多直播间规模化
```

## 3. 第一阶段必须先完成什么

第一阶段不要接真实平台、真实模型、真实数字人。先实现所有 Mock 能力，把主业务链路跑通：

```text
Mock 评论进入
  ↓
标准化 PlatformEvent
  ↓
CommentRouter 创建评论任务
  ↓
ProductRAG 查询商品资料
  ↓
LLMGateway Mock 生成候选回答
  ↓
ComplianceService 审核
  ↓
HumanReviewService 人工确认
  ↓
TTSService Mock 生成音频占位
  ↓
AvatarGateway Mock 播报
  ↓
日志留存
```

## 4. Codex 工作方式

Codex 必须先阅读：

- `README.md`
- `AGENTS.md`
- `docs/01-prd.md`
- `docs/02-architecture.md`
- `docs/04-module-boundaries.md`
- `docs/06-live-state-machine.md`
- `docs/18-codex-issues.md`

然后按 `docs/18-codex-issues.md` 的任务顺序逐个实现。

## 5. 严格禁止

- 禁止跳过合规审核直接播报。
- 禁止业务代码直接调用 LLM Provider。
- 禁止业务代码直接调用平台 API。
- 禁止 LiveControlService 直接调用 LiveTalking。
- 禁止把价格、库存、优惠券等实时事实交给 LLM 猜测。
- 禁止在测试中依赖真实平台账号。
- 禁止提交任何密钥。
- 禁止实现非官方抓包、绕过平台限制、反风控、模拟真人规避审核等功能。

## 6. 交付要求

每个阶段必须交付：

```text
代码
数据库迁移
单元测试
集成测试
更新后的文档
本地启动说明
验收步骤
```

## 7. 技术栈

```text
Backend: Python 3.11 + FastAPI + SQLAlchemy + Alembic + Pydantic
Frontend: Vue 3 + TypeScript + Element Plus
Database: PostgreSQL
Cache/Queue: Redis + Redis Streams
Vector DB: Qdrant
Object Storage: MinIO-compatible
Media: OBS + SRS
Avatar: LiveTalking behind AvatarGateway
Testing: pytest + frontend test runner + E2E tests
```

## 8. 第一条 E2E 验收链路

第一条 E2E 必须实现：

```text
创建商家
创建商品
创建 SKU
创建 FAQ
创建直播间
启动 Mock 直播场次
模拟评论：这款多少钱？
生成候选回答
合规审核通过
人工审核通过
生成播报任务
Avatar Mock 标记播报完成
查询全链路日志
```

如果这条链路不能自动测试通过，不得继续接真实平台。
