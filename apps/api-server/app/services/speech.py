from app.services.avatar import AvatarGateway
from app.services.entities import SpeechTask
from app.services.store import InMemoryStore
from app.services.tts import TTSService


class SpeechQueueService:
    def __init__(self, store: InMemoryStore, tts: TTSService, avatar: AvatarGateway) -> None:
        self.store = store
        self.tts = tts
        self.avatar = avatar

    def enqueue_speech(self, text: str, priority: int = 100) -> SpeechTask:
        task = SpeechTask(text=text, priority=priority)
        self.store.speeches[task.id] = task
        return task

    def next_task(self) -> SpeechTask | None:
        queued = [task for task in self.store.speeches.values() if task.status == "queued"]
        if not queued:
            return None
        return sorted(queued, key=lambda task: task.priority)[0]

    def play_next(self) -> SpeechTask | None:
        task = self.next_task()
        if task is None:
            return None
        asset = self.tts.generate(task.text)
        task.audio_url = asset.audio_url
        task.status = "speaking"
        return self.avatar.speak_audio(task)

    def enqueue_and_play(self, text: str, priority: int = 100) -> SpeechTask:
        self.enqueue_speech(text, priority=priority)
        task = self.play_next()
        if task is None:
            raise RuntimeError("speech queue unexpectedly empty")
        return task
