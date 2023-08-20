import emoji


def send_message(self, chat_id, text, reply_markup=None, emojize=True):
    '''
    Send message
    :param message: message
    '''
    if emojize:
        text = emoji.emojize(text)

    self.bot.send_message(chat_id, text, reply_markup=reply_markup)


def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
    '''
    Send photo
    :param photo: photo
    :param caption: caption
    '''
    self.bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
