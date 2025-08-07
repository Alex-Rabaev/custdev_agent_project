# Диаграммы последовательности AI Business Buddy Bot

## 🔄 Диаграмма последовательности: Начало опроса (/start)

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram API
    participant FH as FastAPI Handler
    participant TC as Temporal Client
    participant WF as UserOnboarding Workflow
    participant LLM as LLM Activity
    participant OA as OpenAI API
    participant MSG as Messaging Activity
    participant DB as Database Activity
    participant MG as MongoDB

    U->>TG: /start
    TG->>FH: webhook
    FH->>DB: save_user_to_db()
    FH->>TC: start_user_workflow(user_data)
    TC->>WF: UserOnboardingWorkflow.run()
    
    WF->>LLM: generate_welcome_message()
    LLM->>OA: OpenAI API call
    OA-->>LLM: welcome message
    LLM-->>WF: welcome text
    
    WF->>MSG: send_message(chat_id, welcome_text)
    MSG->>TG: bot.send_message()
    TG-->>U: welcome message
    
    Note over WF: Wait for first answer
```

## 🔄 Диаграмма последовательности: Обработка ответа пользователя

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram API
    participant FH as FastAPI Handler
    participant WF as UserOnboarding Workflow
    participant LLM as LLM Activity
    participant OA as OpenAI API
    participant MSG as Messaging Activity
    participant DB as Database Activity
    participant MG as MongoDB

    U->>TG: text message
    TG->>FH: webhook
    FH->>WF: submit_answer(answer)
    
    Note over WF: First answer processing
    WF->>LLM: detect_language(answer)
    LLM->>OA: OpenAI API call
    OA-->>LLM: language code
    LLM-->>WF: detected language
    
    WF->>DB: set_user_language(lang)
    DB->>MG: update user document
    MG-->>DB: confirmation
    DB-->>WF: done
    
    loop Question Loop
        WF->>LLM: get_next_question(profile, answers, lang)
        LLM->>OA: OpenAI API call
        OA-->>LLM: next question
        LLM-->>WF: question_data
        
        WF->>MSG: send_message(chat_id, question)
        MSG->>TG: bot.send_message()
        TG-->>U: question
        
        Note over WF: Wait for answer
        U->>TG: answer
        TG->>FH: webhook
        FH->>WF: submit_answer(answer)
        
        WF->>DB: save_answer(telegram_id, qa)
        DB->>MG: update user document
        MG-->>DB: confirmation
        DB-->>WF: done
    end
    
    Note over WF: Final question (email)
    WF->>DB: save_user_email(telegram_id, email)
    WF->>DB: mark_survey_complete(telegram_id)
    WF->>MSG: send_message(final_message)
    MSG->>TG: bot.send_message()
    TG-->>U: completion message
```

## 🔄 Диаграмма последовательности: Проблемный сценарий (без /start)

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram API
    participant FH as FastAPI Handler
    participant TC as Temporal Client
    participant WF as UserOnboarding Workflow

    U->>TG: text message (without /start)
    TG->>FH: webhook
    FH->>TC: get_workflow_handle(user_id)
    
    alt Workflow exists
        TC-->>FH: workflow handle
        FH->>WF: submit_answer(answer)
        Note over WF: May fail if workflow in wrong state
    else Workflow not found
        TC-->>FH: RPCError: workflow not found
        FH-->>U: "❌ Произошла ошибка. Попробуйте позже."
    else Workflow completed
        TC-->>FH: RPCError: workflow already completed
        FH-->>U: "⚠️ Опрос уже завершён. Напиши /start, чтобы пройти заново."
    end
```

## 🔄 Диаграмма последовательности: Определение языка

```mermaid
sequenceDiagram
    participant WF as UserOnboarding Workflow
    participant LLM as LLM Activity
    participant OA as OpenAI API
    participant DB as Database Activity
    participant MG as MongoDB

    Note over WF: After first user answer
    WF->>LLM: detect_language(first_answer)
    
    LLM->>OA: OpenAI API call
    Note over OA: System: "You are a language detector."
    Note over OA: User: "What language the user want to use? Return ISO code only (e.g., en, ru, he): {text}"
    
    OA-->>LLM: language code (e.g., "ru")
    LLM-->>WF: detected_language
    
    WF->>DB: set_user_language(telegram_id, language)
    DB->>MG: update user document
    Note over MG: {"$set": {"language": "ru"}}
    MG-->>DB: confirmation
    DB-->>WF: done
    
    Note over WF: All subsequent questions use detected language
```

## 🔄 Диаграмма последовательности: Генерация следующего вопроса

```mermaid
sequenceDiagram
    participant WF as UserOnboarding Workflow
    participant LLM as LLM Activity
    participant LC as LangChain
    participant OA as OpenAI API
    participant PL as Prompt Loader

    WF->>LLM: get_next_question(profile, answers, language)
    
    LLM->>PL: load_prompt()
    PL-->>LLM: prompt_text
    
    LLM->>LC: get_conversation_chain()
    LC-->>LLM: chain
    
    alt First 3 questions
        Note over LLM: Use short context for basic profile questions
        LLM->>OA: OpenAI API call with short prompt
    else Questions 4-20
        Note over LLM: Use full prompt with business questions
        LLM->>OA: OpenAI API call with full prompt
    else Question 21 (final)
        Note over LLM: Return completion message
        LLM-->>WF: {"question": "completion message", "is_final": true}
    end
    
    OA-->>LLM: generated question
    LLM-->>WF: question_data
    
    Note over WF: question_data contains:
    Note over WF: - question: text
    Note over WF: - is_final: boolean
    Note over WF: - is_email: boolean
```

## 🔄 Диаграмма последовательности: Сохранение данных

```mermaid
sequenceDiagram
    participant WF as UserOnboarding Workflow
    participant DB as Database Activity
    participant MG as MongoDB

    Note over WF: After each answer
    
    alt Regular answer
        WF->>DB: save_answer(telegram_id, qa)
        DB->>MG: update user document
        Note over MG: {"$push": {"answers": qa}, "$set": {"updated_at": timestamp}}
    else Email answer
        WF->>DB: save_user_email(telegram_id, email)
        DB->>MG: update user document
        Note over MG: {"$set": {"email": email}}
    else Survey completion
        WF->>DB: mark_survey_complete(telegram_id)
        DB->>MG: update user document
        Note over MG: {"$set": {"survey_completed": true, "survey_completed_at": timestamp}}
    end
    
    MG-->>DB: confirmation
    DB-->>WF: done
```

## 🔄 Диаграмма последовательности: Обработка ошибок

```mermaid
sequenceDiagram
    participant U as User
    participant TG as Telegram API
    participant FH as FastAPI Handler
    participant TC as Temporal Client
    participant WF as UserOnboarding Workflow
    participant LLM as LLM Activity
    participant OA as OpenAI API

    U->>TG: text message
    TG->>FH: webhook
    
    FH->>TC: get_workflow_handle(user_id)
    
    alt Temporal connection error
        TC-->>FH: ConnectionError
        FH-->>U: "❌ Сервис временно недоступен. Попробуйте позже."
    else Workflow not found
        TC-->>FH: RPCError: workflow not found
        FH-->>U: "⚠️ Начните с команды /start для прохождения опроса."
    else Workflow completed
        TC-->>FH: RPCError: workflow already completed
        FH-->>U: "⚠️ Опрос уже завершён. Напиши /start, чтобы пройти заново."
    else OpenAI API error
        FH->>WF: submit_answer(answer)
        WF->>LLM: get_next_question()
        LLM->>OA: OpenAI API call
        OA-->>LLM: APIError
        LLM-->>WF: fallback question
        WF->>U: fallback message
    else Database error
        WF->>DB: save_answer()
        DB-->>WF: DatabaseError
        WF-->>U: "❌ Ошибка сохранения. Попробуйте позже."
    end
```

## 📊 Статистика компонентов

### Время выполнения (примерные значения):
- **Telegram API**: 100-500ms
- **OpenAI API**: 1-3s
- **MongoDB**: 10-50ms
- **Temporal operations**: 50-200ms
- **LangChain processing**: 500ms-1s

### Частота вызовов:
- **OpenAI API**: ~3-4 calls per user session
- **MongoDB**: ~25-30 operations per user session
- **Telegram API**: ~25-30 calls per user session
- **Temporal signals**: ~20-25 per user session

### Потенциальные узкие места:
1. **OpenAI API latency**: Может замедлить весь процесс
2. **Temporal server**: Центральная точка отказа
3. **MongoDB connection**: При высокой нагрузке
4. **Webhook processing**: FastAPI может стать узким местом 