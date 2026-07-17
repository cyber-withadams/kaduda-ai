"""
Kaduda AI — SMS webhook.

Africa's Talking calls this endpoint (as form-encoded POST) every time
someone texts your shortcode/number. We reply asynchronously via their
Send SMS API — the webhook itself just needs to return 200 quickly so
Africa's Talking doesn't retry/timeout.

Local test (no real phone needed):
    curl -X POST http://localhost:8000/sms \
      -d "from=+254700000000" -d "to=KADUDA" -d "text=What is compound interest?"
"""

from fastapi import FastAPI, Form, BackgroundTasks
from commands import try_handle
from ai import get_ai_reply
from sms import send_sms

app = FastAPI(title="Kaduda AI")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Kaduda AI"}


@app.post("/sms")
async def receive_sms(
    background_tasks: BackgroundTasks,
    from_: str = Form(..., alias="from"),
    text: str = Form(""),
    to: str = Form(""),
):
    phone_number = from_.strip()
    user_text = text.strip()

    background_tasks.add_task(_handle_and_reply, phone_number, user_text)

    # Africa's Talking just needs a fast 200 — the actual reply is sent
    # separately via the Send SMS API in the background task above.
    return {"received": True}


def _handle_and_reply(phone_number: str, user_text: str):
    if not user_text:
        return

    # Structured commands (SACCO balance, farming prices, etc.) take
    # priority once you register them in commands.py. Empty product
    # today, ready the moment you specialize.
    reply = try_handle(phone_number, user_text)

    if reply is None:
        reply = get_ai_reply(phone_number, user_text)

    send_sms(phone_number, reply)
