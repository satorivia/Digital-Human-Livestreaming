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
