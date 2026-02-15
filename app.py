import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram(text: str):
    """
    Sends a Telegram message and returns detailed status so we can debug issues.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return {
            "ok": False,
            "error": "Missing TELEGRAM_TOKEN or CHAT_ID environment variables",
            "has_token": bool(TELEGRAM_TOKEN),
            "has_chat_id": bool(CHAT_ID),
        }

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": text},
            timeout=15,
        )
    except requests.RequestException as e:
        return {"ok": False, "error": f"Request failed: {repr(e)}"}

    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}

    return {"http_status": r.status_code, "body": body}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/test")
def test():
    # This endpoint will show you EXACTLY what Telegram returns (401/400/403 etc.)
    return send_telegram("✅ Test from server")


@app.post("/thumbtack/webhook")
async def thumbtack_webhook(req: Request):
    """
    Thumbtack will POST webhook events here.
    For now we forward the raw payload to Telegram.
    Later we’ll format it nicely and add auto-replies.
    """
    data = await req.json()

    # Keep message length safe for Telegram
    text = "📩 Thumbtack webhook received:\n" + str(data)
    if len(text) > 3500:
        text = text[:3500] + "…"

    result = send_telegram(text)

    # Return something useful for debugging
    return {"received": True, "telegram": result}
