import telebot
from loguru import logger

from src.bot import bot
from src.constants import KEYBOARDS, KEYS, STATES
from src.db import db
from src.utils.utils import send_message, send_photo


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

        @self.bot.message_handler(regexp=KEYS.random_connect)
        def random_connect(message):
            self._handle_random_connect(message)

        @self.bot.message_handler(regexp=KEYS.exit)
        def exit(message):
            self._handle_exit(message)

        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            self._handle_photo_message(message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message):
            self._handle_text_message(message)

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
            self._forward_message_to_connected_user(user,
                                                    "User has left the chat",
                                                    reply_markup=KEYBOARDS.main)
            self._update_user_state(user.get("connect_to"), STATES.idle)
            self._update_user_state(message.chat.id, STATES.idle)
            self._set_None_connected_to(user.get("connect_to"))
            self._set_None_connected_to(message.chat.id)

    def _handle_text_message(self, message):
        """
        Echo messages when user is in 'connect' state.
        """
        user = self._get_user_from_db(message.chat.id)
        if self._user_state_is_connect(user):
            self._forward_message_to_connected_user(user, message.text)

    def _handle_photo_message(self, message):
        """
        Handle photo messages when user is in 'connect' state.
        """
        user = self._get_user_from_db(message.chat.id)
        if self._user_state_is_connect(user):
            self._forward_photo_to_connected_user(user, message.photo[-1].file_id)

    # private helper methods for DB operations
    def _get_user_from_db(self, chat_id):
        """Retrieve a user from the database using their chat ID."""
        return self.db.users.find_one({"_id": chat_id})

    def _user_state_is_connect(self, user):
        """Check if the user's state is 'connect'."""
        return user.get('state') == STATES.connect

    def _forward_message_to_connected_user(self, user, text, reply_markup=None):
        """Forward the message to the connected user."""
        connect_to = user.get('connect_to')
        if connect_to:
            send_message(self, connect_to, text, reply_markup=reply_markup)

    # TODO: handle send photo
    def _forward_photo_to_connected_user(self, user, photo_id, reply_markup=None):
        """Forward the message to the connected user."""
        connect_to = user.get('connect_to')
        if connect_to:
            send_photo(self, connect_to, photo_id, reply_markup=reply_markup)

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
