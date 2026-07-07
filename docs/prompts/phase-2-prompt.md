# Phase 2 Prompt：真实 TTS + LiveTalking Gateway

请在 Mock 主链路已经通过的前提下，实现真实 TTS 和 AvatarGateway 扩展。

要求：

1. 增加 VoiceProfile 与 VoiceLicense。
2. 实现一个真实 TTS Provider 或可运行占位 Provider。
3. 实现 LiveTalkingProvider，但保留 MockAvatarProvider。
4. AvatarGateway 支持 provider 配置切换。
5. 支持 speak_audio、interrupt、idle、health_check。
6. 添加 SRS 预览 URL 逻辑。
7. 不破坏 Phase 1 的 Mock E2E 测试。
