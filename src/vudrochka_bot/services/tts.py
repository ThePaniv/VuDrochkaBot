"""Async text-to-speech via edge-tts (Microsoft Edge neural voices, free)."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

import edge_tts

log = logging.getLogger("vudrochka_bot.tts")

#: Cap the synthesized text so a hostile/huge nickname can't drive a giant request.
MAX_TTS_CHARS = 200


class TTSService:
    """Synthesizes speech to a temporary MP3 using an awaitable, non-blocking API.

    Unlike gTTS (synchronous, blocks the event loop), ``edge_tts.Communicate``
    is asyncio-native, so synthesis never stalls the bot's gateway heartbeat.
    """

    def __init__(self, voice: str) -> None:
        self.voice = voice

    async def synthesize(self, text: str) -> Path:
        """Render *text* to a temp ``.mp3`` and return its path.

        The caller owns the returned file and should delete it after playback
        (see :class:`~vudrochka_bot.services.audio.AudioJob` ``cleanup=True``).
        """
        clean = text.strip()[:MAX_TTS_CHARS]

        # mkstemp creates the file securely and hands back an os-level handle we
        # don't need (edge-tts writes by path), so close it immediately.
        fd, name = tempfile.mkstemp(prefix="vudrochka-tts-", suffix=".mp3")
        os.close(fd)
        path = Path(name)

        communicate = edge_tts.Communicate(clean, self.voice)
        await communicate.save(str(path))
        return path
