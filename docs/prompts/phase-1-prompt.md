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
