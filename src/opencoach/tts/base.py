from __future__ import annotations

from abc import ABC, abstractmethod

from opencoach.schemas.tts import SpeechRequest, SpeechResult


class Speaker(ABC):
    @abstractmethod
    def speak(self, request: SpeechRequest) -> SpeechResult:
        """Generate and play speech for the supplied request."""
