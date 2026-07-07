# 17. 开发里程碑

## 阶段 0：工程骨架

### 目标

建立可持续开发的仓库、后端、前端、基础设施和测试框架。

### 交付物

```text
monorepo 初始化
FastAPI 后端骨架
Vue3 admin-web/control-web 骨架
PostgreSQL / Redis / Qdrant / MinIO / SRS docker-compose
统一配置管理
统一日志
统一错误码
基础鉴权
Alembic 迁移框架
AGENTS.md
README
Makefile
基础 CI
```

### 验收

```text
make up 可启动依赖
/api/v1/healthz 正常
前端可访问
make migrate 可执行
make test 可运行
```

## 阶段 1：商品库 + Mock 全链路

### 目标

不接真实平台和真实数字人，先跑通业务主链路。

### 交付物

```text
Merchant / Product / SKU / FAQ / SellingPoint CRUD
Qdrant 知识库索引
MockPlatformAdapter
评论模拟器
CommentRouter
LiveSession 状态机
LLMGateway MockProvider
ComplianceService 基础规则
HumanReviewService
TTS MockProvider
Avatar MockProvider
场控台基础版
E2E: mock comment to avatar speech
```

### 验收

```text
创建商品和 FAQ
启动 Mock 直播
模拟评论“这款多少钱”
生成候选回答
合规审核
人工通过
Mock 播报完成
全链路日志可查
```

## 阶段 2：真实 TTS + AvatarGateway + LiveTalking

### 目标

让数字人真实播报。

### 交付物

```text
TTSService EdgeTTSProvider
CosyVoiceProvider 预留
GPTSoVITSProvider 预留
语音缓存
VoiceProfile / VoiceLicense
AvatarGateway
LiveTalkingProvider
打断能力
待机视频
fallback 视频
SRS 预览
OBS 操作文档
```

### 验收

```text
场控台审核通过后生成真实音频
AvatarGateway 调用 LiveTalking
数字人口型播报
SRS 可预览
OBS 可采集
```

## 阶段 3：淘宝直播 Adapter

### 目标

优先跑通最适合电商闭环的平台接入。

### 交付物

```text
TaobaoLiveAdapter
淘宝评论事件接收
淘宝上下播事件接收
淘宝订单事件接收
直播间商品查询
商品 ID 映射
淘宝平台合规规则
```

### 验收

```text
淘宝评论进入系统
绑定当前商品
生成候选回答
合规审核
人工通过
数字人播报
订单事件入库
```

## 阶段 4：抖音 Adapter

### 目标

接入抖音直播评论互动能力，强化合规和人工接管。

### 交付物

```text
DouyinAdapter
评论任务启动/停止/查询状态
评论事件接收
平台警告事件
抖音平台规则
高风险默认人审
一键人工接管
```

### 验收

```text
抖音评论进入系统
低风险候选回答
中高风险强制人审
平台警告触发暂停 AI 自动互动
```

## 阶段 5：合规系统强化

### 目标

使系统具备商业运营的基本合规能力。

### 交付物

```text
敏感词库
绝对化用语库
类目规则
平台规则
价格一致性校验
功效宣称检测
AI 标识配置
人工审核流强化
审核日志
合规看板
```

### 验收

```text
所有播报前经过 ComplianceService
高风险不会自动播报
blocked 必须禁止播报
AI 标识常驻
审核可追溯
```

## 阶段 6：小红书 / 视频号保守接入

### 目标

先可播、可控，不追求全自动。

### 交付物

```text
XiaohongshuAdapter 基础版
WeChatChannelsAdapter 基础版
ManualInputAdapter 强化
保守模式配置
平台差异口吻
```

### 验收

```text
可通过人工输入评论触发同样的审核和播报链路
保守模式默认禁止自动回答
```

## 阶段 7：TikTok 国际化

### 目标

扩展海外直播能力。

### 交付物

```text
TikTokAdapter
英文 / 多语言知识库
多语言 Prompt
英文 TTS
多币种价格话术
跨境物流 FAQ
海外售后 FAQ
AIGC 标签配置
```

## 阶段 8：规模化运营

### 目标

从单直播间扩展到多直播间、多账号、多商家。

### 交付物

```text
多商家权限
多直播间并发
排班系统
多数字人形象
多音色
数据看板
成本统计
模型调用监控
直播质量监控
异常告警
```
