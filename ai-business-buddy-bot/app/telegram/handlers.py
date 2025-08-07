from aiogram import Router, types, F
from aiogram.filters import CommandStart
from app.database.mongo import users_collection
from datetime import datetime, timezone
from app.temporal_client.client import start_user_workflow
from app.temporal_client.client import get_temporal_client
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.service import RPCError
from app.workflows.user_onboarding import UserOnboardingWorkflow

router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message):
    print(f"[START] Got message id: {message.message_id} from user {message.from_user.id}")
    user = {
        "telegram_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
        "language": message.from_user.language_code or "en",
        "created_at": datetime.now(timezone.utc),
        "answers": [],
        "profile": {},
        "email": None
    }

    existing = users_collection.find_one({"telegram_id": message.from_user.id})
    if not existing:
        users_collection.insert_one(user)
    else:
        users_collection.update_one(
            {"telegram_id": message.from_user.id},
            {"$set": {"last_visit": datetime.now(timezone.utc)}}
        )

    await message.answer(
        "👋 I am AI Business Buddy — your assistant for business management. "
    )

    user.pop("_id", None)

    # Запуск Temporal workflow
    await start_user_workflow(user)


@router.message(F.text)
async def handle_text_message(message: types.Message):
    telegram_id = message.from_user.id
    answer_text = message.text.strip()

    # Подключаем Temporal client
    client = await get_temporal_client()

    try:
        # Получаем хендл workflow по ID
        handle = client.get_workflow_handle(f"user-onboarding-{telegram_id}")
        
        # Отправляем сигнал в workflow
        await handle.signal(UserOnboardingWorkflow.submit_answer, answer_text)
        await message.answer("✅")
    except RPCError as e:
        if "workflow execution already completed" in str(e):
            await message.answer("⚠️ Опрос уже завершён. Напиши /start, чтобы пройти заново.")
        else:
            # логирование или fallback
            await message.answer("❌ Произошла ошибка. Попробуйте позже.")
            raise