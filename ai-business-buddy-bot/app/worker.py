import asyncio
import os
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from app.workflows.user_onboarding import UserOnboardingWorkflow
from app.workflows.activities import messaging, db, llm

load_dotenv()

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS")


async def main():
    client = await Client.connect(TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        task_queue="user-onboarding-task-queue",
        workflows=[UserOnboardingWorkflow],
        activities=[
            messaging.send_message,
            db.save_answer,
            db.set_user_language,
            db.save_user_email,
            db.mark_survey_complete,
            llm.generate_welcome_message,
            llm.detect_language,
            llm.get_next_question,
        ],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())