from aiogram import Bot
from aiogram.methods import SendMessage, SendPhoto, SendVideo
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram import exceptions

class Sender():
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send(self, text_arr: list, media_arr: list[dict], chat_id: int):
        for k in range(len(text_arr)):
            try:
                text = text_arr[k]['text']
                media = media_arr[k]
                if len(media) > 1:
                    payload = []
                    for i, pic in enumerate(media):
                        if i != 0:
                            text=""
                        if not pic['is_gif']:
                            payload.append(InputMediaPhoto(caption=text, media=pic['url'], parse_mode="HTML"))
                        else: payload.append(InputMediaVideo(caption=text, media=pic['url'], parse_mode="HTML"))
                    await self.bot.send_media_group(chat_id=chat_id, media=payload)
                else:
                    if not media[0]:
                        await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
                    if not media[0]['is_gif']:
                        await self.bot(SendPhoto(chat_id=chat_id, photo=media[0]['url'], caption=text, parse_mode="HTML"))
                    else:
                        await self.bot(SendVideo(chat_id=chat_id, video=media[0]['url'], caption=text, parse_mode="HTML"))
            except exceptions.AiogramError as e:
                print(e)
                continue