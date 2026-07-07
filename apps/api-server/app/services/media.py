class MediaService:
    def preview_url(self, stream_key: str) -> dict[str, str]:
        return {
            "webrtc_url": f"http://localhost:8080/live/{stream_key}.flv",
            "status": "mock_ready",
        }
