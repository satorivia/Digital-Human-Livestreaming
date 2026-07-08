# 后续建议

1. 继续 P0-2：把 P0-1 API 从 in-memory Store 逐步切换为 SQLAlchemy repository，优先 Product、LiveSession、Review、SpeechTask。
2. 为新增主链路表补充 repository 测试和 API-level DB E2E：comment_task、answer_candidate、compliance_result、human_review_task、speech_task、tts_asset、avatar_command_log、audit_log。
3. 将 control-web 页面从静态数据切换到 Pinia store 数据，并处理加载态、错误态、空状态。
4. 为 VoiceProfile、VoiceLicense、AvatarAsset 增加更完整的授权字段、过期时间和审计查询。
5. 在保持默认禁用的前提下，为 EdgeTTS/CosyVoice/GPT-SoVITS Provider 增加配置 schema 和契约测试。
6. 为 LiveTalkingProvider 增加 HTTP 客户端配置、超时、重试和失败降级测试，但不要在自动测试中依赖真实服务。
7. 扩展合规规则后台与价格一致性强校验。
8. 为 Makefile 增加 CI 环境依赖缓存说明，避免网络不可用时阻塞本地验证。
9. 增加 AvatarAsset 授权模型和 migration，确保数字人形象使用授权可审计。
10. 后续再推进 DouyinAdapter 保守配置/normalize_event 骨架；仍不得封装真实平台任务启动或拉流接口。
