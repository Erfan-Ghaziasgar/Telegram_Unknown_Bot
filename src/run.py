import telebot
from loguru import logger

from src.bot import bot
from src.constants import CONTENT_TYPE_MAPPING, KEYBOARDS, KEYS, STATES, COMBINED_PATTERN
from src.db import db
from src.utils.utils import send_message


class Bot:
    def __init__(self, telebot: telebot.TeleBot):
        """
        Initialize bot.
        """
        self.bot = telebot
        self.db = db
        self.handler()

    def handler(self):
        """
        Handler for bot.
        """
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self._handle_welcome(message)

        @self.bot.message_handler(regexp=COMBINED_PATTERN)
        def send_help(message):
            self._handle_help(message)

        @self.bot.message_handler(regexp=KEYS.random_connect)
        def random_connect(message):
            self._handle_random_connect(message)

        @self.bot.message_handler(regexp=KEYS.exit)
        def exit(message):
            self._handle_exit(message)

        @self.bot.message_handler(content_types=CONTENT_TYPE_MAPPING.keys())
        def handle_content(message):
            self._forward_content_to_connected_user(message)

    def _handle_welcome(self, message):
        """
        Handle the welcome message and user initialization.
        """
        send_message(
            self,
            message.chat.id,
            f"👋 Howdy, how are you doing <strong>{message.from_user.first_name}</strong> ?",
            reply_markup=KEYBOARDS.main
        )
        self._upsert_user(message)
        self._update_user_state(message.chat.id, STATES.idle)

    def _handle_help(self, message):
        """
        Handle the help command.
        """
        send_message(
            self,
            message.chat.id,
            "This is a simple bot that allows you to connect to random users and chat with them.\n\n"
            "To connect to a random user, use the /random_connect command.\n\n"
            "To exit a chat, use the /exit command.\n\n"
            "To exit the queue, use the /exit command.\n\n"
            "To get this message again, use the /help command.\n\n"
            "To start over, use the /start command.\n\n"
            "To get the bot's source code, visit:\n"
            "https://github.com/Erfan-Ghaziasgar/Telegram_Unknown_Bot",
            reply_markup=KEYBOARDS.main
        )

    def _handle_random_connect(self, message):
        """
        Handle the random connect command.
        """
        send_message(self, message.chat.id,
                     "You are connecting to random user...",
                     reply_markup=KEYBOARDS.exit)
        self._update_user_state(message.chat.id, STATES.random_connect)
        other_user = self._find_user_with_state(STATES.random_connect,
                                                message.chat.id)

        if not other_user:
            return

        # Update the state of both users to 'connect'
        self._update_user_state(message.chat.id, STATES.connect)
        self._update_user_state(other_user.get("_id"), STATES.connect)

        # Update the 'connect_to' field of both users
        self.db.users.update_one(
            {"_id": other_user.get("_id")},
            {"$set": {"connect_to": message.chat.id}}
        )
        self.db.users.update_one(
            {"_id": message.chat.id},
            {"$set": {"connect_to": other_user.get("_id")}}
        )

        # Echo connection message to both users
        send_message(self, message.chat.id,
                     f"Connected to {other_user.get('_id')} Say Hi to start chatting",
                     reply_markup=KEYBOARDS.exit)
        send_message(self, other_user.get("_id"),
                     f"Connected to {message.chat.id} Say Hi to start chatting",
                     reply_markup=KEYBOARDS.exit)

    def _handle_exit(self, message):
        """
        Handle the exit command.
        """
        # Exit handling logic
        user = self._get_user_from_db(message.chat.id)
        if self._user_state_is_connect(user):
            send_message(self, message.chat.id,
                         "You have left the chat",
                         reply_markup=KEYBOARDS.main
                         )
            send_message(self, user.get("connect_to"), "Your chat partner has left the chat",
                         reply_markup=KEYBOARDS.main
                         )
            self._update_user_state(user.get("connect_to"), STATES.idle)
            self._update_user_state(message.chat.id, STATES.idle)
            self._set_None_connected_to(user.get("connect_to"))
            self._set_None_connected_to(message.chat.id)

        elif user.get("state") == STATES.random_connect:
            send_message(self, message.chat.id,
                         "You have left the queue",
                         reply_markup=KEYBOARDS.main
                         )
            self._update_user_state(message.chat.id, STATES.idle)
            self._set_None_connected_to(message.chat.id)

    # private helper methods for DB operations
    def _get_user_from_db(self, chat_id):
        """Retrieve a user from the database using their chat ID."""
        return self.db.users.find_one({"_id": chat_id})

    def _user_state_is_connect(self, user):
        """Check if the user's state is 'connect'."""
        return user.get('state') == STATES.connect

    def _forward_content_to_connected_user(self, message):
        """
        Forward content based on its type to the connected user.
        """
        user = self._get_user_from_db(message.chat.id)
        if not self._user_state_is_connect(user):
            return

        connect_to = user.get('connect_to')
        if not connect_to:
            return

        send_method_name = CONTENT_TYPE_MAPPING.get(message.content_type)
        if not send_method_name:
            return  # Unsupported content type

        send_method = getattr(self.bot, send_method_name)

        if message.content_type == 'photo':
            send_method(connect_to, message.photo[-1].file_id)  # using highest resolution
        elif message.content_type == 'text':
            send_method(connect_to, message.text)
            self._insert_message(message, connect_to)
        else:
            file_id = getattr(message, message.content_type).file_id
            send_method(connect_to, file_id)

    def _upsert_user(self, message):
        """Insert or update a user in the database."""
        self.db.users.update_one(
            {"_id": message.chat.id},
            {"$set": {
                **message.json,
                "connect_to": None
                }},
            upsert=True
        )

    def _insert_message(self, message, connect_to):
        """Insert a message into the database."""
        self.db.messages.insert_one(
            {
                "message": message.text,
                "user": message.chat.username,
                "chat": message.chat.id,
                "date": message.date,
                'to': self._get_user_from_db(connect_to).get('chat')
            }
        )

    def _find_user_with_state(self, state, chat_id):
        """Find a user with the given state."""
        return self.db.users.find_one(
            {
                "state": state,
                "_id": {"$ne": chat_id}
            }
            )

    def _set_None_connected_to(self, chat_id):
        """Set the 'connect_to' field of a user to None."""
        self.db.users.update_one(
            {"_id": chat_id},
            {"$set": {"connect_to": None}}
        )

    def _update_user_state(self, chat_id, state):
        """Update a user's state."""
        self.db.users.update_one(
            {"_id": chat_id},
            {"$set": {"state": state}}
        )

    def run(self):
        """
        Start the bot.
        """
        logger.info("Bot running...")
        self.bot.infinity_polling()


if __name__ == '__main__':
    logger.info("Bot started")
    bot_instance = Bot(telebot=bot)
    bot_instance.run()
