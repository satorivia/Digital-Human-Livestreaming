from app.core.errors import DomainError
from app.services.entities import SpeechTask
from app.services.store import InMemoryStore


class AvatarGateway:
    def __init__(self, store: InMemoryStore, fail: bool = False) -> None:
        self.store = store
        self.fail = fail

    def speak_audio(self, speech: SpeechTask) -> SpeechTask:
        if self.fail:
            speech.status = "failed"
            self.store.avatar_logs.append({"speech_id": speech.id, "status": "failed"})
            raise DomainError("mock avatar provider failure")
        speech.status = "finished"
        self.store.avatar_logs.append({"speech_id": speech.id, "status": "success"})
        return speech

    def speak_text(self, text: str) -> None:
        self.store.avatar_logs.append({"command": "speak_text", "text": text, "status": "success"})

    def interrupt(self) -> None:
        self.store.avatar_logs.append({"command": "interrupt", "status": "success"})

    def idle(self) -> None:
        self.store.avatar_logs.append({"command": "idle", "status": "success"})
