# 10. 商品 RAG 与 LLM Gateway

## 1. 核心原则

LLM 不能直接回答商品事实。商品事实必须来自：

```text
PostgreSQL: 价格、库存、SKU、优惠、发货、售后等结构化信息
Qdrant: FAQ、卖点、使用方法、成分说明等语义知识
Redis: 高频缓存
```

LLM 只负责：

- 意图识别。
- 语言组织。
- 话术改写。
- 候选回答生成。
- 合规复核辅助。

## 2. RAG 数据分层

| 数据类型 | 存储 | 示例 |
|---|---|---|
| 商品标题 | PostgreSQL | 氨基酸洗面奶 |
| SKU | PostgreSQL | 100ml / 200ml |
| 价格 | PostgreSQL | 直播价 99 |
| 库存 | PostgreSQL | 200 件 |
| 优惠券 | PostgreSQL JSONB | 满 100 减 20 |
| FAQ | PostgreSQL + Qdrant | 敏感肌能用吗 |
| 卖点 | PostgreSQL + Qdrant | 温和清洁 |
| 禁止表达 | PostgreSQL | 保证不过敏 |
| 售后政策 | PostgreSQL + Qdrant | 7 天无理由 |

## 3. 商品问答流程

```text
用户评论
  ↓
CommentRouter 识别意图
  ↓
ProductResolver 定位商品
  ↓
StructuredFactService 查询价格/库存/优惠
  ↓
Retriever 检索 FAQ/卖点/政策
  ↓
LLMGateway 生成候选回答
  ↓
ComplianceService 审核
  ↓
HumanReviewService 或自动低风险通过
```

## 4. 意图分类

基础 intent：

```text
price_query              价格咨询
coupon_query             优惠券咨询
inventory_query          库存咨询
sku_query                规格咨询
shipping_query           发货咨询
after_sales_query        售后咨询
usage_query              使用方法
suitability_query        适用人群
safety_query             安全/过敏/孕妇/儿童
comparison_query         对比竞品
order_query              下单咨询
greeting                 打招呼
spam                     垃圾评论
unknown                  未知
```

## 5. LLMGateway 接口

```python
class LLMGateway:
    async def classify_comment(self, request: ClassifyCommentRequest) -> CommentIntent:
        ...

    async def generate_product_answer(self, request: ProductAnswerRequest) -> ProductAnswer:
        ...

    async def rewrite_for_platform(self, request: RewriteRequest) -> RewriteResult:
        ...

    async def compliance_review(self, request: ComplianceReviewRequest) -> ComplianceReviewResult:
        ...

    async def generate_script(self, request: ScriptGenerationRequest) -> ScriptResult:
        ...
```

## 6. ProductAnswerRequest

```json
{
  "platform": "taobao",
  "comment": "敏感肌能用吗？现在多少钱？",
  "intent": ["suitability_query", "price_query"],
  "product": {
    "id": "prod_001",
    "title": "氨基酸洁面乳",
    "category": "beauty"
  },
  "structured_facts": {
    "live_price": "99.00",
    "currency": "CNY",
    "coupon_info": "领券减20，具体以页面显示为准",
    "stock_status": "in_stock"
  },
  "retrieved_chunks": [
    {
      "source_type": "faq",
      "content": "敏感肌用户建议先做局部测试。"
    }
  ],
  "forbidden_claims": [
    "保证不过敏",
    "100%安全",
    "修复皮肤屏障"
  ],
  "style": "直播口播，简洁自然"
}
```

## 7. ProductAnswerResponse

```json
{
  "answer_text": "这款主打日常温和清洁，敏感肌用户建议先做局部测试。今天直播间价格以页面显示为准，可以先领券再下单。",
  "risk_level": "medium",
  "facts_used": ["live_price", "coupon_info", "faq:xxx"],
  "need_human_review": true
}
```

## 8. Prompt 约束

所有商品回答 Prompt 必须包含：

```text
你不能编造商品信息。
你只能使用提供的结构化事实和检索片段。
如果信息不足，回答“以商品详情页/客服说明为准”。
价格必须加“以页面显示为准”。
不能使用绝对化表达。
不能承诺治疗、治愈、保证效果。
不能引导私下交易。
不能攻击竞品。
输出必须适合直播口播。
```

## 9. Prompt 文件

```text
packages/prompt-templates/
├── comment_classify_v1.md
├── product_answer_v1.md
├── product_script_v1.md
├── compliance_review_v1.md
├── platform_rewrite_taobao_v1.md
├── platform_rewrite_douyin_v1.md
├── platform_rewrite_xhs_v1.md
├── platform_rewrite_wechat_channels_v1.md
└── platform_rewrite_tiktok_v1.md
```

## 10. 模型路由策略

| 任务 | 推荐策略 |
|---|---|
| 评论分类 | 快模型 / 小模型 / 本地模型 |
| 商品回答 | 中等模型 + RAG |
| 高风险审核 | 强模型 + 规则 |
| 长资料总结 | 长上下文模型 |
| 多语言 | 多语言模型 |
| 失败兜底 | 缓存回答 / 固定话术 |

## 11. 缓存策略

缓存 key：

```text
hash(platform + product_id + normalized_intent + normalized_question + fact_version)
```

缓存内容：

- 候选回答。
- 风险等级。
- facts_used。
- 过期时间。

价格/库存问题缓存时间必须短，建议不超过 60 秒或直接不缓存。

## 12. 必须记录的 LLM 日志

```text
request_id
merchant_id
live_session_id
provider
model_name
prompt_version
input_hash
latency_ms
token_usage
status
error_code
created_at
```

不得记录完整敏感个人信息。
