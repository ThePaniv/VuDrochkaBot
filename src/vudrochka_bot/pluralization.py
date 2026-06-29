"""Build the Ukrainian voice-channel status string for a member count.

The original bot used a hand-written JSON table that only covered 0-10 members
and raised ``KeyError`` for an 11th joiner. This computes the correct Ukrainian
plural form for *any* count using the standard East-Slavic agreement rules, so
it never runs out of entries.
"""

from __future__ import annotations

#: Voice-channel status has a hard 500-character limit on Discord's side.
MAX_STATUS_LENGTH = 500

#: The literal emoji shortcode Discord renders as 🦦 in a channel status.
OTTER = ":otter:"

# Grammatical forms of the coined noun "ВиДрочка".
_NOMINATIVE_SINGULAR = "ВиДрочка"  # 1, 21, 31, ...
_PAUCAL = "ВиДрочки"  # 2-4, 22-24, ...
_GENITIVE_PLURAL = "ВиДрочок"  # 0, 5-20, 25-30, ...


def vudrochka_word(count: int) -> str:
    """Return the correct Ukrainian word form for *count* members.

    Follows the East-Slavic numeral-agreement rule:

    * ``count`` ending in 1 (but not 11)            -> nominative singular
    * ``count`` ending in 2, 3, 4 (but not 12-14)   -> paucal
    * everything else (0, 5-20, ...)                -> genitive plural
    """
    if count < 0:
        raise ValueError("member count cannot be negative")

    last_two = count % 100
    last_one = count % 10

    if 11 <= last_two <= 14:
        return _GENITIVE_PLURAL
    if last_one == 1:
        return _NOMINATIVE_SINGULAR
    if 2 <= last_one <= 4:
        return _PAUCAL
    return _GENITIVE_PLURAL


def format_status(count: int) -> str:
    """Render the full voice-channel status for *count* members.

    Examples::

        0 -> "Немає ВиДрочок"
        1 -> ":otter:ВиДрочка"
        3 -> ":otter::otter::otter:ВиДрочки"
        5 -> ":otter:x5 ВиДрочок"  (only once one-otter-each would exceed 500 chars)
    """
    word = vudrochka_word(count)
    if count == 0:
        return f"Немає {word}"

    status = OTTER * count + word
    if len(status) <= MAX_STATUS_LENGTH:
        return status

    # A very large channel would overflow the 500-char status if we drew one
    # otter per member, so fall back to a compact multiplier form.
    return f"{OTTER}x{count} {word}"
