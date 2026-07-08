from typing import Protocol

from app.core.errors import DomainError
from app.services.entities import SpeechTask


class AvatarProvider(Protocol):
    name: str

    def speak_audio(self, speech: SpeechTask) -> SpeechTask:
        """Send audio to an avatar runtime."""

    def interrupt(self) -> None:
        """Interrupt the current avatar playback."""


class LiveTalkingProvider:
    name = "live_talking"

    def speak_audio(self, speech: SpeechTask) -> SpeechTask:
        raise DomainError("LiveTalkingProvider is a disabled placeholder")

    def interrupt(self) -> None:
        raise DomainError("LiveTalkingProvider is a disabled placeholder")
