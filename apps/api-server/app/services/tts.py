from hashlib import sha256

from app.core.errors import DomainError
from app.services.entities import TTSAsset
from app.services.store import InMemoryStore


class MockTTSProvider:
    name = "mock"

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def generate(self, text: str, cache_key: str) -> tuple[str, int]:
        if self.fail:
            raise DomainError("mock tts provider failure")
        duration_ms = max(800, len(text) * 120)
        return f"mock://audio/{cache_key}.wav", duration_ms


class TTSService:
    def __init__(self, store: InMemoryStore, provider: MockTTSProvider | None = None) -> None:
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

    def precache(self, texts: list[str], voice_id: str = "default") -> list[TTSAsset]:
        return [self.generate(text, voice_id=voice_id) for text in texts]
