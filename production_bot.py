import asyncio
import aiohttp
import os
TOKEN = os.getenv("TELEGRAM_TOKEN", "8338872538:AAF3lFNXu6XNY7pL-AxJuyQkAk-cLpYnroE")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
GROQ_KEY = os.getenv("GROQ_API_KEY", "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")
OR_KEY = os.getenv("OPENROUTER_API_KEY", "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")
MM_KEY = os.getenv("MINIMAX_API_KEY", "sk-api-PGmypqVy32nn_hZLh8PIEK1JUqGkFfliuQ0Tx26vCfP1dwXLoun-9T69tWd__1vYqRNR1zlG2T4srtAJ5BatYt6hmFckWgIutX6L4a1Hzj5HhjEQ-WcMGuk")
history = {}
async def send(chat_id, text):
    async with aiohttp.ClientSession() as s:
        await s.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})
async def ai(messages):
    for key in [GROQ_KEY, OR_KEY, MM_KEY]:
        if not key: continue
        url = "https://api.groq.com/openai/v1/chat/completions" if "gsk" in key else ("https://openrouter.ai/api/v1/chat/completions" if "sk-or" in key else "https://api.minimax.chat/v1/text/chatcompletion_pro")
        model = "llama-3.3-70b-versatile" if "gsk" in key else ("meta-llama/llama-3.1-8b-instruct" if "sk-or" in key else "abab6.5s-chat")
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json={"model": model, "messages": messages, "temperature": 0.7}) as r:
                    if r.status == 200:
                        d = await r.json()
                        return d.get("choices", [{}])[0].get("message", {}).get("content", "")
        except: pass
    return "Services unavailable"
async def handle(update):
    msg = update.get("message", {})
    if not msg or "text" not in msg: return
    chat_id = msg["chat"]["id"]
    text = msg["text"]
    if text == "/start": await send(chat_id, "OpenClaw Bot Online!"); return
    if text == "/clear": history[chat_id] = []; await send(chat_id, "Cleared!"); return
    history.setdefault(chat_id, [])
    history[chat_id].append({"role": "user", "content": text})
    msgs = [{"role": "system", "content": "You are helpful."}] + history[chat_id][-6:]
    resp = await ai(msgs)
    history[chat_id].append({"role": "assistant", "content": resp})
    await send(chat_id, resp)
async def poll():
    offset = 0
    while True:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{BASE_URL}/getUpdates?timeout=30&offset={offset}") as r:
                    if r.status == 200:
                        for update in (await r.json()).get("result", []):
                            offset = update["update_id"] + 1
                            await handle(update)
        except: pass
        await asyncio.sleep(1)
print("OpenClaw Bot running...")
asyncio.run(poll())
