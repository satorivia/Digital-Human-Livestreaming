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
