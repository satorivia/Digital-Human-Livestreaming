from app.services.entities import LiveSession, LiveState
from app.services.store import InMemoryStore


class IllegalLiveStateTransition(ValueError):
    pass


class LiveSessionStateMachine:
    allowed_transitions: set[tuple[LiveState, LiveState]] = {
        (LiveState.CREATED, LiveState.LIVE),
        (LiveState.LIVE, LiveState.WAITING_REVIEW),
        (LiveState.WAITING_REVIEW, LiveState.SPEAKING),
        (LiveState.SPEAKING, LiveState.LIVE),
        (LiveState.LIVE, LiveState.HUMAN_TAKEOVER),
        (LiveState.HUMAN_TAKEOVER, LiveState.LIVE),
        (LiveState.LIVE, LiveState.ENDED),
    }

    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def create(self, product_id: str) -> LiveSession:
        session = LiveSession(product_id=product_id)
        self.store.sessions[session.id] = session
        return session

    def transition(self, live_session_id: str, target_state: LiveState, reason: str) -> LiveSession:
        session = self.store.sessions[live_session_id]
        transition = (session.state, target_state)
        if transition not in self.allowed_transitions:
            raise IllegalLiveStateTransition(f"illegal transition {session.state}->{target_state}")
        previous_state = session.state
        session.state = target_state
        self.store.state_logs.append(
            {
                "session_id": live_session_id,
                "from": previous_state,
                "to": target_state,
                "reason": reason,
            },
        )
        return session
