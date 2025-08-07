from datetime import datetime, timezone
from temporalio import activity

@activity.defn
async def save_answer(telegram_id: int, qa: dict):
    from app.database.mongo import users_collection
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {
            "$push": {"answers": qa},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )

@activity.defn
async def set_user_language(telegram_id: int, lang: str):
    from app.database.mongo import users_collection
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"language": lang}}
    )

@activity.defn
async def save_user_email(telegram_id: int, email: str):
    from app.database.mongo import users_collection
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"email": email}}
    )

@activity.defn
async def mark_survey_complete(telegram_id: int):
    from app.database.mongo import users_collection
    users_collection.update_one(
        {"telegram_id": telegram_id},
        {
            "$set": {
                "survey_completed": True,
                "survey_completed_at": datetime.now(timezone.utc)
            }
        }
    )
