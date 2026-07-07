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
