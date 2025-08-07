from fastapi import FastAPI, Request
import uvicorn
from dotenv import load_dotenv
import os
from app.telegram.bot import bot, dp
from aiogram import types
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.telegram.handlers import router

load_dotenv()

WEBHOOK_PATH = f"/webhook/{os.getenv('TELEGRAM_BOT_TOKEN')}"
WEBHOOK_SECRET = os.getenv("TELEGRAM_BOT_TOKEN")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(f"{webhook_url}{WEBHOOK_PATH}")
        print(f"Webhook set to: {webhook_url}{WEBHOOK_PATH}")
    

    dp.include_router(router)


    yield
    
    # Shutdown
    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return JSONResponse(content={"ok": True})


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)