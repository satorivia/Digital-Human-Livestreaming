# 后续建议

1. 将当前 in-memory Store 替换为 SQLAlchemy repository，并补齐 Product、LiveSession、Review、Speech API 路由。
2. 为 VoiceProfile、VoiceLicense、AvatarAsset 增加迁移和授权校验。
3. 增加 EdgeTTS/CosyVoice/GPT-SoVITS Provider 插件类，但默认禁用真实调用。
4. 增加 LiveTalkingProvider HTTP 客户端占位与失败降级测试。
5. 将 control-web 接入真实 API 与 WebSocket 事件。
6. 扩展合规规则后台与价格一致性强校验。
7. 为 Makefile 增加 CI 环境依赖缓存说明，避免网络不可用时阻塞本地验证。
