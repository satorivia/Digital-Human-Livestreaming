from app.core.errors import DomainError
from app.services.entities import AvatarCommandStatus, SpeechStatus, SpeechTask
from app.services.store import InMemoryStore


class AvatarGateway:
    def __init__(self, store: InMemoryStore, fail: bool = False) -> None:
        self.store = store
        self.fail = fail

    def speak_audio(self, speech: SpeechTask) -> SpeechTask:
        if self.fail:
            speech.status = SpeechStatus.FAILED
            speech.failure_reason = "mock avatar provider failure"
            self._log_command("speak_audio", AvatarCommandStatus.FAILED, speech_id=speech.id)
            raise DomainError("mock avatar provider failure")
        speech.status = SpeechStatus.FINISHED
        self._log_command("speak_audio", AvatarCommandStatus.SUCCESS, speech_id=speech.id)
        return speech

    def speak_text(self, text: str) -> None:
        if self.fail:
            self._log_command("speak_text", AvatarCommandStatus.FAILED)
            raise DomainError("mock avatar provider failure")
        self._log_command("speak_text", AvatarCommandStatus.SUCCESS, text=text)

    def interrupt(self, speech: SpeechTask | None = None) -> SpeechTask | None:
        if speech is not None and speech.status == SpeechStatus.SPEAKING:
            speech.status = SpeechStatus.INTERRUPTED
        self._log_command("interrupt", AvatarCommandStatus.SUCCESS, speech_id=getattr(speech, "id", None))
        return speech

    def idle(self) -> None:
        self._log_command("idle", AvatarCommandStatus.SUCCESS)

    def _log_command(self, command: str, status: AvatarCommandStatus, **metadata: object) -> None:
        self.store.avatar_logs.append({"command": command, "status": status.value, **metadata})
