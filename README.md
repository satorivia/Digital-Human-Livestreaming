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
