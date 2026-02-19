"""Safe edit_text: ignore Telegram 'message is not modified' error."""
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def safe_edit_text(message: Message, text: str, reply_markup=None) -> None:
    """Edit message text; ignore Telegram 'message is not modified' error."""
    try:
        await message.edit_text(text=text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise
