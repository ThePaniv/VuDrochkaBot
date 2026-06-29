"""Serialized per-connection audio playback over a discord voice client."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

import discord

log = logging.getLogger("vudrochka_bot.audio")


@dataclass(slots=True)
class AudioJob:
    """A single clip to play. If ``cleanup`` is set the file is deleted after."""

    path: Path
    cleanup: bool = False


class AudioPlayer:
    """Plays queued clips one at a time over a single voice client.

    A self-restarting worker drains the queue and exits when it's empty; the
    next :meth:`submit` starts a fresh worker. This avoids the original bot's
    bug where a ``is_playing`` flag was set once and never reset, permanently
    wedging playback after the first disconnect.
    """

    def __init__(self, voice_client: discord.VoiceClient) -> None:
        self.voice_client = voice_client
        self._queue: asyncio.Queue[AudioJob] = asyncio.Queue()
        self._worker: asyncio.Task[None] | None = None

    def submit(self, job: AudioJob) -> None:
        """Queue a clip and ensure the drain worker is running."""
        self._queue.put_nowait(job)
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._drain())

    async def _drain(self) -> None:
        while not self._queue.empty():
            job = self._queue.get_nowait()
            try:
                if not self.voice_client.is_connected():
                    break
                await self._play_one(job.path)
            except Exception:
                log.exception("Error playing %s", job.path)
            finally:
                if job.cleanup:
                    job.path.unlink(missing_ok=True)
                self._queue.task_done()

    async def _play_one(self, path: Path) -> None:
        source = discord.FFmpegPCMAudio(str(path))
        finished = asyncio.Event()
        loop = asyncio.get_running_loop()

        def _after(error: Exception | None) -> None:
            if error is not None:
                log.error("Playback failed for %s: %s", path, error)
            loop.call_soon_threadsafe(finished.set)

        self.voice_client.play(source, after=_after)
        await finished.wait()

    async def aclose(self) -> None:
        """Cancel the worker and drop any queued clips (cleaning their files)."""
        if self._worker is not None and not self._worker.done():
            self._worker.cancel()
        while not self._queue.empty():
            job = self._queue.get_nowait()
            if job.cleanup:
                job.path.unlink(missing_ok=True)
