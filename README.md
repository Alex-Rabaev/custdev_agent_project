# AI Business Buddy Bot

An intelligent Telegram bot designed to help small business owners streamline customer management, appointment scheduling, communication, CRM, and marketing through conversational AI.

## 🚀 Overview

AI Business Buddy is a customer development agent that conducts personalized surveys with business owners to understand their specific needs and pain points. The bot uses advanced AI to adapt questions based on user responses and provides tailored recommendations for business solutions.

## ✨ Key Features

- **Intelligent Survey System**: Conducts adaptive 21-question surveys based on user responses
- **Multi-language Support**: Automatically detects and responds in the user's preferred language
- **Personalized Recommendations**: Analyzes user responses to provide customized business solutions
- **Temporal Workflow Management**: Robust state management using Temporal for reliable conversation flows
- **MongoDB Integration**: Persistent user data storage and profile management
- **Telegram Integration**: Seamless messaging through Telegram's API

## 🏗️ Architecture

The project is built with a modern microservices architecture:

- **FastAPI**: Web framework for handling Telegram webhooks
- **Temporal**: Workflow orchestration for managing conversation states
- **MongoDB**: Database for user profiles and survey responses
- **aiogram**: Telegram bot framework
- **LangChain**: AI/LLM integration for intelligent responses

## 📁 Project Structure

```
ai-business-buddy-bot/
├── app/
│   ├── database/
│   │   └── mongo.py          # MongoDB connection and operations
│   ├── langchain/
│   │   └── llm_chain.py      # AI/LLM integration
│   ├── telegram/
│   │   ├── bot.py            # Telegram bot setup
│   │   └── handlers.py       # Message handlers
│   ├── temporal_client/
│   │   └── client.py         # Temporal workflow client
│   ├── utils/
│   │   ├── prompt_loader.py  # AI prompt management
│   │   └── prompt.txt        # Core AI prompts
│   ├── workflows/
│   │   ├── activities/
│   │   │   ├── db.py         # Database activities
│   │   │   ├── llm.py        # AI/LLM activities
│   │   │   └── messaging.py  # Messaging activities
│   │   └── user_onboarding.py # Main user onboarding workflow
│   ├── main.py               # FastAPI application entry point
│   └── worker.py             # Temporal worker
└── requirements.txt          # Python dependencies
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- Temporal server
- Telegram Bot Token

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd custdev_agent_project
   ```

2. **Set up virtual environment**
   ```bash
   cd ai-business-buddy-bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file with the following variables:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   WEBHOOK_URL=your_webhook_url
   MONGODB_URI=your_mongodb_connection_string
   TEMPORAL_HOST=localhost:7233
   ```

5. **Start the application**
   ```bash
   python -m app.main
   ```

## 🔧 Configuration

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `WEBHOOK_URL`: Public URL for Telegram webhooks
- `MONGODB_URI`: MongoDB connection string
- `TEMPORAL_HOST`: Temporal server address

### Temporal Workflow

The bot uses Temporal workflows to manage conversation state:
- **UserOnboardingWorkflow**: Manages the entire user onboarding process
- **Activities**: Handle database operations, AI interactions, and messaging

## 📊 Survey Flow

1. **Welcome & Language Detection**: Greets user and detects preferred language
2. **Business Profile**: Collects basic business information (niche, team size, etc.)
3. **Adaptive Questions**: Presents relevant questions based on user responses
4. **Analysis & Recommendations**: Analyzes responses and provides personalized solutions
5. **Email Collection**: Offers early access in exchange for email address

## 🤖 AI Integration

The bot uses advanced AI prompts to:
- Generate personalized welcome messages
- Adapt survey questions based on user responses
- Analyze user pain points and priorities
- Provide tailored business recommendations

## 📈 Business Value

- **Customer Development**: Gathers detailed insights about target market needs
- **Lead Generation**: Collects qualified leads through engaging conversations
- **Product Validation**: Validates product-market fit through real user feedback
- **Market Research**: Understands customer pain points and preferences

## 🚀 Deployment

The application is designed to be deployed as a FastAPI service with:
- Webhook support for Telegram integration
- Health check endpoints
- Proper lifecycle management
- Scalable architecture

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]
