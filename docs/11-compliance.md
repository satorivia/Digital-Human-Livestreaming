# 11. 合规审核设计

## 1. 原则

合规模块是生产系统的核心，不是附加功能。

规则：

- 所有 AI 生成播报必须先过 ComplianceService。
- blocked 结果禁止播报。
- high 风险默认人工处理。
- medium 风险默认人工审核。
- low 风险是否自动通过必须按平台和类目配置。
- 平台警告时必须暂停自动互动。

## 2. 合规范围

```text
AI 标识
敏感词
绝对化用语
价格一致性
虚假宣传
功效宣称
医疗健康风险
食品安全风险
美妆功效风险
母婴儿童风险
金融风险
竞品攻击
私下交易
平台差异规则
音色授权
数字人形象授权
日志留存
```

## 3. ComplianceService 结构

```text
ComplianceService
├── SensitiveWordChecker
├── AbsoluteClaimChecker
├── PriceConsistencyChecker
├── MedicalClaimChecker
├── FoodSafetyChecker
├── CosmeticClaimChecker
├── FinanceRiskChecker
├── ChildProductChecker
├── CompetitorAttackChecker
├── PrivateTransactionChecker
├── PlatformRuleChecker
├── AILabelChecker
├── VoiceLicenseChecker
├── AvatarLicenseChecker
├── LLMComplianceReviewer
└── HumanReviewWorkflow
```

## 4. 审核输入

```json
{
  "merchant_id": "merchant_001",
  "platform": "douyin",
  "live_session_id": "session_001",
  "product_id": "prod_001",
  "category": "beauty",
  "text": "敏感肌一定能用，保证不过敏。",
  "source": "llm_answer",
  "facts_used": ["faq_001"],
  "context": {
    "comment": "敏感肌能用吗？",
    "intent": "suitability_query"
  }
}
```

## 5. 审核输出

```json
{
  "blocked": true,
  "risk_level": "high",
  "need_human_review": true,
  "reasons": [
    {
      "rule": "absolute_claim",
      "message": "命中绝对化表达：一定、保证"
    },
    {
      "rule": "cosmetic_claim",
      "message": "涉及敏感肌适用性，不能承诺不过敏"
    }
  ],
  "suggested_rewrite": "这款主打日常温和清洁，敏感肌用户建议先做局部测试。"
}
```

## 6. 风险分级

| 等级 | 示例 | 策略 |
|---|---|---|
| low | 多少钱、几件装、怎么领券 | 可配置自动通过 |
| medium | 敏感肌、孕妇、儿童、适用人群 | 默认人工审核 |
| high | 保证有效、治疗、治愈、不过敏 | 默认拦截或人工处理 |
| blocked | 私下交易、违法违规、绕平台付款 | 禁止播报 |
| platform_warning | 平台提示异常 | 暂停自动互动，人工接管 |

## 7. 绝对化用语规则

示例词：

```text
最
第一
顶级
永久
100%
绝对
保证
无副作用
完全没有风险
一定有效
根治
治愈
```

规则：

- 命中不一定直接 blocked，但至少 medium。
- 美妆、食品、保健、母婴、医疗相关类目命中后优先 high。

## 8. 价格一致性

LLM 输出价格时必须校验：

- 是否与 `product_price` 中当前平台价格一致。
- 是否在有效期内。
- 是否包含“以页面显示为准”之类兜底提示。
- 是否错误引用其他平台价格。

错误示例：

```text
今天一定只要 99 元。
```

推荐：

```text
今天直播间到手价以页面显示为准，可以先领券再下单。
```

## 9. AI 标识

系统必须支持：

```text
画面角标：AI数字人主播
直播间公告：本直播间使用 AI 数字人技术
定时口播：本直播间主播为 AI 数字人
素材元数据：AI 生成素材标记
日志留存：每句话来源、审核人、播报时间
```

后台配置：

```json
{
  "platform": "taobao",
  "ai_label_enabled": true,
  "screen_badge_text": "AI数字人主播",
  "voice_disclosure_interval_minutes": 20,
  "voice_disclosure_text": "本直播间主播为AI数字人。"
}
```

## 10. 平台差异策略

### 淘宝直播

- 商品事实优先。
- 评论、订单、上下播等事件要留痕。
- 价格、优惠、商品信息必须与平台一致。

### 抖音

- 默认强合规。
- 中高风险评论全部人工审核。
- 平台警告时立刻人工接管。
- AI 标识常驻。

### 小红书

- 默认保守口吻。
- 强种草弱销售。
- 不夸大功效。
- 默认人工审核。

### 视频号

- 默认保守模式。
- 不做全自动无人托管。
- 优先真人场控。

### TikTok

- 开启 AI-generated content 标签策略。
- 多语言合规规则。
- 禁止误导性深度伪造和虚假背书。

## 11. 人工审核工作流

```text
ComplianceService 输出 need_human_review=true
  ↓
创建 human_review_task
  ↓
场控台显示候选回答 + 风险原因
  ↓
审核员选择：通过 / 拒绝 / 改写 / 手动回答
  ↓
通过或改写后生成 speech_task
  ↓
写入 audit_log
```

## 12. 测试用例要求

至少提供：

- 价格低风险通过。
- 敏感肌 medium。
- 保证不过敏 high/blocked。
- 私下交易 blocked。
- 医疗治愈 blocked。
- 平台警告触发人工接管。
- 合规服务异常时默认不播报。
- 人工改写后可播报。
- AI 标识配置缺失时报警。
