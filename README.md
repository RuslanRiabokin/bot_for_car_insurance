# Car Insurance Assistant Telegram Bot

## Overview

This is a simple AI-powered Telegram bot that guides users through the process of purchasing car insurance. The bot interacts conversationally, collects necessary documents, verifies extracted data, and issues a dummy insurance policy for the user.

## Features

### 1. Bot Initialization

* When a user starts the bot, it introduces itself and explains that it helps users buy car insurance.

### 2. Document Submission

* The bot prompts the user to upload photos of:
  * Their passport
  * Their vehicle identification document (technical passport)

### 3. Data Extraction (Mocked or via Mindee API)

* The bot extracts user data from the submitted images.
* Extracted data is shown to the user for confirmation.

### 4. Data Confirmation Flow

* If the user rejects the data, they are asked to re-upload the image.
* The bot repeats the extraction and confirmation steps.
* Once the user confirms the data is correct, the bot proceeds to pricing.

### 5. Price Quotation

* The bot informs the user that the fixed price for insurance is **100 USD**.
* If the user declines, the bot politely reiterates that this is the only available price.
* If the user agrees, the bot proceeds to policy generation.

### 6. Insurance Policy Generation

* The bot generates a dummy insurance policy PDF.
* This document is sent to the user as proof of purchase.

### 7. AI-Driven Conversations

* All conversations simulate intelligent dialogue using OpenAI to make the interaction feel natural and user-friendly.

## Tech Stack

* Python 3.11
* Telegram Bot API (via [aiogram](https://docs.aiogram.dev))
* Mindee API (or mock function for OCR simulation)
* OpenAI API (for natural conversation and document generation)
* PDF generation (using template-based output)

## Project Structure

```

bot\_for\_car\_insurance/
├── services/
│   ├── pdf\_generator.py
│   └── DejaVuSans.ttf
├── ai\_handlers/
├── ai\_provider.py
├── config.py
├── .env
├── .gitignore
├── bot.py                  # Entry point
├── requirements.txt
└── README.md

````

## How to Run (Locally)

### 1. Clone the repository

```bash
git clone https://github.com/RuslanRiabokin/bot_for_car_insurance.git
cd bot_for_car_insurance
````

### 2. Set up the `.env` file

Create a `.env` file in the root directory and add the following variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token

# === Azure OpenAI Configuration ===
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_ID=gpt-35-turbo

# === Webhook Configuration ===
BASE_WEBHOOK_URL=https://yourdomain.ngrok-free.app
WEBHOOK_SECRET=my_key
WEBHOOK_PORT=5000
WEBHOOK_PATH=/webhook
WEB_SERVER_HOST=0.0.0.0
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the bot

```bash
python bot.py
```

---

## 🐳 How to Run with Docker

You can run this bot inside a Docker container.

### 1. Build the Docker image

```bash
docker build -t riabokin/car-insurance-bot:latest .
```

### 2. Run the container

```bash
docker run --env-file .env -p 8000:8000 riabokin/car-insurance-bot:latest
```

> Ensure `.env` contains all required environment variables (see above).

### 3. Push to Docker Hub (optional)

If you want to publish the image:

```bash
docker login
docker push riabokin/car-insurance-bot:latest
```

---

## License

This project is provided for educational and demonstration purposes.

```


