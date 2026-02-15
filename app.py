import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Load environment variables from Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram(text: str):
    """
    Sends a Telegram message and returns detailed status for debugging.
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
        response = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": text},
            timeout=15,
        )
    except requests.RequestException as e:
        return {"ok": False, "error": f"Request failed: {repr(e)}"}

    try:
        body = response.json()
    except Exception:
        body = {"raw": response.text}

    return {"http_status": response.status_code, "body": body}


# 🔹 Health check
@app.get("/health")
def health():
    return {"ok": True}


# 🔹 Test Telegram connection
@app.get("/test")
def test():
    return send_telegram("✅ Test from server")


# 🔹 Thumbtack webhook endpoint
@app.post("/thumbtack/webhook")
async def thumbtack_webhook(req: Request):
    data = await req.json()

    text = "📩 Thumbtack webhook received:\n" + str(data)
    if len(text) > 3500:
        text = text[:3500] + "…"

    result = send_telegram(text)

    return {"received": True, "telegram": result}
