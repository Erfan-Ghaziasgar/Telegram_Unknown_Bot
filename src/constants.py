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
    main=create_inline_keyboard([KEYS.random_connect, KEYS.settings, KEYS.help]),
    settings=create_inline_keyboard([KEYS.language, KEYS.back]),
)