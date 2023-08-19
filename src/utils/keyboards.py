from telebot import types


def create_reply_keyboard(buttons: list, row_width: int = 3, one_time_keyboard: bool = True, resize_keyboard: bool = True, selective: bool = False) -> types.ReplyKeyboardMarkup:
    """
    Create a keyboard with buttons
    :param buttons: list of buttons
    :param row_width: number of buttons in a row
    :param one_time_keyboard: hide keyboard after click
    :param resize_keyboard: resize keyboard
    :param selective: show keyboard for specific users
    :return: keyboard
    """
    keyboard = types.ReplyKeyboardMarkup(row_width=row_width, one_time_keyboard=one_time_keyboard,
                                         resize_keyboard=resize_keyboard, selective=selective)
    buttons = map(lambda button: types.KeyboardButton(button), buttons)
    keyboard.add(*buttons)
    return keyboard


def create_inline_keyboard(buttons: list, row_width: int = 3) -> types.InlineKeyboardMarkup:
    """
    Create a keyboard with buttons
    :param buttons: list of buttons
    :param row_width: number of buttons in a row
    :return: keyboard
    """
    keyboard = types.InlineKeyboardMarkup(row_width=row_width)
    buttons = map(lambda button: types.InlineKeyboardButton(button, callback_data=button), buttons)
    keyboard.add(*buttons)
    return keyboard