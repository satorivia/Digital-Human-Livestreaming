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
