import sqlite3
from app.services import utils
from app.models import ScreenResponse
from aiogram.types import Message
from app.states import *
from db import queries
from app.services import utils
from app import keyboards

class NavigationService:
    def __init__(self):
        pass

    async def welcome(self, user_message: Message | None):
        uid = user_message.from_user.id
        uname = utils.get_user_name(user_message)
        answer = ScreenResponse(
                text=f"Привет, {uname}! Ты в главном меню.",
                reply_markup=keyboards.main_menu(),
                new_state=MainMenu.screen,
                additional_data=None,
                clear=True
            )
        if queries.get_user(uid):
            return answer
        else:
            queries.add_user(uid)
            # self.subscribe()
            return answer
        
        
    async def notif_settings(self, message: Message):
        uid = message.from_user.id
        is_enabled = queries.get_settings(uid)
        if is_enabled.get("notifications_enabled") == 0:
            keyboard = keyboards.turn_on()
        else:
            keyboard = keyboards.turn_off()

        return ScreenResponse(
            text="Настройки уведомлений:",
            reply_markup=keyboard,
            new_state=NotifSettings.screen,
            additional_data=None,
            clear=True
        )
        
    async def alter_settings(self, message: Message):
        uid = message.from_user.id
        is_enabled = queries.get_settings(uid)
        if is_enabled.get("notifications_enabled") == 0:
            queries.update_settings(uid, "notifications_enabled", 1)
            add_text="Включено!"
            keyboard = keyboards.turn_off()
        else:
            queries.update_settings(uid, "notifications_enabled", 0)
            add_text="Выключено!"
            keyboard = keyboards.turn_on()

        return ScreenResponse(
            text=f"{add_text}\n\nНастройки уведомлений:",
            reply_markup=keyboard,
            new_state=NotifSettings.screen,
            additional_data=None,
            clear=True
        )
    
    async def not_implemented(self):
        return ScreenResponse(
            text="В разработке.",
            reply_markup=None,
            new_state=None,
            additional_data=None,
            clear=False
        )
        
    async def fav(self, message: Message):
        uid = message.from_user.id
        favs = queries.get_user_favourite_item_ids(uid)
        print(favs)
        favs = sorted(favs)
        print(favs)
        if not favs:
            text="Пока что у вас нет ни одного предмета в Избранном. Добавьте первый!"
        else:
            text = "Избранное:\n\n"
            add_text = ""
            if len(favs) > 11:
                num = len(favs) - 10
                favs = favs[:10]
                add_text = f"\n     ...и еще {num} предметов."

            for i in favs:
                item = queries.get_item_by_code(i)
                if item is None:
                    queries.delete_favourite(uid, i)
                    continue
                name = item["name"]
                text += f"{i}: {name}\n"

            text += add_text

        return ScreenResponse(
            text=text,
            reply_markup=keyboards.fav_menu(),
            new_state=NotifSettings.fav_menu,
            additional_data=None,
            clear=True
        )
    
    async def add_to_fav(self, message: Message):
        return ScreenResponse(
            text="Отправьте ссылку с <a href=\"https://t.me/banditchatbot/market\">ББМ</a> на предмет, который хотите добавить.\nМожно отправить несколько ссылок за раз, каждую с новой строки.\nДобавить все возможные вещи командой \"все\"",
            reply_markup=keyboards.back(),
            new_state=NotifSettings.input,
            additional_data=None,
            clear=False
        )
    
    async def parse_links(self, message: Message):
        text = "Успешно добавлено:\n\n"
        added_items = []

        uid = message.from_user.id
        favs = queries.get_user_favourite_item_ids(uid)
        if message.text == "все":
            await message.answer("Загрузка...")
            ids = []
            allitems = queries.get_all_items()
            for item in allitems:
                ids.append(item["item_code"])
        else:
            ids = utils.parse_startapp_ids(message.text)

        for id in ids:
            item = queries.get_item_by_code(id)
            print("adding ", item)
            if not item:
                await message.answer(f"Ошибка добавления предмета {id}")
                continue
            
            if id in favs:
                await message.answer(f"{item['name']} уже есть в избранном")
            else:
                try:
                    queries.add_favourite(uid, id)
                    added_items.append({
                        "id": id,
                        "name": item["name"]
                    })
                except sqlite3.IntegrityError as e:
                    print("fav alreafy exists")

        for i in added_items:
            text += str(i["id"]) + ": " +  str(i["name"]) + "\n"

        if len(added_items) == 0:
            text += "Ничего"
        
        if len(text) > 1023:
            text = text[:1020] + "..."
        # print("favs:", favs)
        # print(message.text)

        return ScreenResponse(
            text=text,
            reply_markup=keyboards.back(),
            new_state=None,
            additional_data=None,
            clear=False
        )

    async def remove_from_fav(self, message: Message):
        return ScreenResponse(
            text="Введите код предмета, который хотите убрать.\nВведите \"все\" чтобы удалить из избранного все предметы",
            reply_markup=keyboards.back(),
            new_state=NotifSettings.fav_remove,
            additional_data=None,
            clear=False
        )

    async def rem(self, message: Message):
        uid = message.from_user.id
        favs = queries.get_user_favourite_item_ids(uid)
        text = message.text
        if text.lower() == "все" or text.lower() == "всё" or text.lower() == "алл":
            items = queries.get_user_favourite_item_ids(uid)
            for item in items:
                queries.delete_favourite(uid, item)
            answer = "Удалено всё из избранного!"
        else:
            try:
                num = int(text)
                print("favs:", favs, "num:", num)
                if num not in favs:
                    answer = "Указанного предмета нет в избранном."
                
                else:
                    item = queries.get_item_by_code(num)
                    queries.delete_favourite(uid, num)
                    answer = item["name"] +  " успешно удален"
            except:
                answer = "Введите корректный код предмета."
        return ScreenResponse(
            text=answer,
            reply_markup=keyboards.fav_menu(),
            new_state=NotifSettings.fav_menu,
            additional_data=None,
            clear=True
        )
    
    async def fallback(self):
        return ScreenResponse(
            text="Неизвестная команда",
            reply_markup=keyboards.main_menu(),
            new_state=MainMenu.screen,
            additional_data=None,
            clear=True
        )