"""VuDrochkaBot — a small Discord voice-channel bot.

Two behaviours, both reacting to voice-channel join/leave/move events:

1. Rewrites a voice channel's *status* to ``N x :otter:`` plus the grammatically
   correct Ukrainian word form (``ВиДрочка`` / ``ВиДрочки`` / ``ВиДрочок``).
2. Optionally joins the channel and plays a neural-TTS greeting for each joiner.
"""

__version__ = "1.0.0"
