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
