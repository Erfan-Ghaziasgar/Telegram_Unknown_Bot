from types import SimpleNamespace
from src.utils.keyboards import create_reply_keyboard, create_inline_keyboard


KEYS = SimpleNamespace(
    random_connect="🔀 Random connect",
    settings="⚙️ Settings",
    help="❓ Help",
    back="🔙 Back",
    language="🌐 Language",
)

KEYBOARDS = SimpleNamespace(
    main=create_reply_keyboard([KEYS.random_connect, KEYS.help]),
    settings=create_reply_keyboard([KEYS.settings, KEYS.language, KEYS.back]),
)