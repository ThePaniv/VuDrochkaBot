"""Tests for the voice-status cog's move/join/leave handling.

The cog's handler is async; rather than pull in pytest-asyncio we just drive the
coroutine with ``asyncio.run``. Discord objects are mocked — ``spec=`` makes the
``isinstance(..., discord.VoiceChannel)`` guard pass, and a channel's ``.members``
is whatever we set it to.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import discord

from vudrochka_bot.cogs.voice_status import VoiceStatusCog
from vudrochka_bot.pluralization import format_status


def _member(member_id: int) -> MagicMock:
    member = MagicMock()
    member.id = member_id
    return member


def _voice_channel(members: list[MagicMock], *, channel_id: int) -> MagicMock:
    channel = MagicMock(spec=discord.VoiceChannel)
    channel.members = members
    channel.name = "general"
    channel.id = channel_id
    channel.edit = AsyncMock()
    return channel


def _state(channel: MagicMock | None) -> MagicMock:
    state = MagicMock()
    state.channel = channel
    return state


def _dispatch(member: MagicMock, before: MagicMock | None, after: MagicMock | None) -> None:
    cog = VoiceStatusCog(MagicMock())
    asyncio.run(cog.on_voice_state_update(member, _state(before), _state(after)))


def _status_set_on(channel: MagicMock) -> str:
    channel.edit.assert_awaited_once()
    return channel.edit.await_args.kwargs["status"]


def test_move_clears_the_old_channel_even_if_member_still_listed() -> None:
    # Regression: on a direct move discord may still list the mover in the
    # channel they left. The old code counted them and left a stale otter.
    mover = _member(1)
    old = _voice_channel([mover], channel_id=10)  # not dropped from .members yet
    new = _voice_channel([mover, _member(2)], channel_id=20)

    _dispatch(mover, old, new)

    assert _status_set_on(old) == "Немає ВиДрочок"
    assert _status_set_on(new) == format_status(2)


def test_join_counts_the_new_member() -> None:
    joiner = _member(1)
    channel = _voice_channel([joiner], channel_id=10)

    _dispatch(joiner, None, channel)

    assert _status_set_on(channel) == format_status(1)


def test_leave_drops_the_member_even_if_still_listed() -> None:
    leaver = _member(1)
    channel = _voice_channel([leaver], channel_id=10)  # still listed at dispatch

    _dispatch(leaver, channel, None)

    assert _status_set_on(channel) == "Немає ВиДрочок"


def test_mute_toggle_in_place_is_ignored() -> None:
    member = _member(1)
    channel = _voice_channel([member], channel_id=10)

    # before.channel is after.channel — only mute/deafen changed.
    cog = VoiceStatusCog(MagicMock())
    asyncio.run(cog.on_voice_state_update(member, _state(channel), _state(channel)))

    channel.edit.assert_not_awaited()
