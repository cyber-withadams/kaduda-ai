import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "")
AT_SENDER_ID = os.getenv("AT_SENDER_ID", "KADUDA")
MAX_SMS_SEGMENTS = int(os.getenv("MAX_SMS_SEGMENTS", "3"))

# One SMS segment is 160 chars (GSM-7). We budget characters, not tokens,
# because that's what the user actually pays for / receives.
SMS_SEGMENT_LEN = 160
MAX_REPLY_CHARS = SMS_SEGMENT_LEN * MAX_SMS_SEGMENTS