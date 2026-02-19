"""Safe edit utility to handle 'message is not modified' errors."""
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest


async def safe_edit_text(message: Message, text: str, reply_markup=None) -> None:
    """
    Safely edit message text, ignoring 'message is not modified' errors.
    
    Args:
        message: Message to edit
        text: New text
        reply_markup: Optional inline keyboard
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise
