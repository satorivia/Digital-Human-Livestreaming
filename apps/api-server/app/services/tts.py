from hashlib import sha256
from typing import Protocol

from app.core.errors import DomainError
from app.services.entities import TTSAsset, VoiceLicense, VoiceProfile
from app.services.store import InMemoryStore


class TTSProvider(Protocol):
    name: str

    def generate(self, text: str, cache_key: str) -> tuple[str, int]:
        """Generate speech audio and return URL plus duration in milliseconds."""


class MockTTSProvider:
    name = "mock"

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def generate(self, text: str, cache_key: str) -> tuple[str, int]:
        if self.fail:
            raise DomainError("mock tts provider failure")
        duration_ms = max(800, len(text) * 120)
        return f"mock://audio/{cache_key}.wav", duration_ms


class EdgeTTSProvider:
    name = "edge_tts"

    def generate(self, text: str, cache_key: str) -> tuple[str, int]:
        raise NotImplementedError("EdgeTTSProvider is a disabled placeholder")


class CosyVoiceProvider:
    name = "cosy_voice"

    def generate(self, text: str, cache_key: str) -> tuple[str, int]:
        raise NotImplementedError("CosyVoiceProvider is a disabled placeholder")


class GPTSoVITSProvider:
    name = "gpt_sovits"

    def generate(self, text: str, cache_key: str) -> tuple[str, int]:
        raise NotImplementedError("GPTSoVITSProvider is a disabled placeholder")


class VoiceService:
    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def create_voice_profile(self, name: str, provider: str, voice_id: str) -> VoiceProfile:
        profile = VoiceProfile(name=name, provider=provider, voice_id=voice_id)
        self.store.voice_profiles[profile.id] = profile
        return profile

    def authorize_voice(
        self,
        voice_profile_id: str,
        authorized_by: str,
        authorization_record_url: str,
    ) -> VoiceLicense:
        if voice_profile_id not in self.store.voice_profiles:
            raise DomainError("voice profile does not exist")
        license_record = VoiceLicense(
            voice_profile_id=voice_profile_id,
            authorized_by=authorized_by,
            authorization_record_url=authorization_record_url,
        )
        self.store.voice_licenses[license_record.id] = license_record
        return license_record

    def assert_authorized(self, voice_profile_id: str) -> None:
        if not any(
            license_record.voice_profile_id == voice_profile_id
            for license_record in self.store.voice_licenses.values()
        ):
            raise DomainError("voice profile is not authorized")


class TTSService:
    def __init__(self, store: InMemoryStore, provider: TTSProvider | None = None) -> None:
        self.store = store
        self.provider = provider or MockTTSProvider()

    def cache_key(self, text: str, voice_id: str = "default") -> str:
        return sha256(f"{self.provider.name}:{voice_id}:{text}".encode("utf-8")).hexdigest()

    def generate(self, text: str, voice_id: str = "default") -> TTSAsset:
        key = self.cache_key(text, voice_id)
        cached = self.store.tts_assets.get(key)
        if cached is not None:
            return cached
        audio_url, duration_ms = self.provider.generate(text, key)
        asset = TTSAsset(
            cache_key=key,
            text=text,
            audio_url=audio_url,
            provider=self.provider.name,
            duration_ms=duration_ms,
        )
        self.store.tts_assets[key] = asset
        return asset

    def generate_with_authorized_voice(
        self,
        text: str,
        voice_profile_id: str,
        voice_service: VoiceService,
    ) -> TTSAsset:
        voice_service.assert_authorized(voice_profile_id)
        profile = self.store.voice_profiles[voice_profile_id]
        return self.generate(text, voice_id=profile.voice_id)

    def precache(self, texts: list[str], voice_id: str = "default") -> list[TTSAsset]:
        return [self.generate(text, voice_id=voice_id) for text in texts]
