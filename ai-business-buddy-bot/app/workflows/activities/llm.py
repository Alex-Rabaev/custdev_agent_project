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
            {"role": "user", "content": f"What language is this? Return ISO code only (e.g., en, ru, he): {text}"}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


@activity.defn
async def get_next_question(profile: dict, answers: list[str], language: str) -> dict:
    from app.langchain.llm_chain import get_conversation_chain
    chain = get_conversation_chain(session_id="static_for_now")

    context = f"Язык общения: {language}. Профиль пользователя: {profile}.\n"
    for idx, ans in enumerate(answers):
        context += f"Ответ на вопрос {idx+1}: {ans}\n"
    context += "Какой следующий вопрос стоит задать пользователю?"

    response = chain.invoke(
        {"input": context},
        config={"configurable": {"session_id": "static_for_now"}}
    )
    return {"question": response.content, "is_final": False, "is_email": False}