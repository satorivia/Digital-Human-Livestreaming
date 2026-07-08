# 后续建议

1. 将当前 in-memory Store 替换为 SQLAlchemy repository，并补齐 Product、LiveSession、Review、Speech API 路由。
2. 为 VoiceProfile、VoiceLicense、AvatarAsset 增加更完整的授权字段、过期时间和审计查询。
3. 在保持默认禁用的前提下，为 EdgeTTS/CosyVoice/GPT-SoVITS Provider 增加配置 schema 和契约测试。
4. 为 LiveTalkingProvider 增加 HTTP 客户端配置、超时、重试和失败降级测试，但不要在自动测试中依赖真实服务。
5. 将 control-web 接入真实 API 与 WebSocket 事件，并补齐 Pinia stores。
6. 扩展合规规则后台与价格一致性强校验。
7. 为 Makefile 增加 CI 环境依赖缓存说明，避免网络不可用时阻塞本地验证。
8. 增加 AvatarAsset 授权模型和 migration，确保数字人形象使用授权可审计。
