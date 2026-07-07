# 02. 总体架构设计

## 1. 架构原则

本系统采用“模块化单体起步、可拆微服务演进”的架构。

第一版不要过度微服务化。建议先在一个 monorepo 中实现清晰模块边界，后续按压力和组织结构拆分服务。

核心原则：

1. 平台接入和业务中控解耦。
2. LLM、TTS、数字人均通过 Gateway/Provider 抽象。
3. 所有播报必须经过合规审核。
4. 直播流程由状态机控制，不由 LLM 控制。
5. 商品事实由数据库和知识库提供，不由 LLM 编造。
6. 所有核心动作可追溯。

## 2. 系统上下文

```text
┌─────────────────────────────────────────────────────────────┐
│                         外部系统                             │
│ 淘宝直播 / 抖音 / 小红书 / 视频号 / TikTok / OBS / LiveTalking │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Digital Human Live System                  │
│ 平台接入 / 商品库 / 中控 / AI / 合规 / TTS / 数字人 / 后台       │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                         基础设施                             │
│ PostgreSQL / Redis / Qdrant / MinIO / SRS / Prometheus        │
└─────────────────────────────────────────────────────────────┘
```

## 3. 逻辑架构

```text
┌──────────────────────────────────────────────┐
│                直播平台层                     │
│ 淘宝直播 / 抖音 / 小红书 / 视频号 / TikTok      │
└──────────────────────┬───────────────────────┘
                       │ 评论、订单、上下播、商品、平台警告
                       ↓
┌──────────────────────────────────────────────┐
│                Platform Adapter              │
│ 平台 API / Webhook / SDK / 人工输入 / Mock     │
│ 输出统一 PlatformEvent                         │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Event Gateway                  │
│ 去重 / 鉴权 / 限流 / 标准化 / 写入事件日志       │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Live Control Service           │
│ 直播状态机 / 商品调度 / 评论队列 / 人工接管      │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Product & RAG Service          │
│ 商品事实 / SKU / 价格 / 库存 / FAQ / 向量检索    │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                LLM Gateway                    │
│ 意图识别 / 候选回答 / 平台改写 / 话术生成        │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Compliance Service             │
│ 敏感词 / 绝对化 / 功效宣称 / 价格校验 / 人审      │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Human Review Service           │
│ 审核任务 / 通过 / 拒绝 / 改写 / 人工播报          │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                TTS Service                    │
│ 音色授权 / 语音合成 / 语音缓存 / 失败兜底         │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Avatar Gateway                 │
│ LiveTalking / 播报 / 打断 / 待机 / 形象切换      │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                Media Service                  │
│ OBS / SRS / RTMP / WebRTC / 录制 / 预览         │
└──────────────────────────────────────────────┘
```

## 4. 物理部署架构

### 4.1 本地开发

```text
开发机
├── api-server
├── admin-web
├── control-web
├── postgres container
├── redis container
├── qdrant container
├── minio container
└── srs container

可选 GPU 机器 / 本机
└── LiveTalking

直播工作站
├── OBS
└── 平台直播伴侣
```

### 4.2 测试环境

```text
应用服务器
├── api-server
├── admin-web
├── control-web
├── postgres
├── redis
├── qdrant
├── minio
└── srs

GPU 服务器
├── LiveTalking
├── CosyVoice / GPT-SoVITS
└── 可选本地 LLM
```

### 4.3 生产环境

```text
入口层
├── Nginx / API Gateway
└── TLS / WAF / 限流

应用层
├── api-server replicas
├── platform-adapter workers
├── live-control workers
├── compliance workers
└── background workers

AI 层
├── llm-gateway
├── tts-service
├── avatar-gateway
└── LiveTalking GPU nodes

数据层
├── PostgreSQL
├── Redis
├── Qdrant
├── MinIO / OSS / COS
└── ClickHouse 可后置

媒体层
├── SRS
├── OBS 工作站
└── 录制存储

监控层
├── Prometheus
├── Grafana
├── Loki / ELK
└── Alertmanager
```

## 5. 主链路时序图

```text
PlatformAdapter → EventGateway: PlatformEvent(CommentReceived)
EventGateway → CommentRouter: create comment task
CommentRouter → ProductRAG: resolve product and retrieve facts
ProductRAG → LLMGateway: generate candidate answer
LLMGateway → ComplianceService: review candidate
ComplianceService → HumanReviewService: create review task if needed
HumanReviewService → SpeechQueueService: approve and enqueue speech
SpeechQueueService → TTSService: generate audio
TTSService → AvatarGateway: speak_audio
AvatarGateway → LiveTalking: play audio with lip sync
AvatarGateway → SpeechQueueService: speech finished
SpeechQueueService → AuditLog: write playback log
```

## 6. 降级链路

| 故障 | 降级策略 |
|---|---|
| LLM 超时 | 使用缓存回答或固定兜底话术 |
| RAG 无命中 | 转人工审核，不自动回答 |
| ComplianceService 异常 | 默认拒绝自动播报，转人工 |
| TTS 失败 | 切备用 TTS Provider 或备用音色 |
| LiveTalking 失败 | 切待机视频 / 备用视频 / 静音 |
| 平台事件中断 | 场控台提示，允许人工输入评论 |
| 推流中断 | SRS/OBS 状态告警，暂停自动播报 |
| 平台警告 | 立即进入人工接管模式 |

## 7. 演进路线

MVP：模块化单体 + Mock Provider。

生产初期：保留单体 API，但后台任务和外部 Provider 拆 worker。

规模化：拆成以下服务：

- platform-adapter-service
- live-control-service
- product-rag-service
- llm-gateway-service
- compliance-service
- tts-service
- avatar-gateway-service
- media-service
- analytics-service
