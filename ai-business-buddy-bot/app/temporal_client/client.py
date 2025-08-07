from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError
import os
from app.workflows.user_onboarding import UserOnboardingWorkflow
from dotenv import load_dotenv

load_dotenv()

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS")

async def start_user_workflow(user_data: dict):
    client = await Client.connect(TEMPORAL_ADDRESS)

    try:
        await client.start_workflow(
            UserOnboardingWorkflow.run,
            user_data,
            id=f"user-onboarding-{user_data['telegram_id']}",
            task_queue="user-onboarding-task-queue"
        )
    except WorkflowAlreadyStartedError:
        print(f"⚠️ Workflow уже запущен для пользователя {user_data['telegram_id']}")


async def get_temporal_client():
    return await Client.connect(TEMPORAL_ADDRESS)