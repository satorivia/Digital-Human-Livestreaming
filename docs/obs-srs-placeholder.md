# OBS / SRS 使用占位说明

MVP 使用 MockAvatar，不要求真实 GPU 或 LiveTalking。后续真实预览建议：LiveTalking 输出 RTMP 到 SRS，OBS 采集 SRS/虚拟摄像头，再由人工推流到平台直播工具。不要在系统内保存真实平台推流密钥。

## 本地预览占位链路

```text
AvatarGateway / LiveTalkingProvider
  ↓ RTMP or virtual camera
SRS local service
  ↓ WebRTC / HTTP-FLV preview URL
control-web 场控台预览
```

## OBS 操作占位步骤

1. 启动本地依赖：`make up`。
2. 在 OBS 中添加媒体源或浏览器源，指向 MediaService 返回的 SRS 预览 URL。
3. OBS 推流密钥只在直播工作站本地配置，不提交到仓库，也不写入系统日志。
4. 平台直播伴侣/官方推流工具由人工操作；本系统不实现非官方抓包、反风控或平台绕过能力。
5. 如果 LiveTalking 或 SRS 不可用，场控台应提示降级状态，不阻塞 Mock E2E 测试。
