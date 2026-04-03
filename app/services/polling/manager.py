import asyncio
from app.services.polling.api_client import ApiClient
from app.services.polling import utils, notificatoin_builder
from app.services.polling.sender import Sender
from db import queries
from aiogram.types import Message


class PollingManager():
    def __init__(self, bot):
        self.task: asyncio.Task | None = None
        self.api_client: ApiClient | None = ApiClient()
        self.sender = Sender(bot)

    async def switch(self, msg: Message):
        if utils.check_access(msg):
            is_enabled = queries.get_global_settings()
            if not is_enabled['polling']:
                self.api_client = ApiClient()
                self.start_polling()
                queries.update_global_settings('polling', 1)
                return 'on'
            else:
                await self.stop_polling()
                await self.api_client.aclose()
                self.api_client = None
                queries.update_global_settings('polling', 0)
                return 'off'
        else:
            return False


    def start_polling(self):
        print('start_polling')
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.polling())
            print("start polling")
            return True
        else:
            return False

    async def stop_polling(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            finally:
                self.task = None
                return True
        else:
            print("already done")
            return False
        
    async def polling(self):
        print('begin')
        counter = 0
        while not self.task.done():
            actual_ids = utils.get_actual_items()
            batches = utils.break_into_batches(actual_ids)
            counter += 1
            print(counter)

            for i, batch in enumerate(batches):
                await asyncio.sleep(10)
                results = await self.api_client.get_batch(batch)
                batch_data: list[utils.CompareItemData] = []
                for r in results:
                    if r['success']:
                        try:
                            clear = utils.clear_response(r)
                        except Exception:
                            continue
                        item_data = utils.compare_item(clear)
                        if item_data:
                            batch_data.append(item_data)
                            utils.update_db(item_data)
                if not batch_data:
                    print('no_batch_data')
                    continue
                items_data = utils.item_data_for_batch(batch_data)
                print('batch: ', batch_data, items_data)
                text = notificatoin_builder.make_text(batch_data, items_data)
                print('text', text)
                media = notificatoin_builder.make_media(batch_data, items_data)
                media = utils.correct_media_array(text_arr=text, media_arr=media)
                print('media', media)
                chats = utils.find_recievers(batch_data)
                print('chats', chats)
                for chat in chats:
                    await self.sender.send(text, media, chat)
                    print('sent', chat)

            print('task', self.task.done())