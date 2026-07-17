"""
Talks to the LLM and enforces SMS-appropriate replies.
Two things matter more here than in a normal chatbot:
  1. Cost per message — this uses Groq's free tier, but it's still rate
     limited, so keep max_tokens tight and handle throttling gracefully
     instead of crashing the request.
  2. Reliability over cleverness — someone with no other way to get an
     answer is trusting this. The system prompt below asks for short,
     plain, hedged answers rather than confident-sounding guesses.
"""
import threading
from groq import Groq
from config import GROQ_API_KEY, MAX_REPLY_CHARS
from session import get_history, add_turn

_client = Groq(api_key=GROQ_API_KEY)

# Free-tier rate limits mean too many simultaneous requests will get
# throttled. This caps concurrent calls so bursts queue briefly instead
# of all failing at once.
_sem = threading.Semaphore(5)

MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = f"""You are Kaduda AI, an assistant reachable only by SMS text —
the person asking you a question may have no internet access at all.
Rules for every reply:
- Keep it under {MAX_REPLY_CHARS} characters. This is a hard limit, not a suggestion.
- Plain language. No markdown, no bullet points, no headers — SMS can't render them.
- If you don't know something or it needs a professional (medical, legal,
  financial), say so briefly and suggest where to go, rather than guessing.
- Be direct. No filler like "Great question!" — every character costs the user money.
"""

FALLBACK_REPLY = "Sorry, I'm a bit busy right now — please try again in a moment."


def get_ai_reply(phone_number: str, user_text: str) -> str:
    history = get_history(phone_number)
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + history
        + [{"role": "user", "content": user_text}]
    )

    try:
        with _sem:
            response = _client.chat.completions.create(
                model=MODEL,
                max_tokens=150,
                messages=messages,
            )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI error for {phone_number}: {e}")
        return FALLBACK_REPLY

    reply = _enforce_length(reply)
    add_turn(phone_number, "user", user_text)
    add_turn(phone_number, "assistant", reply)
    return reply


def _enforce_length(text: str) -> str:
    if len(text) <= MAX_REPLY_CHARS:
        return text
    # Hard truncate as a last-resort safety net — the prompt should prevent
    # this being needed, but never trust an LLM to obey a limit 100% of the time.
    return text[: MAX_REPLY_CHARS - 1].rsplit(" ", 1)[0] + "…"