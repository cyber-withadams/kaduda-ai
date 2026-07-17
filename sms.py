"""
Thin wrapper around Africa's Talking so the rest of the app doesn't
need to know which SMS provider is behind it. If you ever switch
providers, this is the only file that changes.
"""
import africastalking
from config import AT_USERNAME, AT_API_KEY, AT_SENDER_ID

africastalking.initialize(AT_USERNAME, AT_API_KEY)
_sms = africastalking.SMS


def _normalize_number(number: str) -> str:
    """
    Africa's Talking requires E.164 format (leading '+'). Numbers coming
    through form-encoded POST data often lose their '+' (it gets decoded
    as a space, then stripped upstream), so we restore it here — this is
    the one place that actually requires the format, so it's the right
    place to enforce it.
    """
    number = number.strip()
    if not number.startswith("+"):
        number = "+" + number
    return number


def send_sms(to_number: str, message: str):
    """
    Send an SMS reply. In sandbox mode, Africa's Talking doesn't actually
    deliver to real phones — it logs the send so you can verify the flow
    end-to-end before going live.
    """
    to_number = _normalize_number(to_number)
    try:
        response = _sms.send(message, [to_number], sender_id=AT_SENDER_ID)
        print(f"[sms.send_sms] sent to {to_number}: {message}")
        return response
    except Exception as exc:
        # Never let an SMS-send failure crash the webhook — log and move on.
        print(f"[sms.send_sms] failed to send to {to_number}: {exc}")
        return None