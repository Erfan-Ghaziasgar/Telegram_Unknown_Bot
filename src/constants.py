from types import SimpleNamespace
from src.utils.keyboards import create_reply_keyboard


KEYS = SimpleNamespace(
    random_connect="🔀 Random connect",
    settings="⚙️ Settings",
    help="❓ Help",
    back="🔙 Back",
    language="🌐 Language",
    exit="❌ Exit",
)

KEYBOARDS = SimpleNamespace(
    main=create_reply_keyboard([KEYS.random_connect, KEYS.help]),
    settings=create_reply_keyboard([KEYS.settings, KEYS.language, KEYS.back]),
    exit=create_reply_keyboard([KEYS.exit]),
)

STATES = SimpleNamespace(
    idle="IDLE",
    random_connect="RANDOM_CONNECT",
    settings="SETTINGS",
    connect="CONNECT",
)

CONTENT_TYPE_MAPPING = {
    'text': 'send_message',
    'voice': 'send_voice',
    'sticker': 'send_sticker',
    'document': 'send_document',
    'video': 'send_video',
    'photo': 'send_photo',
    'audio': 'send_audio',
    'animation': 'send_animation',
}
