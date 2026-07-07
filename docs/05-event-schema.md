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
