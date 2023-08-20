import emoji


def send_message(self, chat_id, text, reply_markup=None, emojize=True):
    '''
    Send message
    :param message: message
    '''
    if emojize:
        text = emoji.emojize(text)

    self.bot.send_message(chat_id, text, reply_markup=reply_markup)


def send_photo(self, chat_id, photo_id, reply_markup=None):
    '''
    Send photo
    :param message: message
    '''
    self.bot.send_photo(chat_id, photo_id, reply_markup=reply_markup)
