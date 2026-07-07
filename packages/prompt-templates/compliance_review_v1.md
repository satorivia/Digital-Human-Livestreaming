# compliance_review_v1

请审查以下直播口播文本是否存在合规风险。

审查维度：

- 敏感词
- 绝对化用语
- 价格不一致
- 功效宣称
- 医疗化表达
- 食品安全风险
- 母婴儿童风险
- 金融风险
- 私下交易
- 竞品攻击
- AI 标识缺失

平台：{{ platform }}
类目：{{ category }}
文本：{{ text }}
商品事实：{{ facts }}

输出 JSON：

{
  "blocked": false,
  "risk_level": "low|medium|high|blocked",
  "need_human_review": true,
  "reasons": [
    {"rule": "...", "message": "..."}
  ],
  "suggested_rewrite": "..."
}
