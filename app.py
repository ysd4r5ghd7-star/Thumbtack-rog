import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=15)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/test")
def test():
    send_telegram("✅ Test from server")
    return {"sent": True}

@app.post("/thumbtack/webhook")
async def thumbtack_webhook(req: Request):
    data = await req.json()
    send_telegram("📩 Thumbtack webhook received:\n" + str(data)[:3500])
    return {"received": True}
