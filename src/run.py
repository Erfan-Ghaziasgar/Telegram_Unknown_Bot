import os

import emoji
import telebot
from dotenv import load_dotenv
from loguru import logger

from src.bot import bot
from src.constants import KEYBOARDS, KEYS
from src.filters import IsAdmin
from src.utils.io import read_json, write_json
from src.db import db


class Bot:
    def __init__(self, telebot: telebot.TeleBot):
        '''
        Initialize bot
        '''
        self.bot = telebot
        self.bot.add_custom_filter(IsAdmin())
        self.handler()

    def handler(self):
        '''
        Handler for bot
        '''
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            '''
            Send welcome message
            :param message: message
            '''
            self.send_message(
                message.chat.id,
                f"Howdy, how are you doing <strong>{message.from_user.first_name}</strong> ?",
                reply_markup=KEYBOARDS.main
                )
            db.users.update_one(
                {"_id": message.chat.id},
                {"$set": message.json},
                upsert=True
                )

        @self.bot.message_handler(regexp=KEYS.random_connect)
        def random_connect(message):
            '''
            Random connect
            :param message: message
            '''
            self.send_message(message.chat.id, "Random connect...")


        @self.bot.message_handler(is_chat_admin=True)
        def admin_of_group(message):
            self.send_message(message.chat.id, "You are admin of this group", reply_markup=KEYBOARDS.settings)


        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            '''
            Echo all messages
            :param message: message
            '''
            # write_json(message.json, DATA_DIR / "messages.json")
            self.send_message(message.chat.id, message.text)


    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        '''
        Send message
        :param message: message
        '''
        if emojize:
            text = emoji.emojize(text)

        self.bot.send_message(chat_id, text,
                              reply_markup=reply_markup)

    def run(self):
        logger.info("Bot running...")
        self.bot.infinity_polling()


if __name__ == '__main__':
    logger.info("Bot started")
    bot = Bot(telebot=bot)
    bot.run()
