# comment_classify_v1

请将直播间评论分类为以下 intent 之一或多个：

- price_query
- coupon_query
- inventory_query
- sku_query
- shipping_query
- after_sales_query
- usage_query
- suitability_query
- safety_query
- comparison_query
- order_query
- greeting
- spam
- unknown

评论：{{ comment }}
当前商品：{{ product_title }}
平台：{{ platform }}

输出 JSON：

{
  "intents": [],
  "is_product_related": true/false,
  "priority": 0,
  "risk_hint": "low|medium|high"
}
