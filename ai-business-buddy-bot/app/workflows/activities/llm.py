from temporalio import activity
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


@activity.defn
async def generate_welcome_message(user_id: str) -> str:
    from app.langchain.llm_chain import get_conversation_chain 
    chain = get_conversation_chain(session_id=user_id)
    response = chain.invoke(
        {"input": (
            "Please greet the user in a friendly tone in English. "
            "Explain what kind of assistant you are and ask the user to reply in the language they'd like to continue in."
        )},
        config={"configurable": {"session_id": user_id}}
    )
    return response.content


@activity.defn
async def detect_language(text: str) -> str:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a language detector."},
            {"role": "user", "content": f"What language the user want to use? Return ISO code only (e.g., en, ru, he): {text}"}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


@activity.defn
async def get_next_question(profile: dict, answers: list[str], language: str) -> dict:
    from app.langchain.llm_chain import get_conversation_chain
    from app.utils.prompt_loader import PROMPT_TEXT
    
    chain = get_conversation_chain(session_id="static_for_now")

    # Если уже задано 21 вопрос, завершаем опрос
    if len(answers) >= 21:
        return {
            "question": "Спасибо за прохождение полного опроса! Теперь я лучше понимаю ваш бизнес и готов помочь вам с любыми вопросами.",
            "is_final": True,
            "is_email": False
        }

    # Если это последний вопрос (21-й), запрашиваем email
    if len(answers) >= 20:
        return {
            "question": "Пожалуйста, укажите ваш email для получения дополнительных материалов и уведомлений о новых возможностях для вашего бизнеса.",
            "is_final": True,
            "is_email": True
        }

    # Для первых вопросов используем короткий промпт
    if len(answers) < 3:
        context = f"""Ты — AI Business Buddy. Задай следующий вопрос из анкеты для понимания бизнеса пользователя.

Язык общения: {language}. 
Профиль пользователя: {profile}.
Количество уже заданных вопросов: {len(answers)}.

Ответы пользователя:
"""
        for idx, ans in enumerate(answers):
            context += f"Вопрос {idx+1}: {ans}\n"
        
        context += f"""
Задай следующий вопросы из списка по одному: 
В какой нише работает пользователь? 
Онлайн бизнес или есть физическая точка? 
Сколько у него человек в команде? 

Используй язык пользователя ({language}) и по результатам заполни его профиль.
"""
    else:
        # Для остальных вопросов используем полный промпт
        context = f"""Ты — AI Business Buddy. Используй следующий промпт для работы:

{PROMPT_TEXT}

Язык общения: {language}. 
Профиль пользователя: {profile}.
Количество уже заданных вопросов: {len(answers)}.

Ответы пользователя:
"""
        for idx, ans in enumerate(answers):
            context += f"Вопрос {idx+1}: {ans}\n"
        
        context += f"""
На основе промпта и предыдущих ответов, задай следующий вопрос из анкеты (вопрос номер {len(answers) + 1}).
Адаптируй вопрос под профиль пользователя и пропускай нерелевантные вопросы.
Используй язык пользователя ({language}).
"""

    try:
        response = chain.invoke(
            {"input": context},
            config={"configurable": {"session_id": "static_for_now"}}
        )
        
        return {"question": response.content, "is_final": False, "is_email": False}
    except Exception as e:
        # Fallback в случае ошибки
        fallback_questions = [
            "ERROR",
            "ERROR",
            "ERROR"
        ]
        
        question_index = min(len(answers), len(fallback_questions) - 1)
        return {
            "question": fallback_questions[question_index],
            "is_final": len(answers) >= 4,
            "is_email": len(answers) >= 4
        }