# Telegram_Unknown_Bot

## Description
A Telegram bot that allows you to chat to unknown people. It is based on the [python-telegram-bot](https://github.com/eternnoir/pyTelegramBotAPI) library.

## Installation

1. Clone the repository: `git clone`
2. Install the requirements:
```
pip install -r requirements.txt
```
3. Create a new bot with [BotFather](https://t.me/BotFather) and copy the token.
4. Create a new file called `.env` and paste the following code:
```
BOT_TOKEN = your_token_here
```
5. Add src/ to your PYTHONPATH:
```
export PYTHONPATH="${PYTHONPATH}:/path/to/src/"
```
6. Run the bot: 
```
python3 src/main.py
```
