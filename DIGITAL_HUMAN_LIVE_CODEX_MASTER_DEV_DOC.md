# 数字人直播系统 Codex 全量开发文档 v1.0

本文件由文档包合并生成，适合直接复制给 Codex 作为项目上下文。



---

# 文件：`README.md`

# Digital Human Live — Codex 开发文档包 v1.0

本仓库文档包用于指导 Codex 从 0 到 1 开发一套面向电商直播的数字人直播系统。

目标平台：

- 淘宝直播
- 抖音
- 小红书
- 视频号
- 后续：TikTok

核心目标：

> 开源项目做底座，自研系统做核心。LiveTalking 负责数字人实时渲染，OBS/SRS 负责采集、推流与预览，自研系统负责平台接入、商品知识库、直播中控、合规审核、人工接管和运营后台。

## 推荐阅读顺序

1. `AGENTS.md`：Codex 必须遵守的仓库规则。
2. `docs/00-codex-handoff.md`：给 Codex 的总交接说明。
3. `docs/01-prd.md`：产品需求说明。
4. `docs/02-architecture.md`：总体架构。
5. `docs/03-repo-structure.md`：仓库结构与工程规范。
6. `docs/04-module-boundaries.md`：模块边界。
7. `docs/05-event-schema.md`：平台事件标准化。
8. `docs/06-live-state-machine.md`：直播状态机。
9. `docs/07-data-model.md`：数据模型。
10. `docs/db/schema.sql`：数据库 DDL 草案。
11. `docs/08-api-spec.md` 与 `docs/api/openapi.yaml`：API 契约。
12. `docs/09-platform-adapters.md`：平台 Adapter 开发说明。
13. `docs/10-ai-rag-llm.md`：商品 RAG 与 LLM Gateway。
14. `docs/11-compliance.md`：合规审核。
15. `docs/12-tts-avatar-media.md`：TTS、LiveTalking、OBS/SRS。
16. `docs/13-frontend.md`：前端后台与场控台。
17. `docs/14-testing-strategy.md`：测试策略。
18. `docs/15-deployment-ops.md`：部署与运维。
19. `docs/16-security-privacy.md`：安全与隐私。
20. `docs/17-milestones.md`：阶段里程碑。
21. `docs/18-codex-issues.md`：Codex Issue 拆分。
22. `docs/19-acceptance-checklists.md`：验收清单。
23. `docs/prompts/codex-initial-prompt.md`：首次交给 Codex 的启动 Prompt。

## MVP 主链路

```text
商品资料录入
  ↓
FAQ / 卖点 / 售后 / 禁止表达入库
  ↓
知识切片 + Qdrant 向量索引
  ↓
启动直播场次
  ↓
平台评论进入 Platform Adapter
  ↓
统一转成 PlatformEvent
  ↓
CommentRouter 去重、限流、意图识别、绑定商品
  ↓
ProductRAG 检索结构化事实与知识片段
  ↓
LLMGateway 生成候选回答
  ↓
ComplianceService 审核
  ↓
HumanReviewService 人工确认
  ↓
TTSService 生成语音
  ↓
AvatarGateway 调用 LiveTalking 播报
  ↓
OBS / SRS 预览与推流
  ↓
日志、审核记录、播报记录留存
```

## 第一版严控范围

包含：

- 单商家
- 单直播间
- MockPlatformAdapter
- 商品库
- 商品 FAQ / 卖点 / 售后 / 禁止表达
- 评论模拟器
- 商品问答
- 合规审核
- 人工审核
- TTS Mock + 可选 EdgeTTS
- Avatar Mock + LiveTalking Gateway 预留
- 场控台基础版
- 全链路日志
- Docker Compose 本地开发环境

暂不包含：

- 多租户 SaaS
- 计费系统
- 多账号矩阵
- 全平台真实接入
- 全自动无人直播
- 自动投流广告
- GPU 集群调度
- 高级数据大屏

## Codex 开发原则

- 不要一次性实现整个系统。
- 先跑通 Mock 全链路，再逐步替换真实 Provider。
- 所有外部能力必须通过 Gateway / Adapter 抽象层调用。
- 每个模块必须有单元测试。
- 每个阶段必须有 E2E 验收链路。
- 所有 AI 生成播报必须经过 ComplianceService。
- 高风险问题必须人工审核。
- 每句话都必须留日志。



---

# 文件：`AGENTS.md`

# AGENTS.md

## Project Goal

Build a digital human live streaming system for ecommerce live rooms.

Primary platforms:

- Taobao Live
- Douyin
- Xiaohongshu
- WeChat Channels
- Future: TikTok

The system must support digital human product explanation, comment handling, product RAG, AI answer generation, compliance review, human review, TTS, avatar playback, OBS/SRS media output, and audit logging.

## Non-Negotiable Architecture Rules

- Do not call platform APIs directly from business services.
- All platform integrations must go through `PlatformAdapter`.
- Do not call LLM providers directly from business logic.
- All LLM calls must go through `LLMGateway`.
- Do not call TTS providers directly from business logic.
- All TTS calls must go through `TTSService`.
- Do not couple LiveTalking directly with `LiveControlService`.
- All avatar commands must go through `AvatarGateway`.
- Do not bypass `ComplianceService` before digital human playback.
- Every AI-generated speech must pass compliance review before playback.
- Medium-risk and high-risk answers must require human review unless explicitly configured otherwise.
- Blocked answers must never be played.
- Every broadcasted sentence must be logged.
- Every live-state transition must be recorded.
- Every platform raw event must be stored or hash-logged for audit and debugging.
- Tests must not require real platform credentials.
- Use mock providers for platform, LLM, TTS, avatar, and media in automated tests.

## Security Rules

- Never commit secrets.
- Use environment variables or secret managers for credentials.
- Mask platform tokens, API keys, and user identifiers in logs.
- Do not store unnecessary personal data.
- Store platform raw payloads with configurable retention.
- Validate all uploaded files by type, size, and extension.
- Audio clone features must require a voice authorization record.
- Avatar assets must require ownership or usage authorization records.
- Do not implement unofficial scraping, packet capture, credential bypass, or platform anti-bot circumvention.
- If official platform APIs are unavailable, implement a `ManualInputAdapter` or `MockPlatformAdapter`, not a policy-violating workaround.

## Coding Stack

Backend:

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis + Redis Streams
- Qdrant
- MinIO-compatible object storage
- pytest
- ruff
- mypy where practical

Frontend:

- Vue 3
- TypeScript
- Element Plus
- Pinia
- Vue Router
- Axios
- WebSocket client
- ECharts for dashboards

Infrastructure:

- Docker Compose for local development
- Nginx gateway when needed
- SRS for RTMP/WebRTC preview and media routing
- OBS used on a streaming workstation, not necessarily containerized

## Directory Rules

- `apps/api-server`: FastAPI app entrypoint, routing, dependency injection, auth, OpenAPI.
- `apps/admin-web`: admin dashboard.
- `apps/control-web`: live control room dashboard.
- `services/platform-adapter`: platform adapter abstraction and implementations.
- `services/live-control`: live sessions, state machine, comment routing, speech queue, takeover.
- `services/product-rag`: products, SKU, FAQ, RAG indexing and retrieval.
- `services/llm-gateway`: LLM providers, prompt templates, model routing.
- `services/compliance`: rules, risk classification, human review workflow.
- `services/tts-service`: TTS provider abstraction, audio cache, voice licenses.
- `services/avatar-gateway`: Avatar provider abstraction, LiveTalking integration, mock avatar.
- `services/media-service`: SRS, stream health, recording, preview URLs.
- `packages/event-schema`: shared event schema.
- `packages/shared-types`: shared Pydantic/TypeScript types.
- `packages/prompt-templates`: versioned prompts.
- `infra`: local infrastructure configuration.
- `docs`: product, architecture, API, data, testing, deployment documentation.

## Development Rules

- Prefer small, testable modules.
- Prefer explicit state machines over implicit control flow.
- Use typed request/response schemas for every API.
- Use Alembic migrations for every database change.
- Add unit tests for every new service.
- Add integration tests for every important workflow.
- Include a mock provider before adding a real external provider.
- Do not introduce a new production dependency without explaining why.
- Update docs when changing public APIs, events, or state machine rules.

## Test Commands

Until the repository is fully bootstrapped, implement these commands in `Makefile`:

```bash
make install
make up
make down
make migrate
make seed
make test
make lint
make typecheck
make e2e
```

## Pull Request Expectations

Every PR must include:

- Summary of changes.
- Affected modules.
- Database migrations if any.
- Tests added/updated.
- Known limitations.
- Manual verification steps.
- Security and compliance considerations if the PR touches platform, AI, voice, avatar, or live playback.

## Done Definition

A task is not done until:

- Code compiles/runs.
- Tests pass.
- Public APIs are documented.
- Error cases are handled.
- Logs are structured and do not leak secrets.
- Mock tests do not depend on external credentials.
- Business rules in docs remain accurate.



---

# 文件：`docs/00-codex-handoff.md`

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



---

# 文件：`docs/01-prd.md`

# 01. 产品需求文档 PRD

## 1. 项目背景

电商直播场景需要高频讲品、实时互动、价格解释、促销引导、售后答疑和长时间稳定开播。数字人直播系统的价值在于降低基础讲解成本，提高标准化答疑能力，并让真人场控聚焦复杂问题和成交转化。

本系统面向：

- 品牌自播团队
- 电商服务商
- MCN / 代运营公司
- 店铺矩阵直播团队
- 后续跨境 TikTok Shop 团队

## 2. 目标平台

MVP 优先：

1. 淘宝直播
2. 抖音

后续扩展：

3. 小红书
4. 视频号
5. TikTok

## 3. 产品目标

### 3.1 MVP 目标

实现一个单商家、单直播间、单数字人的可用闭环：

- 商品资料录入。
- 商品 FAQ 与卖点管理。
- Mock 平台评论接入。
- AI 根据商品知识生成候选回答。
- 候选回答经过合规审核。
- 场控人工确认后数字人播报。
- 播报、审核、评论、状态全链路留痕。
- 可接入 LiveTalking 做真实数字人播报。
- 可通过 OBS/SRS 预览或推流。

### 3.2 生产目标

- 支持淘宝直播、抖音、小红书、视频号、TikTok 的平台 Adapter。
- 支持多直播间。
- 支持多数字人形象和多音色。
- 支持商品知识库、平台差异话术、类目规则。
- 支持人工接管和异常兜底。
- 支持合规标识、敏感词、功效宣称、价格一致性校验。
- 支持数据分析、直播复盘、转化评估。

## 4. 用户角色

| 角色 | 权限 |
|---|---|
| 超级管理员 | 管理所有商家、平台配置、系统配置 |
| 商家管理员 | 管理本商家的店铺、商品、直播间、数字人 |
| 运营人员 | 配置商品、话术、排班、直播脚本 |
| 场控人员 | 监控直播、审核回答、人工接管 |
| 审核人员 | 维护合规规则、审核高风险话术 |
| 技术运维 | 查看系统状态、平台连接、推流状态、日志 |

## 5. 核心业务场景

### 5.1 商品循环讲解

系统根据当前直播商品池自动调度商品讲解脚本：

```text
选择商品 → 读取卖点 → 生成/读取脚本 → 合规审核 → TTS → 数字人播报
```

### 5.2 评论问答

观众评论进入后，系统进行：

```text
去重 → 黑名单过滤 → 意图识别 → 商品定位 → 知识库检索 → 候选回答 → 合规审核 → 人工确认 → 播报
```

### 5.3 人工接管

场控随时可以：

- 打断数字人当前播报。
- 暂停 AI 自动讲解。
- 手动输入文本让数字人播报。
- 切换真人语音或备用视频。
- 恢复 AI 自动流程。

### 5.4 异常兜底

必须处理：

- LLM 超时。
- TTS 失败。
- LiveTalking 卡死。
- OBS/SRS 推流中断。
- 平台事件中断。
- 平台警告。
- 审核队列积压。

## 6. 功能模块

### 6.1 商家与店铺管理

- 商家创建、编辑、禁用。
- 店铺管理。
- 平台账号配置。
- 平台授权状态显示。

### 6.2 商品管理

- 商品 CRUD。
- SKU 管理。
- 价格 / 库存 / 优惠券。
- FAQ。
- 商品卖点。
- 售后 / 发货 / 退换规则。
- 禁止表达。
- 平台差异话术。
- 商品资料导入。
- 知识库索引。

### 6.3 直播管理

- 直播间管理。
- 直播场次管理。
- 商品池。
- 当前讲解商品。
- 直播状态机。
- 直播日志。

### 6.4 评论处理

- 平台事件接入。
- 评论标准化。
- 评论去重。
- 黑名单过滤。
- 意图识别。
- 优先级排序。
- 绑定商品。
- 生成任务。

### 6.5 AI 问答

- 多模型网关。
- Prompt 模板。
- 商品 RAG。
- 平台改写。
- 缓存回答。
- 模型调用日志。

### 6.6 合规审核

- 敏感词。
- 绝对化用语。
- 价格一致性。
- 功效宣称。
- 类目规则。
- 平台规则。
- AI 标识检查。
- 人工审核。
- 审核日志。

### 6.7 TTS 与数字人

- TTS Provider。
- 音色管理。
- 音色授权。
- 音频缓存。
- LiveTalking 接入。
- 数字人播报。
- 播报打断。
- 形象切换。
- 场景切换。

### 6.8 媒体与推流

- SRS 预览。
- RTMP/WebRTC 状态检测。
- OBS 配置说明。
- 录制。
- 备用视频。

### 6.9 前端后台

- 管理后台。
- 场控台。
- 审核台。
- 数据看板。
- 系统监控。

## 7. 非功能需求

### 7.1 可用性

- 主链路失败时必须有降级方案。
- 不能因 LLM 失败导致直播中断。
- 不能因 TTS 失败导致系统崩溃。

### 7.2 可审计

每条播报必须记录：

- 来源评论。
- 候选回答。
- 模型信息。
- Prompt 版本。
- 合规结果。
- 审核人。
- TTS 音色。
- 播报时间。

### 7.3 可扩展

- 平台接入通过 Adapter 扩展。
- LLM 通过 Provider 扩展。
- TTS 通过 Provider 扩展。
- 数字人通过 AvatarProvider 扩展。

### 7.4 安全

- 不提交密钥。
- Token 脱敏。
- 用户信息最小化存储。
- 音色和数字人资产必须有授权记录。

## 8. MVP 成功标准

- Mock 全链路 E2E 测试通过。
- 场控台可看到评论、候选回答、审核结果、播报任务。
- 所有 AI 播报都经过 ComplianceService。
- 高风险回答不会自动播报。
- LiveTalking Gateway 可接入或 Mock 可替换。
- 本地 Docker Compose 可启动基础依赖。



---

# 文件：`docs/02-architecture.md`

# 02. 总体架构设计

## 1. 架构原则

本系统采用“模块化单体起步、可拆微服务演进”的架构。

第一版不要过度微服务化。建议先在一个 monorepo 中实现清晰模块边界，后续按压力和组织结构拆分服务。

核心原则：

1. 平台接入和业务中控解耦。
2. LLM、TTS、数字人均通过 Gateway/Provider 抽象。
3. 所有播报必须经过合规审核。
4. 直播流程由状态机控制，不由 LLM 控制。
5. 商品事实由数据库和知识库提供，不由 LLM 编造。
6. 所有核心动作可追溯。

## 2. 系统上下文

```text
┌─────────────────────────────────────────────────────────────┐
│                         外部系统                             │
│ 淘宝直播 / 抖音 / 小红书 / 视频号 / TikTok / OBS / LiveTalking │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Digital Human Live System                  │
│ 平台接入 / 商品库 / 中控 / AI / 合规 / TTS / 数字人 / 后台       │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                         基础设施                             │
│ PostgreSQL / Redis / Qdrant / MinIO / SRS / Prometheus        │
└─────────────────────────────────────────────────────────────┘
```

## 3. 逻辑架构

```text
┌──────────────────────────────────────────────┐
│                直播平台层                     │
│ 淘宝直播 / 抖音 / 小红书 / 视频号 / TikTok      │
└──────────────────────┬───────────────────────┘
                       │ 评论、订单、上下播、商品、平台警告
                       ↓
┌──────────────────────────────────────────────┐
│                Platform Adapter              │
│ 平台 API / Webhook / SDK / 人工输入 / Mock     │
│ 输出统一 PlatformEvent                         │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Event Gateway                  │
│ 去重 / 鉴权 / 限流 / 标准化 / 写入事件日志       │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Live Control Service           │
│ 直播状态机 / 商品调度 / 评论队列 / 人工接管      │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Product & RAG Service          │
│ 商品事实 / SKU / 价格 / 库存 / FAQ / 向量检索    │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                LLM Gateway                    │
│ 意图识别 / 候选回答 / 平台改写 / 话术生成        │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Compliance Service             │
│ 敏感词 / 绝对化 / 功效宣称 / 价格校验 / 人审      │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Human Review Service           │
│ 审核任务 / 通过 / 拒绝 / 改写 / 人工播报          │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                TTS Service                    │
│ 音色授权 / 语音合成 / 语音缓存 / 失败兜底         │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Avatar Gateway                 │
│ LiveTalking / 播报 / 打断 / 待机 / 形象切换      │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Media Service                  │
│ OBS / SRS / RTMP / WebRTC / 录制 / 预览         │
└──────────────────────────────────────────────┘
```

## 4. 物理部署架构

### 4.1 本地开发

```text
开发机
├── api-server
├── admin-web
├── control-web
├── postgres container
├── redis container
├── qdrant container
├── minio container
└── srs container

可选 GPU 机器 / 本机
└── LiveTalking

直播工作站
├── OBS
└── 平台直播伴侣
```

### 4.2 测试环境

```text
应用服务器
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
```

### 4.3 生产环境

```text
入口层
├── Nginx / API Gateway
└── TLS / WAF / 限流

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

## 5. 主链路时序图

```text
PlatformAdapter → EventGateway: PlatformEvent(CommentReceived)
EventGateway → CommentRouter: create comment task
CommentRouter → ProductRAG: resolve product and retrieve facts
ProductRAG → LLMGateway: generate candidate answer
LLMGateway → ComplianceService: review candidate
ComplianceService → HumanReviewService: create review task if needed
HumanReviewService → SpeechQueueService: approve and enqueue speech
SpeechQueueService → TTSService: generate audio
TTSService → AvatarGateway: speak_audio
AvatarGateway → LiveTalking: play audio with lip sync
AvatarGateway → SpeechQueueService: speech finished
SpeechQueueService → AuditLog: write playback log
```

## 6. 降级链路

| 故障 | 降级策略 |
|---|---|
| LLM 超时 | 使用缓存回答或固定兜底话术 |
| RAG 无命中 | 转人工审核，不自动回答 |
| ComplianceService 异常 | 默认拒绝自动播报，转人工 |
| TTS 失败 | 切备用 TTS Provider 或备用音色 |
| LiveTalking 失败 | 切待机视频 / 备用视频 / 静音 |
| 平台事件中断 | 场控台提示，允许人工输入评论 |
| 推流中断 | SRS/OBS 状态告警，暂停自动播报 |
| 平台警告 | 立即进入人工接管模式 |

## 7. 演进路线

MVP：模块化单体 + Mock Provider。

生产初期：保留单体 API，但后台任务和外部 Provider 拆 worker。

规模化：拆成以下服务：

- platform-adapter-service
- live-control-service
- product-rag-service
- llm-gateway-service
- compliance-service
- tts-service
- avatar-gateway-service
- media-service
- analytics-service



---

# 文件：`docs/03-repo-structure.md`

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



---

# 文件：`docs/04-module-boundaries.md`

# 04. 模块边界说明

## 1. 模块依赖总览

```text
PlatformAdapter
  ↓
EventGateway
  ↓
LiveControlService
  ├── ProductRAGService
  ├── LLMGateway
  ├── ComplianceService
  ├── HumanReviewService
  ├── TTSService
  ├── AvatarGateway
  └── MediaService
```

所有外部系统必须通过 Adapter 或 Gateway 进入系统，不允许业务模块直接依赖第三方 SDK。

## 2. Platform Adapter

### 职责

- 处理平台授权配置。
- 接收平台事件。
- 验签、鉴权、去重。
- 保存 raw payload。
- 标准化为 `PlatformEvent`。
- 输出到事件流。
- 上报平台连接状态和异常。

### 不负责

- 不做商品问答。
- 不调用 LLM。
- 不调用 TTS。
- 不调用 AvatarGateway。
- 不做合规判断。
- 不决定是否播报。

### 接口

```python
class PlatformAdapter:
    async def start(self, room_id: str) -> None: ...
    async def stop(self, room_id: str) -> None: ...
    async def get_live_status(self, room_id: str) -> LiveStatus: ...
    async def get_products(self, room_id: str) -> list[PlatformProduct]: ...
    async def subscribe_comments(self, room_id: str) -> None: ...
    async def subscribe_orders(self, room_id: str) -> None: ...
    async def normalize_event(self, raw_event: dict) -> PlatformEvent: ...
```

## 3. Event Gateway

### 职责

- 接收 Adapter 输出的标准事件。
- 事件去重。
- 基础限流。
- 写入 `platform_event_log`。
- 发布到 Redis Streams。

### 输入

`PlatformEvent`

### 输出

Redis Stream：

```text
stream:platform_events
```

## 4. Live Control Service

### 职责

- 直播场次生命周期。
- 显式状态机。
- 评论任务调度。
- 商品讲解调度。
- 播报队列。
- 人工接管。
- 异常降级。
- 状态日志。

### 子模块

```text
LiveSessionService
ScriptScheduler
CommentRouter
SpeechQueueService
TakeoverService
FallbackService
LiveEventLogger
```

### 禁止

- 禁止直接调用平台 API。
- 禁止直接调用 LLM Provider。
- 禁止直接调用 TTS Provider。
- 禁止直接调用 LiveTalking。
- 禁止绕过 ComplianceService。

## 5. Product & RAG Service

### 职责

- 商品管理。
- SKU、价格、库存。
- 商品 FAQ。
- 商品卖点。
- 发货、售后、退换规则。
- 禁止表达。
- 平台差异话术。
- 知识切片。
- 向量索引。
- RAG 检索。

### 数据来源分层

```text
结构化事实：PostgreSQL
语义知识：Qdrant
热点缓存：Redis
文件资料：MinIO
```

### 禁止

- 禁止让 LLM 猜测价格。
- 禁止把实时库存只存向量库。
- 禁止用过期商品信息回答用户。

## 6. LLM Gateway

### 职责

- 多模型路由。
- Prompt 模板版本管理。
- 超时、重试、降级。
- Token 与成本记录。
- 模型调用日志。

### 能力

```python
class LLMGateway:
    async def classify_comment(self, request): ...
    async def generate_product_answer(self, request): ...
    async def rewrite_for_platform(self, request): ...
    async def compliance_review(self, request): ...
    async def generate_script(self, request): ...
```

### Provider

```text
MockProvider
OpenAICompatibleProvider
QwenProvider
DeepSeekProvider
KimiProvider
GLMProvider
LocalModelProvider
```

## 7. Compliance Service

### 职责

- 规则审核。
- LLM 复核。
- 风险分级。
- 人工审核任务创建。
- 审核结果记录。
- 平台差异规则。
- AI 标识检查。

### 输出

```json
{
  "blocked": false,
  "risk_level": "medium",
  "need_human_review": true,
  "reasons": [],
  "suggested_rewrite": "..."
}
```

### 默认策略

- 审核服务异常时，不得自动播报。
- 高风险默认进入人工审核。
- blocked 必须禁止播报。

## 8. Human Review Service

### 职责

- 创建审核任务。
- 通过、拒绝、改写。
- 手动回答。
- 记录审核人和审核时间。
- 推送审核状态到场控台。

### 状态

```text
PENDING
APPROVED
REJECTED
REWRITTEN
EXPIRED
CANCELLED
```

## 9. TTS Service

### 职责

- TTS Provider 管理。
- 音色管理。
- 音色授权校验。
- 音频缓存。
- 生成任务。
- 失败降级。
- 音频文件存储。

### Provider

```text
MockTTSProvider
EdgeTTSProvider
CosyVoiceProvider
GPTSoVITSProvider
AliyunTTSProvider
TencentTTSProvider
FallbackTTSProvider
```

## 10. Avatar Gateway

### 职责

- 隔离 LiveTalking。
- 文本播报。
- 音频播报。
- 打断播报。
- 待机状态。
- 切换数字人。
- 切换场景。
- 查询流地址。
- 健康检查。

### Provider

```text
MockAvatarProvider
LiveTalkingProvider
FallbackVideoProvider
```

## 11. Media Service

### 职责

- SRS 预览 URL。
- RTMP/WebRTC 健康检查。
- 录制开始/停止。
- OBS 配置提示。
- 媒体流状态上报。

## 12. Frontend Apps

### admin-web

用于配置和管理。

### control-web

用于直播实时场控。

### monitor-web

用于系统监控，可后置。

## 13. 模块调用规则

| 调用方 | 允许调用 | 禁止调用 |
|---|---|---|
| PlatformAdapter | EventGateway | LLM/TTS/Avatar |
| LiveControl | ProductRAG/LLMGateway/Compliance/HumanReview/TTS/Avatar | 外部平台 SDK |
| ProductRAG | DB/Qdrant/Redis | Avatar/平台 API |
| LLMGateway | LLM Provider | DB 写业务状态 |
| Compliance | 规则库/LLMGateway | Avatar |
| TTSService | TTS Provider/MinIO | LLM/平台 API |
| AvatarGateway | LiveTalking | Compliance/平台 API |



---

# 文件：`docs/05-event-schema.md`

# 05. 平台事件标准化

## 1. 目标

不同平台事件格式不同，必须统一转为 `PlatformEvent` 后再进入业务系统。

平台 Adapter 只负责标准化，不负责业务决策。

## 2. 标准事件类型

```text
LiveStarted
LiveEnded
CommentReceived
LikeReceived
GiftReceived
FollowReceived
OrderCreated
ProductChanged
ProductClicked
UserEntered
PlatformWarningReceived
PlatformStreamInterrupted
ManualCommentEntered
```

## 3. PlatformEvent JSON

```json
{
  "event_id": "evt_20260707_000001",
  "platform": "taobao",
  "room_id": "room_001",
  "live_session_id": "session_001",
  "event_type": "CommentReceived",
  "timestamp": 1783410000,
  "user": {
    "platform_user_id": "u_hash_123",
    "nickname": "用户昵称",
    "level": "normal",
    "is_blacklisted": false
  },
  "content": "这款敏感肌可以用吗？",
  "product": {
    "platform_product_id": "tb_10001",
    "internal_product_id": "prod_001",
    "sku_id": "sku_001"
  },
  "metadata": {
    "source": "webhook",
    "trace_id": "trace_xxx"
  },
  "raw": {}
}
```

## 4. 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| event_id | string | 是 | 全局唯一事件 ID，平台无 ID 时生成 hash |
| platform | enum | 是 | taobao/douyin/xhs/wechat_channels/tiktok/mock/manual |
| room_id | string | 是 | 平台或内部直播间 ID |
| live_session_id | string | 否 | 内部直播场次 ID，可后续绑定 |
| event_type | enum | 是 | 事件类型 |
| timestamp | integer | 是 | 秒级或毫秒级时间戳，统一转换 |
| user | object | 否 | 用户信息，尽量脱敏 |
| content | string | 否 | 评论或文本内容 |
| product | object | 否 | 商品映射 |
| metadata | object | 否 | 标准元信息 |
| raw | object | 是 | 原始 payload，按配置保存或脱敏保存 |

## 5. Redis Stream

使用 Redis Streams 做 MVP 事件队列。

```text
stream:platform_events       平台事件
stream:comment_tasks         评论任务
stream:review_tasks          审核任务
stream:speech_tasks          播报任务
stream:avatar_commands       数字人指令
stream:system_alerts         系统告警
```

事件消息示例：

```json
{
  "event_id": "evt_001",
  "event_type": "CommentReceived",
  "payload": "{...json...}"
}
```

## 6. 去重策略

去重 key：

```text
platform + platform_event_id
```

如果平台没有 event id：

```text
hash(platform + room_id + event_type + user_id + content + timestamp_bucket)
```

Redis key：

```text
dedupe:platform_event:{event_id}
```

TTL：建议 24 小时。

## 7. 评论标准化流程

```text
平台 raw payload
  ↓
验签 / 鉴权
  ↓
字段提取
  ↓
用户信息脱敏
  ↓
商品 ID 映射
  ↓
生成 event_id
  ↓
写入 platform_event_log
  ↓
发布 PlatformEvent
```

## 8. Pydantic Schema 草案

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional

class Platform(str, Enum):
    TAOBAO = "taobao"
    DOUYIN = "douyin"
    XHS = "xhs"
    WECHAT_CHANNELS = "wechat_channels"
    TIKTOK = "tiktok"
    MOCK = "mock"
    MANUAL = "manual"

class PlatformEventType(str, Enum):
    LIVE_STARTED = "LiveStarted"
    LIVE_ENDED = "LiveEnded"
    COMMENT_RECEIVED = "CommentReceived"
    LIKE_RECEIVED = "LikeReceived"
    GIFT_RECEIVED = "GiftReceived"
    FOLLOW_RECEIVED = "FollowReceived"
    ORDER_CREATED = "OrderCreated"
    PRODUCT_CHANGED = "ProductChanged"
    PRODUCT_CLICKED = "ProductClicked"
    USER_ENTERED = "UserEntered"
    PLATFORM_WARNING_RECEIVED = "PlatformWarningReceived"
    PLATFORM_STREAM_INTERRUPTED = "PlatformStreamInterrupted"
    MANUAL_COMMENT_ENTERED = "ManualCommentEntered"

class PlatformUser(BaseModel):
    platform_user_id: Optional[str] = None
    nickname: Optional[str] = None
    level: Optional[str] = None
    is_blacklisted: bool = False

class PlatformProductRef(BaseModel):
    platform_product_id: Optional[str] = None
    internal_product_id: Optional[str] = None
    sku_id: Optional[str] = None

class PlatformEvent(BaseModel):
    event_id: str
    platform: Platform
    room_id: str
    live_session_id: Optional[str] = None
    event_type: PlatformEventType
    timestamp: int
    user: Optional[PlatformUser] = None
    content: Optional[str] = None
    product: Optional[PlatformProductRef] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)
```



---

# 文件：`docs/06-live-state-machine.md`

# 06. 直播状态机

## 1. 为什么必须使用状态机

电商直播不是普通聊天机器人。系统必须明确知道当前直播处于什么阶段，什么动作允许发生，什么动作必须禁止。

LLM 不能直接控制直播流程。LLM 只能作为分类、生成、改写、审核辅助。

## 2. 状态定义

```text
CREATED                 直播场次已创建
WARMING_UP              预热中
EXPLAINING_PRODUCT      商品讲解中
WAITING_INTERACTION     等待互动处理
GENERATING_ANSWER       生成候选回答中
WAITING_HUMAN_REVIEW    等待人工审核
SPEAKING                数字人播报中
HUMAN_TAKEOVER          人工接管中
FALLBACK                异常降级中
PAUSED                  暂停
ENDED                   已结束
```

## 3. 状态流转图

```text
CREATED
  │ start_live
  ↓
WARMING_UP
  │ warmup_done
  ↓
EXPLAINING_PRODUCT
  │ comment_received
  ↓
WAITING_INTERACTION
  │ need_answer
  ↓
GENERATING_ANSWER
  │ answer_generated
  ↓
WAITING_HUMAN_REVIEW
  │ approved
  ↓
SPEAKING
  │ speech_finished
  └──────────────→ EXPLAINING_PRODUCT

任意状态 ── human_takeover ──→ HUMAN_TAKEOVER
HUMAN_TAKEOVER ── release_takeover ──→ EXPLAINING_PRODUCT
任意状态 ── system_error ──→ FALLBACK
FALLBACK ── recover ──→ EXPLAINING_PRODUCT
任意状态 ── pause ──→ PAUSED
PAUSED ── resume ──→ EXPLAINING_PRODUCT
任意状态 ── end_live ──→ ENDED
```

## 4. 状态转移表

| 当前状态 | 事件 | 下一个状态 | 动作 |
|---|---|---|---|
| CREATED | start_live | WARMING_UP | 创建日志，加载商品池，启动平台监听 |
| WARMING_UP | warmup_done | EXPLAINING_PRODUCT | 加入开场话术 |
| EXPLAINING_PRODUCT | comment_received | WAITING_INTERACTION | 评论入队，不打断当前播报 |
| WAITING_INTERACTION | need_answer | GENERATING_ANSWER | 启动意图识别与 RAG |
| WAITING_INTERACTION | no_answer_needed | EXPLAINING_PRODUCT | 忽略或归档评论 |
| GENERATING_ANSWER | answer_generated | WAITING_HUMAN_REVIEW | 创建候选回答和审核任务 |
| GENERATING_ANSWER | answer_failed | EXPLAINING_PRODUCT | 使用兜底策略或转人工 |
| WAITING_HUMAN_REVIEW | approved | SPEAKING | 创建 TTS 和播报任务 |
| WAITING_HUMAN_REVIEW | rejected | EXPLAINING_PRODUCT | 记录拒绝原因 |
| WAITING_HUMAN_REVIEW | rewritten | SPEAKING | 使用人工改写内容播报 |
| SPEAKING | speech_finished | EXPLAINING_PRODUCT | 标记播报完成 |
| SPEAKING | interrupt | EXPLAINING_PRODUCT | 打断并记录 |
| 任意状态 | human_takeover | HUMAN_TAKEOVER | 暂停 AI 队列，打断播报 |
| HUMAN_TAKEOVER | manual_speak | HUMAN_TAKEOVER | 人工播报 |
| HUMAN_TAKEOVER | release_takeover | EXPLAINING_PRODUCT | 恢复 AI 讲品 |
| 任意状态 | system_error | FALLBACK | 切备用视频或静音 |
| FALLBACK | recover | EXPLAINING_PRODUCT | 恢复正常流程 |
| 任意状态 | pause | PAUSED | 暂停队列 |
| PAUSED | resume | EXPLAINING_PRODUCT | 恢复讲品 |
| 任意状态 | end_live | ENDED | 停止队列，保存总结 |

## 5. 非法转移示例

| 当前状态 | 事件 | 结果 |
|---|---|---|
| CREATED | approved | 拒绝 |
| ENDED | start_live | 拒绝，必须新建场次 |
| SPEAKING | start_live | 拒绝 |
| FALLBACK | approved | 拒绝，必须 recover 后再播报 |
| HUMAN_TAKEOVER | auto_answer | 拒绝，人工接管期间不能自动播报 |

## 6. 状态机实现要求

- 使用显式转移表。
- 非法转移必须抛出业务异常。
- 每次转移写入 `live_state_log`。
- 状态转移必须带 `triggered_by`。
- 状态转移必须带 `reason`。
- 状态转移必须可回放。

## 7. 事件结构

```json
{
  "session_id": "session_001",
  "from_state": "EXPLAINING_PRODUCT",
  "to_state": "WAITING_INTERACTION",
  "event": "comment_received",
  "triggered_by": "system",
  "reason": "new comment received",
  "metadata": {
    "comment_task_id": "ct_001"
  },
  "created_at": "2026-07-07T12:00:00+08:00"
}
```

## 8. Python 草案

```python
from enum import Enum

class LiveState(str, Enum):
    CREATED = "CREATED"
    WARMING_UP = "WARMING_UP"
    EXPLAINING_PRODUCT = "EXPLAINING_PRODUCT"
    WAITING_INTERACTION = "WAITING_INTERACTION"
    GENERATING_ANSWER = "GENERATING_ANSWER"
    WAITING_HUMAN_REVIEW = "WAITING_HUMAN_REVIEW"
    SPEAKING = "SPEAKING"
    HUMAN_TAKEOVER = "HUMAN_TAKEOVER"
    FALLBACK = "FALLBACK"
    PAUSED = "PAUSED"
    ENDED = "ENDED"

TRANSITIONS = {
    (LiveState.CREATED, "start_live"): LiveState.WARMING_UP,
    (LiveState.WARMING_UP, "warmup_done"): LiveState.EXPLAINING_PRODUCT,
    (LiveState.EXPLAINING_PRODUCT, "comment_received"): LiveState.WAITING_INTERACTION,
    (LiveState.WAITING_INTERACTION, "need_answer"): LiveState.GENERATING_ANSWER,
    (LiveState.WAITING_INTERACTION, "no_answer_needed"): LiveState.EXPLAINING_PRODUCT,
    (LiveState.GENERATING_ANSWER, "answer_generated"): LiveState.WAITING_HUMAN_REVIEW,
    (LiveState.GENERATING_ANSWER, "answer_failed"): LiveState.EXPLAINING_PRODUCT,
    (LiveState.WAITING_HUMAN_REVIEW, "approved"): LiveState.SPEAKING,
    (LiveState.WAITING_HUMAN_REVIEW, "rejected"): LiveState.EXPLAINING_PRODUCT,
    (LiveState.WAITING_HUMAN_REVIEW, "rewritten"): LiveState.SPEAKING,
    (LiveState.SPEAKING, "speech_finished"): LiveState.EXPLAINING_PRODUCT,
    (LiveState.SPEAKING, "interrupt"): LiveState.EXPLAINING_PRODUCT,
}

GLOBAL_TRANSITIONS = {
    "human_takeover": LiveState.HUMAN_TAKEOVER,
    "system_error": LiveState.FALLBACK,
    "pause": LiveState.PAUSED,
    "end_live": LiveState.ENDED,
}
```

## 9. 必须测试

- 所有合法状态转移。
- 所有非法状态转移。
- 任意状态进入人工接管。
- 人工接管期间禁止自动播报。
- ENDED 后禁止继续处理评论。
- FALLBACK 后必须 recover 才能恢复。
- 状态日志写入。



---

# 文件：`docs/07-data-model.md`

# 07. 数据模型设计

## 1. 数据库选择

MVP 使用 PostgreSQL 作为主库。

Redis 用于缓存和轻队列。

Qdrant 用于商品 FAQ、卖点、知识片段向量检索。

MinIO/OSS/COS 用于音频、视频、图片、授权文件、录制文件。

## 2. 核心实体

```text
merchant                 商家
user                     用户
role                     角色
permission               权限
shop                     店铺
platform_account         平台账号
live_room                直播间
live_session             直播场次
live_state_log           直播状态日志
product                  商品
product_sku              SKU
product_price            平台价格
product_inventory        库存
product_selling_point    商品卖点
product_faq              FAQ
product_policy           售后 / 发货 / 退换规则
product_forbidden_claim  禁止表达
product_platform_copy    平台差异话术
knowledge_chunk          知识切片
platform_event_log       平台事件日志
comment_task             评论任务
answer_candidate         候选回答
compliance_result        合规结果
human_review_task        人工审核任务
speech_task              播报任务
tts_asset                TTS 音频资产
voice_profile            音色
voice_license            音色授权
avatar                   数字人形象
avatar_command_log       数字人指令日志
media_stream             媒体流
recording_asset          录制资产
audit_log                审计日志
system_config            系统配置
```

## 3. 多租户边界

MVP 可以单商家，但数据模型从一开始保留 `merchant_id`。

所有业务表原则上都应有：

```text
id
merchant_id
created_at
updated_at
```

日志类表可保留：

```text
id
merchant_id
live_session_id
created_at
```

## 4. 商品数据模型

商品必须分结构化数据和语义知识。

结构化数据：

- 商品标题。
- 品牌。
- 类目。
- SKU。
- 价格。
- 到手价。
- 优惠券。
- 库存。
- 发货时效。
- 售后政策。

语义知识：

- 商品卖点。
- FAQ。
- 成分说明。
- 使用方法。
- 适用人群。
- 禁忌人群。
- 场景化话术。

## 5. 评论与回答数据模型

```text
platform_event_log
  ↓
comment_task
  ↓
answer_candidate
  ↓
compliance_result
  ↓
human_review_task
  ↓
speech_task
  ↓
tts_asset
  ↓
avatar_command_log
```

## 6. 状态字段建议

### comment_task.status

```text
pending
processing
ignored
answer_generated
reviewing
approved
rejected
spoken
failed
```

### answer_candidate.status

```text
generated
compliance_passed
compliance_blocked
waiting_human_review
approved
rejected
rewritten
expired
```

### speech_task.status

```text
pending
generating_audio
audio_ready
queued
speaking
finished
interrupted
failed
cancelled
```

### human_review_task.status

```text
pending
approved
rejected
rewritten
expired
cancelled
```

## 7. 索引建议

- `platform_event_log(event_id)` 唯一索引。
- `comment_task(live_session_id, status, created_at)`。
- `comment_task(event_id)` 唯一索引。
- `answer_candidate(comment_task_id)`。
- `human_review_task(live_session_id, status, created_at)`。
- `speech_task(live_session_id, status, priority, created_at)`。
- `product(merchant_id, status)`。
- `product_sku(product_id)`。
- `product_price(sku_id, platform)`。

## 8. 审计要求

以下动作必须写入 audit_log：

- 平台账号配置变更。
- 商品价格变更。
- 商品禁止表达变更。
- 合规规则变更。
- 人工审核通过/拒绝/改写。
- 人工接管开始/结束。
- 直播场次开始/结束。
- 音色授权变更。
- 数字人资产变更。



---

# 文件：`docs/08-api-spec.md`

# 08. API 契约说明

## 1. 通用约定

API 前缀：

```text
/api/v1
```

成功响应：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "req_xxx"
}
```

失败响应：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": {}
  },
  "request_id": "req_xxx"
}
```

## 2. 认证接口

```http
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
POST /api/v1/auth/refresh
```

MVP 可先实现简单 JWT。生产需接入企业 SSO 或更严格权限系统。

## 3. 商家与平台账号

```http
POST /api/v1/merchants
GET  /api/v1/merchants
GET  /api/v1/merchants/{merchant_id}
PUT  /api/v1/merchants/{merchant_id}

POST /api/v1/shops
GET  /api/v1/shops
PUT  /api/v1/shops/{shop_id}

POST /api/v1/platform-accounts
GET  /api/v1/platform-accounts
GET  /api/v1/platform-accounts/{account_id}
PUT  /api/v1/platform-accounts/{account_id}
POST /api/v1/platform-accounts/{account_id}/test-connection
```

## 4. 商品接口

```http
POST   /api/v1/products
GET    /api/v1/products
GET    /api/v1/products/{product_id}
PUT    /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}

POST /api/v1/products/{product_id}/skus
GET  /api/v1/products/{product_id}/skus
PUT  /api/v1/products/{product_id}/skus/{sku_id}

POST /api/v1/products/{product_id}/prices
GET  /api/v1/products/{product_id}/prices

POST /api/v1/products/{product_id}/faqs
GET  /api/v1/products/{product_id}/faqs
PUT  /api/v1/products/{product_id}/faqs/{faq_id}
DELETE /api/v1/products/{product_id}/faqs/{faq_id}

POST /api/v1/products/{product_id}/selling-points
GET  /api/v1/products/{product_id}/selling-points

POST /api/v1/products/{product_id}/policies
GET  /api/v1/products/{product_id}/policies

POST /api/v1/products/{product_id}/forbidden-claims
GET  /api/v1/products/{product_id}/forbidden-claims

POST /api/v1/products/import
POST /api/v1/products/{product_id}/index
POST /api/v1/products/{product_id}/generate-script
```

## 5. 直播接口

```http
POST /api/v1/live-rooms
GET  /api/v1/live-rooms
GET  /api/v1/live-rooms/{room_id}
PUT  /api/v1/live-rooms/{room_id}

POST /api/v1/live-sessions
GET  /api/v1/live-sessions
GET  /api/v1/live-sessions/{session_id}
POST /api/v1/live-sessions/{session_id}/start
POST /api/v1/live-sessions/{session_id}/warmup-done
POST /api/v1/live-sessions/{session_id}/pause
POST /api/v1/live-sessions/{session_id}/resume
POST /api/v1/live-sessions/{session_id}/end
GET  /api/v1/live-sessions/{session_id}/state
GET  /api/v1/live-sessions/{session_id}/events
POST /api/v1/live-sessions/{session_id}/products
PUT  /api/v1/live-sessions/{session_id}/current-product
```

## 6. 评论与审核接口

```http
GET  /api/v1/live-sessions/{session_id}/comments
POST /api/v1/live-sessions/{session_id}/comments/mock
POST /api/v1/comments/{comment_task_id}/generate-answer
POST /api/v1/comments/{comment_task_id}/ignore
POST /api/v1/comments/{comment_task_id}/priority

GET  /api/v1/live-sessions/{session_id}/review-tasks
GET  /api/v1/review-tasks/{task_id}
POST /api/v1/review-tasks/{task_id}/approve
POST /api/v1/review-tasks/{task_id}/reject
POST /api/v1/review-tasks/{task_id}/rewrite
POST /api/v1/review-tasks/{task_id}/manual-answer
```

## 7. 人工接管接口

```http
POST /api/v1/live-sessions/{session_id}/takeover/start
POST /api/v1/live-sessions/{session_id}/takeover/stop
POST /api/v1/live-sessions/{session_id}/takeover/speak-text
POST /api/v1/live-sessions/{session_id}/takeover/mute-avatar
POST /api/v1/live-sessions/{session_id}/takeover/fallback-video
POST /api/v1/live-sessions/{session_id}/takeover/interrupt
```

## 8. TTS 接口

```http
POST /api/v1/tts/generate
POST /api/v1/tts/precache
GET  /api/v1/tts/assets/{asset_id}
GET  /api/v1/voices
POST /api/v1/voices
PUT  /api/v1/voices/{voice_id}
POST /api/v1/voices/{voice_id}/license
POST /api/v1/voices/{voice_id}/validate-license
```

### TTS Generate Request

```json
{
  "merchant_id": "merchant_001",
  "text": "这款今天直播间有优惠。",
  "voice_id": "voice_001",
  "language": "zh-CN",
  "speed": 1.0,
  "emotion": "friendly",
  "platform": "taobao",
  "cache_enabled": true
}
```

### TTS Generate Response

```json
{
  "asset_id": "tts_001",
  "audio_url": "s3://bucket/audio/tts_001.wav",
  "duration_ms": 3200,
  "cache_hit": false
}
```

## 9. 数字人接口

```http
POST /api/v1/avatar/speak-text
POST /api/v1/avatar/speak-audio
POST /api/v1/avatar/interrupt
POST /api/v1/avatar/idle
POST /api/v1/avatar/switch-avatar
POST /api/v1/avatar/switch-scene
GET  /api/v1/avatar/stream-url
GET  /api/v1/avatar/health
```

## 10. 媒体接口

```http
GET  /api/v1/live-sessions/{session_id}/media/preview-url
POST /api/v1/live-sessions/{session_id}/media/start-recording
POST /api/v1/live-sessions/{session_id}/media/stop-recording
GET  /api/v1/live-sessions/{session_id}/media/health
GET  /api/v1/live-sessions/{session_id}/media/recordings
```

## 11. WebSocket

场控台实时连接：

```text
/ws/live-sessions/{session_id}
```

服务端推送消息类型：

```text
state_changed
comment_received
answer_generated
compliance_checked
review_task_created
speech_started
speech_finished
avatar_error
platform_warning
stream_health_changed
human_takeover_started
human_takeover_ended
```

示例：

```json
{
  "type": "comment_received",
  "session_id": "session_001",
  "payload": {
    "comment_task_id": "ct_001",
    "content": "这款多少钱？",
    "intent": "price_query"
  },
  "timestamp": 1783410000
}
```



---

# 文件：`docs/09-platform-adapters.md`

# 09. 平台 Adapter 开发说明

## 1. 开发原则

所有平台都必须通过 `PlatformAdapter` 接入。

业务层只消费统一的 `PlatformEvent`，不能依赖淘宝、抖音、小红书、视频号或 TikTok 的原始字段。

## 2. 平台优先级

```text
P0: MockPlatformAdapter
P1: TaobaoLiveAdapter
P2: DouyinAdapter
P3: XiaohongshuAdapter
P4: WeChatChannelsAdapter
P5: TikTokAdapter
P6: ManualInputAdapter
```

必须先实现 MockPlatformAdapter。

## 3. MockPlatformAdapter

### 目标

在没有真实平台权限时跑通全链路。

### 功能

- 创建 Mock 直播间。
- 模拟开播。
- 模拟评论。
- 模拟商品切换。
- 模拟订单。
- 模拟平台警告。
- 模拟下播。

### API

```http
POST /api/v1/live-sessions/{session_id}/comments/mock
POST /api/v1/live-sessions/{session_id}/platform-events/mock
```

## 4. TaobaoLiveAdapter

### 优先能力

- 淘宝数字人评论推送。
- 淘宝直播订单消息。
- 淘宝直播上下播消息。
- 直播间商品信息查询。
- 直播间场次信息查询。
- 商品 ID 映射。

### 处理流程

```text
淘宝消息推送
  ↓
验签 / 鉴权
  ↓
raw payload 入库
  ↓
normalize_event
  ↓
PlatformEvent 发布到 stream:platform_events
  ↓
LiveControl 消费
```

### 事件映射

| 淘宝事件 | 标准事件 |
|---|---|
| 数字人评论推送 | CommentReceived |
| 直播订单消息 | OrderCreated |
| 直播上下播消息 | LiveStarted / LiveEnded |
| 商品池变化 | ProductChanged |

### 注意事项

- 必须处理授权状态。
- 必须处理重复推送。
- 必须建立平台商品 ID 与内部 product_id 的映射。
- 评论不能直接触发播报，必须进入中控和合规链路。

## 5. DouyinAdapter

### 优先能力

- 评论互动数据能力申请后的任务启动。
- 停止任务。
- 查询任务状态。
- 评论事件推送接收。
- 平台警告事件上报。
- 点赞、关注、礼物预留。

### 处理流程

```text
启动直播间数据推送任务
  ↓
抖音推送评论到开发者服务器
  ↓
验签 / 鉴权 / 去重
  ↓
转 PlatformEvent
  ↓
进入 CommentRouter
```

### 合规策略

- 低风险问题可配置自动审核通过。
- 中风险问题默认人审。
- 高风险问题默认拦截。
- 平台异常时暂停 AI 自动互动。
- 场控台必须保留一键人工接管。

## 6. XiaohongshuAdapter

### MVP 策略

小红书第一版建议做保守接入：

- 商品资料管理。
- 直播画面推流。
- 人工场控输入评论。
- 官方可用接口接入商品/订单能力。
- 不依赖非官方抓包作为生产链路。

### 默认规则

```json
{
  "auto_answer_enabled": false,
  "human_review_required": true,
  "ai_label_required": true,
  "platform_tone": "soft_seeding"
}
```

## 7. WeChatChannelsAdapter

### MVP 策略

视频号默认保守模式：

- 真人场控 + 数字人辅助。
- 不做全自动无人托管。
- 评论可人工录入或官方能力接入。
- 高风险问题全部人工处理。
- 平台异常立即暂停自动互动。

### 默认规则

```json
{
  "auto_answer_enabled": false,
  "human_review_required": true,
  "takeover_required": true,
  "fallback_video_enabled": true
}
```

## 8. TikTokAdapter

### 后续能力

- 英文 / 多语言评论接入。
- AI-generated content 标签配置。
- 多币种价格。
- 跨境物流 FAQ。
- 海外售后 FAQ。
- 多语言 TTS。
- 多时区直播排班。

### 默认规则

```json
{
  "ai_label_required": true,
  "language": "en-US",
  "currency_mode": "multi_currency",
  "human_review_required_for_policy_topics": true
}
```

## 9. ManualInputAdapter

当平台没有稳定开放接口，或账号权限未开通时，使用人工输入适配器。

功能：

- 场控手动复制评论。
- 手动选择商品。
- 手动触发候选回答。
- 保留同样的合规和播报链路。

ManualInputAdapter 仍然输出标准 `PlatformEvent`：

```json
{
  "platform": "manual",
  "event_type": "ManualCommentEntered",
  "content": "这款发什么快递？"
}
```

## 10. Adapter 测试要求

每个 Adapter 必须测试：

- raw payload 标准化。
- 必填字段缺失。
- 重复事件去重。
- 鉴权失败。
- 平台异常。
- 商品 ID 映射。
- 用户信息脱敏。



---

# 文件：`docs/10-ai-rag-llm.md`

# 10. 商品 RAG 与 LLM Gateway

## 1. 核心原则

LLM 不能直接回答商品事实。商品事实必须来自：

```text
PostgreSQL: 价格、库存、SKU、优惠、发货、售后等结构化信息
Qdrant: FAQ、卖点、使用方法、成分说明等语义知识
Redis: 高频缓存
```

LLM 只负责：

- 意图识别。
- 语言组织。
- 话术改写。
- 候选回答生成。
- 合规复核辅助。

## 2. RAG 数据分层

| 数据类型 | 存储 | 示例 |
|---|---|---|
| 商品标题 | PostgreSQL | 氨基酸洗面奶 |
| SKU | PostgreSQL | 100ml / 200ml |
| 价格 | PostgreSQL | 直播价 99 |
| 库存 | PostgreSQL | 200 件 |
| 优惠券 | PostgreSQL JSONB | 满 100 减 20 |
| FAQ | PostgreSQL + Qdrant | 敏感肌能用吗 |
| 卖点 | PostgreSQL + Qdrant | 温和清洁 |
| 禁止表达 | PostgreSQL | 保证不过敏 |
| 售后政策 | PostgreSQL + Qdrant | 7 天无理由 |

## 3. 商品问答流程

```text
用户评论
  ↓
CommentRouter 识别意图
  ↓
ProductResolver 定位商品
  ↓
StructuredFactService 查询价格/库存/优惠
  ↓
Retriever 检索 FAQ/卖点/政策
  ↓
LLMGateway 生成候选回答
  ↓
ComplianceService 审核
  ↓
HumanReviewService 或自动低风险通过
```

## 4. 意图分类

基础 intent：

```text
price_query              价格咨询
coupon_query             优惠券咨询
inventory_query          库存咨询
sku_query                规格咨询
shipping_query           发货咨询
after_sales_query        售后咨询
usage_query              使用方法
suitability_query        适用人群
safety_query             安全/过敏/孕妇/儿童
comparison_query         对比竞品
order_query              下单咨询
greeting                 打招呼
spam                     垃圾评论
unknown                  未知
```

## 5. LLMGateway 接口

```python
class LLMGateway:
    async def classify_comment(self, request: ClassifyCommentRequest) -> CommentIntent:
        ...

    async def generate_product_answer(self, request: ProductAnswerRequest) -> ProductAnswer:
        ...

    async def rewrite_for_platform(self, request: RewriteRequest) -> RewriteResult:
        ...

    async def compliance_review(self, request: ComplianceReviewRequest) -> ComplianceReviewResult:
        ...

    async def generate_script(self, request: ScriptGenerationRequest) -> ScriptResult:
        ...
```

## 6. ProductAnswerRequest

```json
{
  "platform": "taobao",
  "comment": "敏感肌能用吗？现在多少钱？",
  "intent": ["suitability_query", "price_query"],
  "product": {
    "id": "prod_001",
    "title": "氨基酸洁面乳",
    "category": "beauty"
  },
  "structured_facts": {
    "live_price": "99.00",
    "currency": "CNY",
    "coupon_info": "领券减20，具体以页面显示为准",
    "stock_status": "in_stock"
  },
  "retrieved_chunks": [
    {
      "source_type": "faq",
      "content": "敏感肌用户建议先做局部测试。"
    }
  ],
  "forbidden_claims": [
    "保证不过敏",
    "100%安全",
    "修复皮肤屏障"
  ],
  "style": "直播口播，简洁自然"
}
```

## 7. ProductAnswerResponse

```json
{
  "answer_text": "这款主打日常温和清洁，敏感肌用户建议先做局部测试。今天直播间价格以页面显示为准，可以先领券再下单。",
  "risk_level": "medium",
  "facts_used": ["live_price", "coupon_info", "faq:xxx"],
  "need_human_review": true
}
```

## 8. Prompt 约束

所有商品回答 Prompt 必须包含：

```text
你不能编造商品信息。
你只能使用提供的结构化事实和检索片段。
如果信息不足，回答“以商品详情页/客服说明为准”。
价格必须加“以页面显示为准”。
不能使用绝对化表达。
不能承诺治疗、治愈、保证效果。
不能引导私下交易。
不能攻击竞品。
输出必须适合直播口播。
```

## 9. Prompt 文件

```text
packages/prompt-templates/
├── comment_classify_v1.md
├── product_answer_v1.md
├── product_script_v1.md
├── compliance_review_v1.md
├── platform_rewrite_taobao_v1.md
├── platform_rewrite_douyin_v1.md
├── platform_rewrite_xhs_v1.md
├── platform_rewrite_wechat_channels_v1.md
└── platform_rewrite_tiktok_v1.md
```

## 10. 模型路由策略

| 任务 | 推荐策略 |
|---|---|
| 评论分类 | 快模型 / 小模型 / 本地模型 |
| 商品回答 | 中等模型 + RAG |
| 高风险审核 | 强模型 + 规则 |
| 长资料总结 | 长上下文模型 |
| 多语言 | 多语言模型 |
| 失败兜底 | 缓存回答 / 固定话术 |

## 11. 缓存策略

缓存 key：

```text
hash(platform + product_id + normalized_intent + normalized_question + fact_version)
```

缓存内容：

- 候选回答。
- 风险等级。
- facts_used。
- 过期时间。

价格/库存问题缓存时间必须短，建议不超过 60 秒或直接不缓存。

## 12. 必须记录的 LLM 日志

```text
request_id
merchant_id
live_session_id
provider
model_name
prompt_version
input_hash
latency_ms
token_usage
status
error_code
created_at
```

不得记录完整敏感个人信息。



---

# 文件：`docs/11-compliance.md`

# 11. 合规审核设计

## 1. 原则

合规模块是生产系统的核心，不是附加功能。

规则：

- 所有 AI 生成播报必须先过 ComplianceService。
- blocked 结果禁止播报。
- high 风险默认人工处理。
- medium 风险默认人工审核。
- low 风险是否自动通过必须按平台和类目配置。
- 平台警告时必须暂停自动互动。

## 2. 合规范围

```text
AI 标识
敏感词
绝对化用语
价格一致性
虚假宣传
功效宣称
医疗健康风险
食品安全风险
美妆功效风险
母婴儿童风险
金融风险
竞品攻击
私下交易
平台差异规则
音色授权
数字人形象授权
日志留存
```

## 3. ComplianceService 结构

```text
ComplianceService
├── SensitiveWordChecker
├── AbsoluteClaimChecker
├── PriceConsistencyChecker
├── MedicalClaimChecker
├── FoodSafetyChecker
├── CosmeticClaimChecker
├── FinanceRiskChecker
├── ChildProductChecker
├── CompetitorAttackChecker
├── PrivateTransactionChecker
├── PlatformRuleChecker
├── AILabelChecker
├── VoiceLicenseChecker
├── AvatarLicenseChecker
├── LLMComplianceReviewer
└── HumanReviewWorkflow
```

## 4. 审核输入

```json
{
  "merchant_id": "merchant_001",
  "platform": "douyin",
  "live_session_id": "session_001",
  "product_id": "prod_001",
  "category": "beauty",
  "text": "敏感肌一定能用，保证不过敏。",
  "source": "llm_answer",
  "facts_used": ["faq_001"],
  "context": {
    "comment": "敏感肌能用吗？",
    "intent": "suitability_query"
  }
}
```

## 5. 审核输出

```json
{
  "blocked": true,
  "risk_level": "high",
  "need_human_review": true,
  "reasons": [
    {
      "rule": "absolute_claim",
      "message": "命中绝对化表达：一定、保证"
    },
    {
      "rule": "cosmetic_claim",
      "message": "涉及敏感肌适用性，不能承诺不过敏"
    }
  ],
  "suggested_rewrite": "这款主打日常温和清洁，敏感肌用户建议先做局部测试。"
}
```

## 6. 风险分级

| 等级 | 示例 | 策略 |
|---|---|---|
| low | 多少钱、几件装、怎么领券 | 可配置自动通过 |
| medium | 敏感肌、孕妇、儿童、适用人群 | 默认人工审核 |
| high | 保证有效、治疗、治愈、不过敏 | 默认拦截或人工处理 |
| blocked | 私下交易、违法违规、绕平台付款 | 禁止播报 |
| platform_warning | 平台提示异常 | 暂停自动互动，人工接管 |

## 7. 绝对化用语规则

示例词：

```text
最
第一
顶级
永久
100%
绝对
保证
无副作用
完全没有风险
一定有效
根治
治愈
```

规则：

- 命中不一定直接 blocked，但至少 medium。
- 美妆、食品、保健、母婴、医疗相关类目命中后优先 high。

## 8. 价格一致性

LLM 输出价格时必须校验：

- 是否与 `product_price` 中当前平台价格一致。
- 是否在有效期内。
- 是否包含“以页面显示为准”之类兜底提示。
- 是否错误引用其他平台价格。

错误示例：

```text
今天一定只要 99 元。
```

推荐：

```text
今天直播间到手价以页面显示为准，可以先领券再下单。
```

## 9. AI 标识

系统必须支持：

```text
画面角标：AI数字人主播
直播间公告：本直播间使用 AI 数字人技术
定时口播：本直播间主播为 AI 数字人
素材元数据：AI 生成素材标记
日志留存：每句话来源、审核人、播报时间
```

后台配置：

```json
{
  "platform": "taobao",
  "ai_label_enabled": true,
  "screen_badge_text": "AI数字人主播",
  "voice_disclosure_interval_minutes": 20,
  "voice_disclosure_text": "本直播间主播为AI数字人。"
}
```

## 10. 平台差异策略

### 淘宝直播

- 商品事实优先。
- 评论、订单、上下播等事件要留痕。
- 价格、优惠、商品信息必须与平台一致。

### 抖音

- 默认强合规。
- 中高风险评论全部人工审核。
- 平台警告时立刻人工接管。
- AI 标识常驻。

### 小红书

- 默认保守口吻。
- 强种草弱销售。
- 不夸大功效。
- 默认人工审核。

### 视频号

- 默认保守模式。
- 不做全自动无人托管。
- 优先真人场控。

### TikTok

- 开启 AI-generated content 标签策略。
- 多语言合规规则。
- 禁止误导性深度伪造和虚假背书。

## 11. 人工审核工作流

```text
ComplianceService 输出 need_human_review=true
  ↓
创建 human_review_task
  ↓
场控台显示候选回答 + 风险原因
  ↓
审核员选择：通过 / 拒绝 / 改写 / 手动回答
  ↓
通过或改写后生成 speech_task
  ↓
写入 audit_log
```

## 12. 测试用例要求

至少提供：

- 价格低风险通过。
- 敏感肌 medium。
- 保证不过敏 high/blocked。
- 私下交易 blocked。
- 医疗治愈 blocked。
- 平台警告触发人工接管。
- 合规服务异常时默认不播报。
- 人工改写后可播报。
- AI 标识配置缺失时报警。



---

# 文件：`docs/12-tts-avatar-media.md`

# 12. TTS、数字人、媒体设计

## 1. 总体链路

```text
播报文本
  ↓
ComplianceService 审核
  ↓
HumanReviewService 通过
  ↓
TTSService 生成音频
  ↓
AvatarGateway 调用数字人
  ↓
LiveTalking 口型同步
  ↓
虚拟摄像头 / RTMP / WebRTC
  ↓
OBS / SRS
  ↓
平台直播伴侣 / 平台推流
```

## 2. TTSService

### Provider

```text
MockTTSProvider          本地测试
EdgeTTSProvider          Demo
CosyVoiceProvider        主力中文 / 多语言 TTS
GPTSoVITSProvider        音色克隆
AliyunTTSProvider        云厂商兜底
TencentTTSProvider       云厂商兜底
FallbackTTSProvider      失败兜底
```

### 接口

```python
class TTSService:
    async def generate(self, request: TTSGenerateRequest) -> TTSResult: ...
    async def precache(self, request: TTSPCacheRequest) -> list[TTSResult]: ...
    async def list_voices(self, merchant_id: str) -> list[VoiceProfile]: ...
    async def clone_voice(self, request: VoiceCloneRequest) -> VoiceProfile: ...
    async def validate_voice_license(self, voice_id: str) -> bool: ...
```

### 缓存策略

```text
缓存 key = hash(text + voice_id + speed + emotion + platform + language)
```

适合预生成：

- 欢迎语。
- 商品卖点。
- 催单话术。
- FAQ 答案。
- 冷场话术。
- AI 身份提示。

实时生成：

- 观众个性化问题。
- 人工输入回答。

### 音色授权

音色必须有授权记录：

```text
voice_id
owner_name
source_file_url
consent_document_url
allowed_platforms
commercial_allowed
valid_from
valid_to
status
```

无授权或授权过期不能上线。

## 3. AvatarGateway

### 目标

主业务不能直接调用 LiveTalking。必须通过 AvatarGateway 隔离。

### 接口

```python
class AvatarGateway:
    async def speak_text(self, request: SpeakTextRequest) -> AvatarCommandResult: ...
    async def speak_audio(self, request: SpeakAudioRequest) -> AvatarCommandResult: ...
    async def interrupt(self, session_id: str) -> None: ...
    async def idle(self, session_id: str) -> None: ...
    async def switch_avatar(self, session_id: str, avatar_id: str) -> None: ...
    async def switch_scene(self, session_id: str, scene_id: str) -> None: ...
    async def get_stream_url(self, session_id: str) -> StreamInfo: ...
    async def health_check(self) -> AvatarHealth: ...
```

### Provider

```text
MockAvatarProvider
LiveTalkingProvider
FallbackVideoProvider
```

### SpeakAudioRequest

```json
{
  "session_id": "session_001",
  "avatar_id": "avatar_001",
  "speech_task_id": "speech_001",
  "audio_url": "s3://bucket/audio/xxx.wav",
  "text": "这款今天直播间有优惠。",
  "interrupt_current": false,
  "metadata": {
    "source": "approved_answer"
  }
}
```

## 4. LiveTalking 接入

### MVP 模式

```text
TTS 生成完整音频文件
  ↓
AvatarGateway 调用 LiveTalking 播放音频
  ↓
LiveTalking 输出虚拟摄像头 / RTMP
  ↓
OBS 采集
```

### 生产优化

```text
分句 TTS
分句播报
高频语音缓存
讲品脚本预生成
待机动作视频
异常备用视频
```

### 打断策略

触发打断：

- 人工接管。
- 平台警告。
- 高优先级评论。
- 直播异常。
- 场控手动打断。

打断流程：

```text
SpeechQueueService 标记当前 speech_task interrupted
  ↓
AvatarGateway.interrupt
  ↓
LiveTalking 停止当前播报
  ↓
状态机返回 EXPLAINING_PRODUCT 或 HUMAN_TAKEOVER
```

## 5. MediaService

### 职责

- SRS 预览地址。
- RTMP/WebRTC 健康状态。
- 录制开始/停止。
- 推流中断告警。
- 备用视频状态。

### MVP 推流链路

```text
LiveTalking
  ↓
虚拟摄像头 / RTMP
  ↓
OBS
  ↓
平台直播伴侣 / 平台推流地址
```

### 内部预览链路

```text
LiveTalking RTMP
  ↓
SRS
  ↓
WebRTC / HTTP-FLV
  ↓
场控台预览
```

## 6. 异常处理

| 异常 | 处理 |
|---|---|
| TTS 超时 | 切备用 Provider 或使用缓存语音 |
| 音色无授权 | 拒绝生成并提示运营 |
| LiveTalking 无响应 | 切 fallback video |
| RTMP 中断 | 告警并暂停自动播报 |
| OBS 未连接 | 场控台提示，不阻塞业务测试 |
| 音频文件丢失 | speech_task 标记 failed |

## 7. 测试要求

- MockTTS 生成假音频 URL。
- TTS 缓存命中。
- 音色授权失败。
- MockAvatar speak_audio 成功。
- Avatar interrupt 成功。
- LiveTalkingProvider 连接失败降级。
- MediaService 返回 SRS preview URL。



---

# 文件：`docs/13-frontend.md`

# 13. 前端后台设计

## 1. 前端应用拆分

```text
admin-web      商家 / 运营后台
control-web    直播场控台
monitor-web    系统监控台，可后置
```

MVP 可以先做：

- admin-web：商品、直播间、数字人基础配置。
- control-web：评论、审核、播报、人工接管。

## 2. 技术栈

```text
Vue 3
TypeScript
Vite
Element Plus
Pinia
Vue Router
Axios
WebSocket
ECharts
```

## 3. admin-web 菜单

```text
首页概览
商家管理
店铺管理
平台账号
商品管理
  ├── 商品列表
  ├── SKU 管理
  ├── 价格 / 库存
  ├── FAQ
  ├── 卖点
  ├── 售后政策
  ├── 禁用话术
  └── 平台差异话术
直播管理
  ├── 直播间
  ├── 直播场次
  ├── 直播排班
  └── 商品池
AI 能力
  ├── 模型配置
  ├── Prompt 模板
  ├── TTS 配置
  └── 音色管理
数字人资产
  ├── 数字人形象
  ├── 待机视频
  ├── 备用视频
  └── 场景模板
合规风控
  ├── 敏感词
  ├── 类目规则
  ├── 平台规则
  ├── AI 标识配置
  └── 审核记录
数据看板
系统设置
```

## 4. control-web 场控台布局

```text
┌────────────────────┬────────────────────────┬───────────────────────┐
│ 左侧：直播状态       │ 中间：评论/任务队列       │ 右侧：回答/审核/接管     │
│ - 平台              │ - 评论列表              │ - AI 候选回答           │
│ - 当前状态          │ - 用户昵称              │ - 合规风险              │
│ - 当前商品          │ - 评论内容              │ - 命中规则              │
│ - 数字人预览        │ - 意图标签              │ - 编辑框                │
│ - 推流状态          │ - 优先级                │ - 通过/拒绝/改写         │
│ - 快捷操作          │ - 待审核/已处理          │ - 人工接管              │
└────────────────────┴────────────────────────┴───────────────────────┘
```

## 5. 场控台必须支持

- 查看直播状态。
- 查看当前平台。
- 查看当前商品。
- 查看数字人预览。
- 查看推流状态。
- 查看评论队列。
- 查看 AI 候选回答。
- 查看合规风险和命中原因。
- 编辑回答后通过。
- 拒绝回答。
- 手动输入回答。
- 一键人工接管。
- 一键停止接管。
- 一键静音。
- 一键打断。
- 一键切备用视频。
- 查看播报历史。
- 查看审核历史。
- 查看平台警告。

## 6. WebSocket 事件

连接：

```text
/ws/live-sessions/{session_id}
```

事件类型：

```text
state_changed
comment_received
answer_generated
compliance_checked
review_task_created
review_task_updated
speech_started
speech_finished
avatar_error
platform_warning
stream_health_changed
human_takeover_started
human_takeover_ended
```

前端收到事件后必须更新对应 Pinia store。

## 7. 前端状态管理

Pinia stores：

```text
useAuthStore
useMerchantStore
useProductStore
useLiveSessionStore
useCommentStore
useReviewStore
useSpeechStore
useAvatarStore
useMediaStore
useComplianceStore
```

## 8. 页面 MVP

### 商品列表页

- 商品列表。
- 新建商品。
- 编辑商品。
- FAQ 管理入口。
- 索引状态。

### 商品详情页

- 基础信息。
- SKU。
- 价格。
- FAQ。
- 卖点。
- 禁用表达。
- 平台差异话术。

### 直播场次页

- 创建直播场次。
- 选择直播间。
- 选择商品池。
- 选择数字人。
- 选择音色。
- 启动 Mock 直播。

### 场控台

- 评论模拟输入。
- 评论队列。
- 生成候选回答。
- 审核通过/拒绝/改写。
- 播报任务状态。
- 人工接管。

## 9. 前端权限

| 功能 | 运营 | 场控 | 审核 | 管理员 |
|---|---|---|---|---|
| 商品编辑 | 是 | 否 | 否 | 是 |
| 直播启动 | 是 | 是 | 否 | 是 |
| 审核通过 | 否 | 是 | 是 | 是 |
| 合规规则编辑 | 否 | 否 | 是 | 是 |
| 平台账号配置 | 否 | 否 | 否 | 是 |
| 人工接管 | 否 | 是 | 否 | 是 |

## 10. E2E 前端验收

- 能登录。
- 能创建商品。
- 能添加 FAQ。
- 能创建直播场次。
- 能启动 Mock 直播。
- 能模拟评论。
- 能看到候选回答。
- 能通过审核。
- 能看到播报完成状态。
- 能打开人工接管并恢复。



---

# 文件：`docs/14-testing-strategy.md`

# 14. 测试策略

## 1. 测试目标

系统必须可持续迭代。第一版就要建立测试体系。

核心目标：

- Mock 全链路可自动测试。
- 状态机合法性可测试。
- 合规规则可测试。
- Provider 替换不影响业务测试。
- 不依赖真实平台凭证。

## 2. 测试分层

```text
Unit Tests          单元测试
Integration Tests   集成测试
E2E Tests           端到端测试
Contract Tests      Adapter / Provider 契约测试
Manual QA           真实平台灰度测试
```

## 3. 单元测试范围

必须覆盖：

```text
LiveSession 状态机
PlatformEvent normalize_event
CommentRouter 去重 / 限流 / 分类
ProductResolver 商品绑定
RAG Retriever 检索
LLMGateway MockProvider
Compliance Rules
HumanReviewService
TTS Cache
AvatarGateway MockProvider
SpeechQueueService
TakeoverService
```

## 4. 集成测试

### 4.1 评论问答链路

```text
Mock 评论
  ↓
CommentRouter
  ↓
ProductRAG
  ↓
LLMGateway Mock
  ↓
ComplianceService
  ↓
HumanReviewService
  ↓
SpeechQueueService
```

### 4.2 商品索引链路

```text
商品 FAQ 创建
  ↓
knowledge_chunk 创建
  ↓
Qdrant upsert
  ↓
检索命中
```

### 4.3 人工接管链路

```text
直播中
  ↓
start_takeover
  ↓
暂停 AI 队列
  ↓
interrupt avatar
  ↓
manual_speak
  ↓
release_takeover
  ↓
恢复 EXPLAINING_PRODUCT
```

## 5. 第一条 E2E 测试

测试名称：`test_mock_comment_to_avatar_speech_flow`

步骤：

1. 创建商家。
2. 创建商品。
3. 创建 SKU。
4. 创建价格。
5. 创建 FAQ。
6. 创建直播间。
7. 创建直播场次。
8. 启动直播。
9. 模拟评论：`这款多少钱？`
10. 系统创建 comment_task。
11. 生成 answer_candidate。
12. 通过 compliance_result。
13. 创建 human_review_task。
14. 人工审核通过。
15. 创建 speech_task。
16. MockTTS 生成音频 URL。
17. MockAvatar 完成播报。
18. 查询日志完整。

断言：

- `comment_task.status == spoken`
- `answer_candidate.status == approved`
- `speech_task.status == finished`
- `live_state_log` 至少包含 start、review、speak。
- `avatar_command_log.status == success`

## 6. 合规测试用例

| 输入 | 预期 |
|---|---|
| 这款多少钱 | low |
| 敏感肌可以用吗 | medium + need_human_review |
| 保证不过敏 | high 或 blocked |
| 100% 有效 | high |
| 可以私下转账 | blocked |
| 能治好湿疹 | blocked |
| 今天以页面价格为准 | low |

## 7. Mock Provider 要求

### MockPlatformAdapter

- 可产生评论。
- 可产生订单。
- 可产生上下播。
- 可产生平台警告。

### MockLLMProvider

- 根据 intent 返回稳定文本。
- 支持模拟超时。
- 支持模拟错误。

### MockTTSProvider

- 返回假 audio_url。
- 返回 duration_ms。
- 支持模拟失败。

### MockAvatarProvider

- 接收 speak_audio。
- 标记 command success。
- 支持 interrupt。
- 支持模拟失败。

## 8. 压测目标

MVP：

- 单直播间每分钟 100 条评论进入不崩溃。
- 评论入队延迟 < 300ms。
- Mock 生成回答 < 1s。
- 场控台 WebSocket 稳定。

生产初期：

- 单直播间每分钟 500 条评论。
- 高频问题缓存命中。
- 低风险问题自动处理可配置。
- 人审队列不丢数据。

## 9. CI 要求

每个 PR 必须运行：

```bash
make lint
make test
make typecheck
```

核心分支额外运行：

```bash
make e2e
```



---

# 文件：`docs/15-deployment-ops.md`

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



---

# 文件：`docs/16-security-privacy.md`

# 16. 安全与隐私

## 1. 安全原则

- 最小权限。
- 密钥不进代码库。
- 用户信息最小化。
- 日志脱敏。
- 外部平台调用可审计。
- AI 生成内容可追溯。
- 音色和形象授权可证明。

## 2. 密钥管理

禁止提交：

- 平台 App Key。
- 平台 App Secret。
- access_token。
- refresh_token。
- LLM API Key。
- TTS API Key。
- MinIO/OSS/COS Secret。
- JWT Secret。

开发环境使用 `.env`，仓库只提交 `.env.example`。

生产环境使用 Secret Manager 或环境变量注入。

## 3. 日志脱敏

必须脱敏：

- 平台 token。
- API key。
- 手机号。
- 身份证。
- 地址。
- 用户平台 ID。

建议：

```text
platform_user_id → hash 后保存
手机号 → 138****0000
token → tok_****abcd
```

## 4. 用户数据

评论内容属于业务数据，但仍需控制访问：

- 只有对应商家可看。
- 平台用户 ID 尽量 hash。
- raw payload 可配置是否保存。
- 支持按时间清理。

## 5. 音色授权

语音克隆必须有授权记录。

字段：

```text
授权人
来源文件
授权文件
授权平台
是否商用
有效期
审核状态
```

无授权不能在生产直播使用。

## 6. 数字人形象授权

数字人形象必须有：

- 形象来源。
- 肖像授权或资产授权。
- 商用许可。
- 可用平台。
- 有效期。

## 7. AI 内容标识

系统必须支持：

- 画面角标。
- 定时口播。
- 直播间公告。
- 素材元数据标识。
- 播报日志。

## 8. 平台合规边界

禁止实现：

- 非官方抓包。
- 规避平台审核。
- 模拟真人绕过风控。
- 自动私信诱导绕平台交易。
- 删除或隐藏 AI 标识。
- 未授权声音克隆。
- 未授权真人形象复刻。

当平台未开放 API 时，使用：

- ManualInputAdapter。
- MockPlatformAdapter。
- 官方直播伴侣采集方案。

## 9. 权限设计

权限粒度：

```text
merchant:read/write
shop:read/write
platform_account:read/write
product:read/write
live_session:read/write/control
review:read/approve/reject
compliance:read/write
voice:read/write/approve
avatar:read/write/approve
system:admin
```

## 10. 审计日志

必须记录：

- 登录。
- 平台账号变更。
- 商品价格变更。
- 合规规则变更。
- Prompt 模板变更。
- 审核通过/拒绝/改写。
- 人工接管。
- 音色授权变更。
- 数字人资产变更。



---

# 文件：`docs/17-milestones.md`

# 17. 开发里程碑

## 阶段 0：工程骨架

### 目标

建立可持续开发的仓库、后端、前端、基础设施和测试框架。

### 交付物

```text
monorepo 初始化
FastAPI 后端骨架
Vue3 admin-web/control-web 骨架
PostgreSQL / Redis / Qdrant / MinIO / SRS docker-compose
统一配置管理
统一日志
统一错误码
基础鉴权
Alembic 迁移框架
AGENTS.md
README
Makefile
基础 CI
```

### 验收

```text
make up 可启动依赖
/api/v1/healthz 正常
前端可访问
make migrate 可执行
make test 可运行
```

## 阶段 1：商品库 + Mock 全链路

### 目标

不接真实平台和真实数字人，先跑通业务主链路。

### 交付物

```text
Merchant / Product / SKU / FAQ / SellingPoint CRUD
Qdrant 知识库索引
MockPlatformAdapter
评论模拟器
CommentRouter
LiveSession 状态机
LLMGateway MockProvider
ComplianceService 基础规则
HumanReviewService
TTS MockProvider
Avatar MockProvider
场控台基础版
E2E: mock comment to avatar speech
```

### 验收

```text
创建商品和 FAQ
启动 Mock 直播
模拟评论“这款多少钱”
生成候选回答
合规审核
人工通过
Mock 播报完成
全链路日志可查
```

## 阶段 2：真实 TTS + AvatarGateway + LiveTalking

### 目标

让数字人真实播报。

### 交付物

```text
TTSService EdgeTTSProvider
CosyVoiceProvider 预留
GPTSoVITSProvider 预留
语音缓存
VoiceProfile / VoiceLicense
AvatarGateway
LiveTalkingProvider
打断能力
待机视频
fallback 视频
SRS 预览
OBS 操作文档
```

### 验收

```text
场控台审核通过后生成真实音频
AvatarGateway 调用 LiveTalking
数字人口型播报
SRS 可预览
OBS 可采集
```

## 阶段 3：淘宝直播 Adapter

### 目标

优先跑通最适合电商闭环的平台接入。

### 交付物

```text
TaobaoLiveAdapter
淘宝评论事件接收
淘宝上下播事件接收
淘宝订单事件接收
直播间商品查询
商品 ID 映射
淘宝平台合规规则
```

### 验收

```text
淘宝评论进入系统
绑定当前商品
生成候选回答
合规审核
人工通过
数字人播报
订单事件入库
```

## 阶段 4：抖音 Adapter

### 目标

接入抖音直播评论互动能力，强化合规和人工接管。

### 交付物

```text
DouyinAdapter
评论任务启动/停止/查询状态
评论事件接收
平台警告事件
抖音平台规则
高风险默认人审
一键人工接管
```

### 验收

```text
抖音评论进入系统
低风险候选回答
中高风险强制人审
平台警告触发暂停 AI 自动互动
```

## 阶段 5：合规系统强化

### 目标

使系统具备商业运营的基本合规能力。

### 交付物

```text
敏感词库
绝对化用语库
类目规则
平台规则
价格一致性校验
功效宣称检测
AI 标识配置
人工审核流强化
审核日志
合规看板
```

### 验收

```text
所有播报前经过 ComplianceService
高风险不会自动播报
blocked 必须禁止播报
AI 标识常驻
审核可追溯
```

## 阶段 6：小红书 / 视频号保守接入

### 目标

先可播、可控，不追求全自动。

### 交付物

```text
XiaohongshuAdapter 基础版
WeChatChannelsAdapter 基础版
ManualInputAdapter 强化
保守模式配置
平台差异口吻
```

### 验收

```text
可通过人工输入评论触发同样的审核和播报链路
保守模式默认禁止自动回答
```

## 阶段 7：TikTok 国际化

### 目标

扩展海外直播能力。

### 交付物

```text
TikTokAdapter
英文 / 多语言知识库
多语言 Prompt
英文 TTS
多币种价格话术
跨境物流 FAQ
海外售后 FAQ
AIGC 标签配置
```

## 阶段 8：规模化运营

### 目标

从单直播间扩展到多直播间、多账号、多商家。

### 交付物

```text
多商家权限
多直播间并发
排班系统
多数字人形象
多音色
数据看板
成本统计
模型调用监控
直播质量监控
异常告警
```



---

# 文件：`docs/18-codex-issues.md`

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



---

# 文件：`docs/19-acceptance-checklists.md`

# 19. 验收清单

## 1. 阶段 0 验收

- [ ] 仓库结构符合 docs/03-repo-structure.md。
- [ ] `AGENTS.md` 存在。
- [ ] `.env.example` 存在且不包含真实密钥。
- [ ] `make up` 可启动 Postgres/Redis/Qdrant/MinIO/SRS。
- [ ] `make migrate` 可执行。
- [ ] `/api/v1/healthz` 返回正常。
- [ ] admin-web 可启动。
- [ ] control-web 可启动。
- [ ] `make test` 可运行。

## 2. 阶段 1 验收

- [ ] 可创建商家。
- [ ] 可创建商品。
- [ ] 可创建 SKU。
- [ ] 可创建价格。
- [ ] 可创建 FAQ。
- [ ] 可创建商品卖点。
- [ ] 可执行商品知识库索引。
- [ ] MockPlatformAdapter 可模拟评论。
- [ ] CommentRouter 可创建 comment_task。
- [ ] LLMGateway Mock 可生成候选回答。
- [ ] ComplianceService 可输出风险等级。
- [ ] HumanReviewService 可审核通过/拒绝/改写。
- [ ] TTSService Mock 可生成假音频。
- [ ] AvatarGateway Mock 可完成播报。
- [ ] 场控台可完成评论到播报链路。
- [ ] E2E 测试通过。

## 3. 阶段 2 验收

- [ ] 音色管理可用。
- [ ] 音色授权校验可用。
- [ ] TTS 真实 Provider 至少一个可用。
- [ ] AvatarGateway 能调用 LiveTalkingProvider。
- [ ] 可完成真实数字人播报。
- [ ] 可打断当前播报。
- [ ] 可切换待机 / fallback。
- [ ] SRS 可返回预览地址。
- [ ] OBS 可采集画面或 RTMP。

## 4. 淘宝 Adapter 验收

- [ ] 平台账号配置可保存。
- [ ] 淘宝 raw event 可入库。
- [ ] 淘宝评论可转 PlatformEvent。
- [ ] 淘宝上下播可转 PlatformEvent。
- [ ] 淘宝订单可转 PlatformEvent。
- [ ] 商品 ID 映射可用。
- [ ] 淘宝评论可进入问答链路。
- [ ] 淘宝订单可记录。

## 5. 抖音 Adapter 验收

- [ ] 平台账号配置可保存。
- [ ] 互动数据任务启动/停止/查询状态封装完成。
- [ ] 抖音评论可转 PlatformEvent。
- [ ] 平台警告可进入系统告警。
- [ ] 中高风险默认人审。
- [ ] 平台警告触发暂停自动互动。

## 6. 合规验收

- [ ] 每条 AI 播报有 compliance_result。
- [ ] blocked 不会创建 speech_task。
- [ ] high 不会自动播报。
- [ ] medium 默认进入人审。
- [ ] 价格回答经过价格一致性校验。
- [ ] AI 标识配置可用。
- [ ] 直播间角标配置可用。
- [ ] 定时 AI 身份提示可用。
- [ ] 所有审核操作写 audit_log。

## 7. 业务验收

- [ ] 数字人可连续讲解商品。
- [ ] 观众提问可进入场控台。
- [ ] AI 能生成候选回答。
- [ ] 人工可编辑后播报。
- [ ] 价格不胡编。
- [ ] 卖点不胡编。
- [ ] 敏感问题能拦截。
- [ ] 人工接管可用。
- [ ] 下播后可导出日志。

## 8. 安全验收

- [ ] 仓库无密钥。
- [ ] 日志脱敏。
- [ ] 平台 token 不明文输出。
- [ ] 音色有授权记录。
- [ ] 数字人形象有授权记录。
- [ ] 文件上传限制类型和大小。
- [ ] 权限控制可用。

## 9. 上线前人工检查

- [ ] 平台规则已由运营/法务确认。
- [ ] 直播间 AI 标识已配置。
- [ ] 商品话术已审核。
- [ ] 音色授权已确认。
- [ ] 数字人形象授权已确认。
- [ ] 人工接管人员在岗。
- [ ] 平台账号状态正常。
- [ ] OBS/SRS 推流测试通过。
- [ ] 应急预案确认。



---

# 文件：`docs/20-reference-sources.md`

# 20. 参考来源

本文件用于给开发与合规团队核对外部依赖与平台信息。实际开发时，平台规则和接口权限可能变化，接入前必须重新核对官方文档。

## OpenAI Codex

- Codex CLI: https://developers.openai.com/codex/cli
- Codex Cloud/Web: https://developers.openai.com/codex/cloud
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Codex GitHub Review: https://developers.openai.com/codex/integrations/github
- Codex best practices: https://developers.openai.com/codex/learn/best-practices

## 数字人、媒体、向量库

- LiveTalking: https://github.com/lipku/livetalking
- OBS: https://obsproject.com/
- SRS: https://github.com/ossrs/srs
- Qdrant: https://github.com/qdrant/qdrant

## 平台接口

- 淘宝直播 API: https://developer.alibaba.com/docs/topic_list.htm?cid=248
- 淘宝直播间商品/场次 API: https://open.fliggy.com/docs/api.htm?apiId=31582
- 抖音直播间评论互动数据: https://developer.open-douyin.com/docs/resource/zh-CN/interaction/jierushuoming/hudongshuju/pinglunshuju
- 小红书开放平台应用类目: https://xiaohongshu.apifox.cn/
- TikTok AI-generated content: https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content

## 合规

- 人工智能生成合成内容标识办法: https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm



---

# 文件：`docs/prompts/codex-initial-prompt.md`

# Codex 初始启动 Prompt

请在 Codex 中打开一个全新的 Git 仓库，然后粘贴以下 Prompt。

---

你现在是本项目的主开发 Agent。请先阅读以下文件，不要马上写代码：

- `README.md`
- `AGENTS.md`
- `docs/00-codex-handoff.md`
- `docs/01-prd.md`
- `docs/02-architecture.md`
- `docs/03-repo-structure.md`
- `docs/04-module-boundaries.md`
- `docs/06-live-state-machine.md`
- `docs/18-codex-issues.md`

阅读后请输出：

1. 你理解的系统目标。
2. 你理解的模块边界。
3. 第一阶段开发顺序。
4. 你将先实现的第一个 Issue。
5. 需要创建的文件清单。

然后从 `Issue 001：初始化 monorepo 与基础文档` 开始实现。

开发要求：

- 严格遵守 `AGENTS.md`。
- 不要一次性开发完整系统。
- 每次只完成当前 Issue。
- 不要接真实平台 API。
- 不要提交任何密钥。
- 所有外部能力先使用 Mock Provider。
- 每个模块必须有测试。
- 公共 API、事件、状态机变化必须同步更新文档。

完成后请给出：

- 修改文件列表。
- 如何运行。
- 如何测试。
- 当前未完成事项。



---

# 文件：`docs/prompts/phase-0-prompt.md`

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



---

# 文件：`docs/prompts/phase-1-prompt.md`

# Phase 1 Prompt：商品库 + Mock 主链路

请按 `docs/18-codex-issues.md` 的 Issue 006 到 Issue 020 实现 Mock 主链路。

要求：

- 使用 MockPlatformAdapter。
- 使用 MockLLMProvider。
- 使用 MockTTSProvider。
- 使用 MockAvatarProvider。
- 不接真实平台。
- 不接真实 LiveTalking。
- 跑通第一条 E2E：Mock 评论到数字人播报。

E2E 链路：

```text
创建商品 → 创建 FAQ → 启动 Mock 直播 → 模拟评论 → 候选回答 → 合规审核 → 人工通过 → MockTTS → MockAvatar → 日志完整
```



---

# 文件：`docs/prompts/phase-2-prompt.md`

# Phase 2 Prompt：真实 TTS + LiveTalking Gateway

请在 Mock 主链路已经通过的前提下，实现真实 TTS 和 AvatarGateway 扩展。

要求：

1. 增加 VoiceProfile 与 VoiceLicense。
2. 实现一个真实 TTS Provider 或可运行占位 Provider。
3. 实现 LiveTalkingProvider，但保留 MockAvatarProvider。
4. AvatarGateway 支持 provider 配置切换。
5. 支持 speak_audio、interrupt、idle、health_check。
6. 添加 SRS 预览 URL 逻辑。
7. 不破坏 Phase 1 的 Mock E2E 测试。



---

# 文件：`docs/prompts/phase-3-taobao-prompt.md`

# Phase 3 Prompt：淘宝直播 Adapter

请实现 TaobaoLiveAdapter 的基础框架和契约测试。

要求：

1. 不需要真实密钥。
2. 不需要在测试中调用淘宝真实接口。
3. 实现配置模型。
4. 实现 raw event 入库。
5. 实现评论事件 normalize_event。
6. 实现上下播事件 normalize_event。
7. 实现订单事件 normalize_event。
8. 实现商品 ID 映射。
9. 所有测试使用 fixture payload。
10. 输出标准 PlatformEvent。



---

# 文件：`docs/prompts/phase-4-douyin-prompt.md`

# Phase 4 Prompt：抖音 Adapter

请实现 DouyinAdapter 的基础框架和契约测试。

要求：

1. 不需要真实密钥。
2. 不在测试中请求真实抖音接口。
3. 实现互动数据任务启动/停止/查询状态的客户端接口封装，可使用 mock HTTP。
4. 实现评论事件 normalize_event。
5. 实现平台警告事件。
6. 接入平台规则：中高风险默认人审，平台警告触发暂停自动互动。

