# 13. 前端后台设计

## 1. 前端应用拆分

```text
admin-web      商家 / 运营后台
control-web    直播场控台
monitor-web    系统监控台，可后置
```

MVP 可以先做：

- admin-web：商品、直播间、数字人基础配置。
- control-web：评论、审核、播报、人工接管。

## 2. 技术栈

```text
Vue 3
TypeScript
Vite
Element Plus
Pinia
Vue Router
Axios
WebSocket
ECharts
```

## 3. admin-web 菜单

```text
首页概览
商家管理
店铺管理
平台账号
商品管理
  ├── 商品列表
  ├── SKU 管理
  ├── 价格 / 库存
  ├── FAQ
  ├── 卖点
  ├── 售后政策
  ├── 禁用话术
  └── 平台差异话术
直播管理
  ├── 直播间
  ├── 直播场次
  ├── 直播排班
  └── 商品池
AI 能力
  ├── 模型配置
  ├── Prompt 模板
  ├── TTS 配置
  └── 音色管理
数字人资产
  ├── 数字人形象
  ├── 待机视频
  ├── 备用视频
  └── 场景模板
合规风控
  ├── 敏感词
  ├── 类目规则
  ├── 平台规则
  ├── AI 标识配置
  └── 审核记录
数据看板
系统设置
```

## 4. control-web 场控台布局

```text
┌────────────────────┬────────────────────────┬───────────────────────┐
│ 左侧：直播状态       │ 中间：评论/任务队列       │ 右侧：回答/审核/接管     │
│ - 平台              │ - 评论列表              │ - AI 候选回答           │
│ - 当前状态          │ - 用户昵称              │ - 合规风险              │
│ - 当前商品          │ - 评论内容              │ - 命中规则              │
│ - 数字人预览        │ - 意图标签              │ - 编辑框                │
│ - 推流状态          │ - 优先级                │ - 通过/拒绝/改写         │
│ - 快捷操作          │ - 待审核/已处理          │ - 人工接管              │
└────────────────────┴────────────────────────┴───────────────────────┘
```

## 5. 场控台必须支持

- 查看直播状态。
- 查看当前平台。
- 查看当前商品。
- 查看数字人预览。
- 查看推流状态。
- 查看评论队列。
- 查看 AI 候选回答。
- 查看合规风险和命中原因。
- 编辑回答后通过。
- 拒绝回答。
- 手动输入回答。
- 一键人工接管。
- 一键停止接管。
- 一键静音。
- 一键打断。
- 一键切备用视频。
- 查看播报历史。
- 查看审核历史。
- 查看平台警告。

## 6. WebSocket 事件

连接：

```text
/ws/live-sessions/{session_id}
```

事件类型：

```text
state_changed
comment_received
answer_generated
compliance_checked
review_task_created
review_task_updated
speech_started
speech_finished
avatar_error
platform_warning
stream_health_changed
human_takeover_started
human_takeover_ended
```

前端收到事件后必须更新对应 Pinia store。

## 7. 前端状态管理

Pinia stores：

```text
useAuthStore
useMerchantStore
useProductStore
useLiveSessionStore
useCommentStore
useReviewStore
useSpeechStore
useAvatarStore
useMediaStore
useComplianceStore
```

## 8. 页面 MVP

### 商品列表页

- 商品列表。
- 新建商品。
- 编辑商品。
- FAQ 管理入口。
- 索引状态。

### 商品详情页

- 基础信息。
- SKU。
- 价格。
- FAQ。
- 卖点。
- 禁用表达。
- 平台差异话术。

### 直播场次页

- 创建直播场次。
- 选择直播间。
- 选择商品池。
- 选择数字人。
- 选择音色。
- 启动 Mock 直播。

### 场控台

- 评论模拟输入。
- 评论队列。
- 生成候选回答。
- 审核通过/拒绝/改写。
- 播报任务状态。
- 人工接管。

## 9. 前端权限

| 功能 | 运营 | 场控 | 审核 | 管理员 |
|---|---|---|---|---|
| 商品编辑 | 是 | 否 | 否 | 是 |
| 直播启动 | 是 | 是 | 否 | 是 |
| 审核通过 | 否 | 是 | 是 | 是 |
| 合规规则编辑 | 否 | 否 | 是 | 是 |
| 平台账号配置 | 否 | 否 | 否 | 是 |
| 人工接管 | 否 | 是 | 否 | 是 |

## 10. E2E 前端验收

- 能登录。
- 能创建商品。
- 能添加 FAQ。
- 能创建直播场次。
- 能启动 Mock 直播。
- 能模拟评论。
- 能看到候选回答。
- 能通过审核。
- 能看到播报完成状态。
- 能打开人工接管并恢复。
