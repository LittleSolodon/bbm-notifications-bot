from aiogram import Bot
from aiogram.methods import SendMessage, SendPhoto, SendVideo
from io import BytesIO

class Sender():
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send(self, text: str, url: str, chat_id: int, is_gif = False):
        if not is_gif:
            await self.bot(SendPhoto(chat_id=chat_id, photo=url, caption=text, parse_mode="HTML"))
        else:
            await self.bot(SendVideo(chat_id=chat_id, video=url, caption=text, parse_mode="HTML"))
