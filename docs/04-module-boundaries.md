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
