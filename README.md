# Kaduda AI — SMS-based AI assistant (MVP)

Text a question, get an AI answer back by SMS. No smartphone, no data
bundle, no app required — just basic phone + network signal.

## How it works

```
Person texts a number
        ↓
Africa's Talking receives it, forwards to your /sms webhook
        ↓
main.py routes it: known command? (commands.py) → else → AI (ai.py)
        ↓
Reply sent back via Africa's Talking Send SMS API (sms.py)
```

Files:
- `main.py` — the FastAPI webhook Africa's Talking calls
- `ai.py` — talks to the LLM, keeps replies SMS-length
- `sms.py` — sends the reply SMS via Africa's Talking
- `session.py` — remembers the last few messages per phone number (in-memory — swap for Redis before real launch)
- `commands.py` — where you'll plug in specialized commands later (SACCO balance checks, farming prices, etc.) without touching the rest of the app
- `config.py` — reads your `.env`

## 1. Run it locally (free, ~10 minutes)

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env: add your ANTHROPIC_API_KEY (get a free-tier key at console.anthropic.com)
uvicorn main:app --reload
```

Simulate an inbound SMS without a real phone:
```bash
curl -X POST http://localhost:8000/sms \
  -d "from=+254700000000" -d "to=KADUDA" -d "text=What is compound interest?"
```
Check your terminal — you'll see the AI reply logged (real send is skipped in sandbox mode until Africa's Talking is wired up below).

## 2. Wire up Africa's Talking (free sandbox, no card needed)

1. Sign up at https://account.africastalking.com — creates a free **Sandbox** app automatically.
2. Get your sandbox `username` (always `sandbox`) and `API key` from the dashboard → put them in `.env` as `AT_USERNAME` / `AT_API_KEY`.
3. In the sandbox dashboard, under **SMS → Simulator**, you can send test messages to your app and see replies — this is how you demo it to yourself or a pilot SACCO before spending anything.
4. Africa's Talking needs to reach your webhook, so it must be a public URL — see deployment below. Set it under sandbox app settings → **Callback URL** → `https://your-deployed-url.com/sms`.

Going live later (real shortcode, real phones) just means switching from the sandbox app to a paid production app in the same dashboard — no code changes needed.

## 3. Deploy for free

**Render** (recommended, genuinely free web service tier):
1. Push this folder to a GitHub repo.
2. On render.com → New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add your `.env` values under Render's Environment tab (never commit `.env` itself).
6. Copy the resulting `https://your-app.onrender.com` URL into Africa's Talking's callback URL setting.

Railway works the same way if you prefer it.

## 4. What to build next (in order)

1. Test it yourself via the AT simulator until replies feel right — tune `SYSTEM_PROMPT` in `ai.py`.
2. Get 5-10 people (friends, family) to text it for a week. Watch what they ask — that tells you which vertical to specialize into.
3. When ready to specialize (e.g. SACCO members), add commands in `commands.py` — e.g. a `BAL` command that queries a real system — without touching the webhook or AI code.
4. Move `session.py` from in-memory to Redis/Postgres before any real launch — in-memory state disappears on every restart and doesn't scale past one server process.

## Cost reality check

This is free to build and free to test in sandbox. Once live: Africa's Talking charges per SMS sent (both inbound delivery to you and your outbound reply), and the LLM API charges per request. Neither is large per-message, but at volume it's real money — that's what your monetization model (subscription, per-query billing, or institutional licensing) needs to cover.
