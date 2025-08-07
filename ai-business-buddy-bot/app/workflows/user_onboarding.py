from temporalio import workflow
from datetime import timedelta
from app.workflows.activities import messaging, db, llm

@workflow.defn
class UserOnboardingWorkflow:
    @workflow.run
    async def run(self, user: dict):
        self.telegram_id = user["telegram_id"]
        self.answers = []
        self.profile = {}
        self.language = "en"

        welcome_msg = await workflow.execute_activity(
            llm.generate_welcome_message,
            args=[str(self.telegram_id)],
            schedule_to_close_timeout=timedelta(seconds=15),
        )

        await workflow.execute_activity(
            messaging.send_message,
            args=[int(self.telegram_id), welcome_msg],
            schedule_to_close_timeout=timedelta(seconds=15),
        )

        await workflow.wait_condition(lambda: hasattr(self, "first_answer"))

        self.language = await workflow.execute_activity(
            llm.detect_language,
            args=[self.first_answer],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        await workflow.execute_activity(
            db.set_user_language,
            args=[int(self.telegram_id), self.language],
            schedule_to_close_timeout=timedelta(seconds=5),
        )

        self.finished = False
        while not self.finished:
            question_data = await workflow.execute_activity(
                llm.get_next_question,
                args=[self.profile, [a["answer"] for a in self.answers], self.language],
                schedule_to_close_timeout=timedelta(seconds=60),
            )

            question_text = question_data["question"]

            await workflow.execute_activity(
                messaging.send_message,
                args=[int(self.telegram_id), question_text],
                schedule_to_close_timeout=timedelta(seconds=15),
            )

            await workflow.wait_condition(lambda: hasattr(self, "last_answer"))

            answer = self.last_answer
            del self.last_answer

            if question_data.get("is_email"):
                await workflow.execute_activity(
                    db.save_user_email,
                    args=[int(self.telegram_id), answer],
                    schedule_to_close_timeout=timedelta(seconds=10),
                )
                # Для email тоже добавляем в ответы, чтобы правильно считать количество
                self.answers.append({"question": question_text, "answer": answer})

            else:
                await workflow.execute_activity(
                    db.save_answer,
                    args=[int(self.telegram_id), {"question": question_text, "answer": answer}],
                    schedule_to_close_timeout=timedelta(seconds=15),
                )
                self.answers.append({"question": question_text, "answer": answer})

            if question_data.get("is_final"):
                self.finished = True
                await workflow.execute_activity(
                    db.mark_survey_complete,
                    args=[int(self.telegram_id)],
                    schedule_to_close_timeout=timedelta(seconds=5),
                )
                
                # Отправляем финальное сообщение
                final_message = """🎉 Спасибо за прохождение опроса!

На основе ваших ответов я подготовлю персонализированный анализ вашего бизнеса и рекомендации по улучшению.

В ближайшее время вы получите:
• Анализ ключевых вызовов вашего бизнеса
• Персонализированные рекомендации
• Информацию о том, как AI Business Buddy может помочь решить ваши задачи

Просто напишите мне, если у вас есть вопросы или нужна помощь!"""
                await workflow.execute_activity(
                    messaging.send_message,
                    args=[int(self.telegram_id), final_message],
                    schedule_to_close_timeout=timedelta(seconds=15),
                )

    @workflow.signal
    async def submit_answer(self, answer: str):
        if not hasattr(self, "first_answer"):
            self.first_answer = answer
        else:
            self.last_answer = answer