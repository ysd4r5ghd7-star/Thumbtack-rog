import os
import json
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Render Environment Variables (ДОЛЖНЫ БЫТЬ ИМЕННО ТАК, С БОЛЬШИХ БУКВ)
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


def pretty_payload(data) -> str:
    """
    Make payload readable for Telegram.
    """
    try:
        s = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        s = str(data)

    # Telegram message length safety
    if len(s) > 3200:
        s = s[:3200] + "\n…(truncated)"
    return s


@app.get("/")
def root():
    return {"service": "thumbtack-rog", "status": "running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/test")
def test():
    # Shows Telegram response (200/401/403 etc.)
    return send_telegram("✅ Test from server")


@app.get("/ping")
def ping():
    # Quick test: server → Telegram
    return send_telegram("🔔 Ping OK — server → Telegram работает")


@app.post("/thumbtack/webhook")
async def thumbtack_webhook(req: Request):
    """
    Thumbtack will POST webhook events here.
    We forward payload to Telegram for now.
    """
    data = await req.json()

    # Try to extract common useful fields (if present)
    event_type = data.get("type") or data.get("eventType") or "unknown"
    negotiation_id = (
        data.get("negotiationID")
        or data.get("negotiationId")
        or (data.get("negotiation") or {}).get("id")
        or (data.get("data") or {}).get("negotiationID")
        or (data.get("data") or {}).get("negotiationId")
    )

    header = f"📩 Thumbtack webhook\nType: {event_type}"
    if negotiation_id:
        header += f"\nNegotiation: {negotiation_id}"

    payload_text = pretty_payload(data)
    msg = f"{header}\n\n{payload_text}"

    tg_result = send_telegram(msg)
    return {"received": True, "telegram": tg_result}
