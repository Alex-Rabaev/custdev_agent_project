from temporalio import activity

@activity.defn
async def send_message(chat_id: int, text: str):
    from aiogram import Bot
    import os
    from dotenv import load_dotenv

    load_dotenv()
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    print(f"[SEND_MESSAGE] Sending message to {chat_id}: {text}")
    await bot.send_message(chat_id, text)