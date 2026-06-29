"""Tests for the Ukrainian count-word logic."""

from __future__ import annotations

import pytest

from vudrochka_bot.pluralization import (
    MAX_STATUS_LENGTH,
    OTTER,
    format_status,
    vudrochka_word,
)


@pytest.mark.parametrize(
    ("count", "word"),
    [
        (0, "ВиДрочок"),
        (1, "ВиДрочка"),
        (2, "ВиДрочки"),
        (3, "ВиДрочки"),
        (4, "ВиДрочки"),
        (5, "ВиДрочок"),
        (10, "ВиДрочок"),
        (11, "ВиДрочок"),  # the count that crashed the original 0-10 table
        (12, "ВиДрочок"),
        (14, "ВиДрочок"),
        (21, "ВиДрочка"),
        (22, "ВиДрочки"),
        (25, "ВиДрочок"),
        (101, "ВиДрочка"),
        (111, "ВиДрочок"),
    ],
)
def test_word_form(count: int, word: str) -> None:
    assert vudrochka_word(count) == word


def test_format_zero() -> None:
    assert format_status(0) == "Немає ВиДрочок"


def test_format_small_counts() -> None:
    assert format_status(1) == f"{OTTER}ВиДрочка"
    assert format_status(3) == OTTER * 3 + "ВиДрочки"


def test_format_respects_discord_limit() -> None:
    status = format_status(999)
    assert len(status) <= MAX_STATUS_LENGTH
    assert "999" in status


def test_negative_count_rejected() -> None:
    with pytest.raises(ValueError):
        vudrochka_word(-1)
