"""Logging setup shared by the bot and its cogs."""

from __future__ import annotations

import logging

import discord


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging using discord.py's coloured handler.

    discord.py ships a sensible coloured stream handler; we reuse it so our own
    loggers and the library's log lines share one consistent format.
    """
    discord.utils.setup_logging(level=getattr(logging, level.upper(), logging.INFO))
