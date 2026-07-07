# 16. 安全与隐私

## 1. 安全原则

- 最小权限。
- 密钥不进代码库。
- 用户信息最小化。
- 日志脱敏。
- 外部平台调用可审计。
- AI 生成内容可追溯。
- 音色和形象授权可证明。

## 2. 密钥管理

禁止提交：

- 平台 App Key。
- 平台 App Secret。
- access_token。
- refresh_token。
- LLM API Key。
- TTS API Key。
- MinIO/OSS/COS Secret。
- JWT Secret。

开发环境使用 `.env`，仓库只提交 `.env.example`。

生产环境使用 Secret Manager 或环境变量注入。

## 3. 日志脱敏

必须脱敏：

- 平台 token。
- API key。
- 手机号。
- 身份证。
- 地址。
- 用户平台 ID。

建议：

```text
platform_user_id → hash 后保存
手机号 → 138****0000
token → tok_****abcd
```

## 4. 用户数据

评论内容属于业务数据，但仍需控制访问：

- 只有对应商家可看。
- 平台用户 ID 尽量 hash。
- raw payload 可配置是否保存。
- 支持按时间清理。

## 5. 音色授权

语音克隆必须有授权记录。

字段：

```text
授权人
来源文件
授权文件
授权平台
是否商用
有效期
审核状态
```

无授权不能在生产直播使用。

## 6. 数字人形象授权

数字人形象必须有：

- 形象来源。
- 肖像授权或资产授权。
- 商用许可。
- 可用平台。
- 有效期。

## 7. AI 内容标识

系统必须支持：

- 画面角标。
- 定时口播。
- 直播间公告。
- 素材元数据标识。
- 播报日志。

## 8. 平台合规边界

禁止实现：

- 非官方抓包。
- 规避平台审核。
- 模拟真人绕过风控。
- 自动私信诱导绕平台交易。
- 删除或隐藏 AI 标识。
- 未授权声音克隆。
- 未授权真人形象复刻。

当平台未开放 API 时，使用：

- ManualInputAdapter。
- MockPlatformAdapter。
- 官方直播伴侣采集方案。

## 9. 权限设计

权限粒度：

```text
merchant:read/write
shop:read/write
platform_account:read/write
product:read/write
live_session:read/write/control
review:read/approve/reject
compliance:read/write
voice:read/write/approve
avatar:read/write/approve
system:admin
```

## 10. 审计日志

必须记录：

- 登录。
- 平台账号变更。
- 商品价格变更。
- 合规规则变更。
- Prompt 模板变更。
- 审核通过/拒绝/改写。
- 人工接管。
- 音色授权变更。
- 数字人资产变更。
