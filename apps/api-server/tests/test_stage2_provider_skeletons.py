import pytest

pytest.importorskip("pydantic")

from app.core.errors import DomainError
from app.services import (
    CosyVoiceProvider,
    EdgeTTSProvider,
    GPTSoVITSProvider,
    InMemoryStore,
    LiveTalkingProvider,
    SpeechTask,
    TTSService,
    VoiceService,
)


def test_voice_license_is_required_before_authorized_tts_generation() -> None:
    store = InMemoryStore()
    voices = VoiceService(store)
    profile = voices.create_voice_profile("主播音色", provider="mock", voice_id="anchor")

    with pytest.raises(DomainError):
        TTSService(store).generate_with_authorized_voice("欢迎", profile.id, voices)

    license_record = voices.authorize_voice(
        profile.id,
        authorized_by="operator",
        authorization_record_url="mock://voice-license/record",
    )
    asset = TTSService(store).generate_with_authorized_voice("欢迎", profile.id, voices)

    assert license_record.voice_profile_id == profile.id
    assert asset.audio_url.startswith("mock://audio/")


def test_real_tts_providers_are_disabled_placeholders() -> None:
    for provider in [EdgeTTSProvider(), CosyVoiceProvider(), GPTSoVITSProvider()]:
        with pytest.raises(NotImplementedError):
            provider.generate("测试", "cache-key")


def test_livetalking_provider_is_disabled_placeholder() -> None:
    provider = LiveTalkingProvider()
    with pytest.raises(DomainError):
        provider.speak_audio(SpeechTask(text="hello"))
    with pytest.raises(DomainError):
        provider.interrupt()
