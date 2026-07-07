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
