# 12. TTS、数字人、媒体设计

## 1. 总体链路

```text
播报文本
  ↓
ComplianceService 审核
  ↓
HumanReviewService 通过
  ↓
TTSService 生成音频
  ↓
AvatarGateway 调用数字人
  ↓
LiveTalking 口型同步
  ↓
虚拟摄像头 / RTMP / WebRTC
  ↓
OBS / SRS
  ↓
平台直播伴侣 / 平台推流
```

## 2. TTSService

### Provider

```text
MockTTSProvider          本地测试
EdgeTTSProvider          Demo
CosyVoiceProvider        主力中文 / 多语言 TTS
GPTSoVITSProvider        音色克隆
AliyunTTSProvider        云厂商兜底
TencentTTSProvider       云厂商兜底
FallbackTTSProvider      失败兜底
```

### 接口

```python
class TTSService:
    async def generate(self, request: TTSGenerateRequest) -> TTSResult: ...
    async def precache(self, request: TTSPCacheRequest) -> list[TTSResult]: ...
    async def list_voices(self, merchant_id: str) -> list[VoiceProfile]: ...
    async def clone_voice(self, request: VoiceCloneRequest) -> VoiceProfile: ...
    async def validate_voice_license(self, voice_id: str) -> bool: ...
```

### 缓存策略

```text
缓存 key = hash(text + voice_id + speed + emotion + platform + language)
```

适合预生成：

- 欢迎语。
- 商品卖点。
- 催单话术。
- FAQ 答案。
- 冷场话术。
- AI 身份提示。

实时生成：

- 观众个性化问题。
- 人工输入回答。

### 音色授权

音色必须有授权记录：

```text
voice_id
owner_name
source_file_url
consent_document_url
allowed_platforms
commercial_allowed
valid_from
valid_to
status
```

无授权或授权过期不能上线。

## 3. AvatarGateway

### 目标

主业务不能直接调用 LiveTalking。必须通过 AvatarGateway 隔离。

### 接口

```python
class AvatarGateway:
    async def speak_text(self, request: SpeakTextRequest) -> AvatarCommandResult: ...
    async def speak_audio(self, request: SpeakAudioRequest) -> AvatarCommandResult: ...
    async def interrupt(self, session_id: str) -> None: ...
    async def idle(self, session_id: str) -> None: ...
    async def switch_avatar(self, session_id: str, avatar_id: str) -> None: ...
    async def switch_scene(self, session_id: str, scene_id: str) -> None: ...
    async def get_stream_url(self, session_id: str) -> StreamInfo: ...
    async def health_check(self) -> AvatarHealth: ...
```

### Provider

```text
MockAvatarProvider
LiveTalkingProvider
FallbackVideoProvider
```

### SpeakAudioRequest

```json
{
  "session_id": "session_001",
  "avatar_id": "avatar_001",
  "speech_task_id": "speech_001",
  "audio_url": "s3://bucket/audio/xxx.wav",
  "text": "这款今天直播间有优惠。",
  "interrupt_current": false,
  "metadata": {
    "source": "approved_answer"
  }
}
```

## 4. LiveTalking 接入

### MVP 模式

```text
TTS 生成完整音频文件
  ↓
AvatarGateway 调用 LiveTalking 播放音频
  ↓
LiveTalking 输出虚拟摄像头 / RTMP
  ↓
OBS 采集
```

### 生产优化

```text
分句 TTS
分句播报
高频语音缓存
讲品脚本预生成
待机动作视频
异常备用视频
```

### 打断策略

触发打断：

- 人工接管。
- 平台警告。
- 高优先级评论。
- 直播异常。
- 场控手动打断。

打断流程：

```text
SpeechQueueService 标记当前 speech_task interrupted
  ↓
AvatarGateway.interrupt
  ↓
LiveTalking 停止当前播报
  ↓
状态机返回 EXPLAINING_PRODUCT 或 HUMAN_TAKEOVER
```

## 5. MediaService

### 职责

- SRS 预览地址。
- RTMP/WebRTC 健康状态。
- 录制开始/停止。
- 推流中断告警。
- 备用视频状态。

### MVP 推流链路

```text
LiveTalking
  ↓
虚拟摄像头 / RTMP
  ↓
OBS
  ↓
平台直播伴侣 / 平台推流地址
```

### 内部预览链路

```text
LiveTalking RTMP
  ↓
SRS
  ↓
WebRTC / HTTP-FLV
  ↓
场控台预览
```

## 6. 异常处理

| 异常 | 处理 |
|---|---|
| TTS 超时 | 切备用 Provider 或使用缓存语音 |
| 音色无授权 | 拒绝生成并提示运营 |
| LiveTalking 无响应 | 切 fallback video |
| RTMP 中断 | 告警并暂停自动播报 |
| OBS 未连接 | 场控台提示，不阻塞业务测试 |
| 音频文件丢失 | speech_task 标记 failed |

## 7. 测试要求

- MockTTS 生成假音频 URL。
- TTS 缓存命中。
- 音色授权失败。
- MockAvatar speak_audio 成功。
- Avatar interrupt 成功。
- LiveTalkingProvider 连接失败降级。
- MediaService 返回 SRS preview URL。
