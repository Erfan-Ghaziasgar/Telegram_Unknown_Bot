import emoji


def send_message(self, chat_id, text, reply_markup=None, emojize=True):
    '''
    Send message
    :param message: message
    '''
    if emojize:
        text = emoji.emojize(text)

    self.bot.send_message(chat_id, text, reply_markup=reply_markup)
