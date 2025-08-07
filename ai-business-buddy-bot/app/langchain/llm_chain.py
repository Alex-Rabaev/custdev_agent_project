import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable

from langchain_mongodb import MongoDBChatMessageHistory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from app.database.mongo import mongo_client

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Промпт
prompt = ChatPromptTemplate.from_messages([
    ("system", "You're a helpful assistant for small business owners. Respond in the user's language."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# LLM
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o",
)

# Цепочка
chain: Runnable = prompt | llm

# Конструктор истории
def get_conversation_chain(session_id: str) -> RunnableWithMessageHistory:
    return RunnableWithMessageHistory(
        chain,
        lambda _: MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=MONGO_URI,
            database_name="business_buddy",
            collection_name="langchain_chat_history"
        ),
        input_messages_key="input",
        history_messages_key="history",
    )
