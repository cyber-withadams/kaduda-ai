"""
Command router.

Right now Kaduda AI is general-purpose: any text that isn't a recognized
command just goes to the AI. When you're ready to specialize (e.g. a SACCO
pilot with "BAL" / "LOAN" commands, or a farming vertical with "PRICE maize"),
register the new commands here — nothing else in the app needs to change.

Each handler takes (phone_number, raw_text) and returns a reply string,
or None to fall through to the next handler (and eventually to the AI).
"""

from typing import Callable, Optional

Handler = Callable[[str, str], Optional[str]]

_COMMANDS: dict[str, Handler] = {}


def register(keyword: str):
    """Decorator to register a command keyword (case-insensitive, first word of the SMS)."""
    def wrapper(fn: Handler):
        _COMMANDS[keyword.upper()] = fn
        return fn
    return wrapper


def try_handle(phone_number: str, raw_text: str) -> Optional[str]:
    first_word = raw_text.strip().split(" ", 1)[0].upper() if raw_text.strip() else ""
    handler = _COMMANDS.get(first_word)
    if handler:
        return handler(phone_number, raw_text)
    return None


# --- Example commands (disabled by default — uncomment / adapt when specializing) ---

# @register("HELP")
# def help_command(phone_number: str, raw_text: str) -> str:
#     return "Kaduda AI: just text your question and I'll reply. Msg rates may apply."
