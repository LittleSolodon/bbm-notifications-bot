from db  import queries
from pathlib import PurePath
import httpx
from app.services.notifications.sender import Sender
import asyncio
from aiogram.types import Message, CallbackQuery
from app.services import utils
import json
from dotenv import load_dotenv
import os

load_dotenv()

class NotificationService():
    def __init__(self, bot):
        self.iteration = 0
        self.progress = 0
        self.sender = Sender(bot)
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(2, pool=20),
            http2=True,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=30),
            transport=httpx.AsyncHTTPTransport(retries=2)
        )

    async def update_list(self, user_message: Message):
        print("begin")
        uid = user_message.from_user.id
        user = queries.get_user(uid)
        print(user)
        is_admin = user.get("is_admin")
        if is_admin == 0:
            return -1
        else:
            failed_ids = []
            for i in range(1400//30):
                tasks = []
                for k in range(30):
                    print(i*30 + k)
                    tasks.append(self.check_item(i*30 + k))
                res = await asyncio.gather(*tasks)

                for item_id, ok in res:
                    if not ok:
                        failed_ids.append(item_id)

                await asyncio.sleep(0.5)

            print("failed: ", failed_ids)
            
            return 0
        
    async def check_item(self, item_id: str):
        params = {
            "platform": "tg",
            "rawData": os.getenv("PLAYER_HASH"),
            "url": f"https://stage-app52440787-c7d40ae3d108.pages.vk-apps.com/index.html#/item/{item_id}",
            "type": "getItemInfo",
            "uniqueItemId": item_id
        }
        item = queries.get_item(item_id)
        if not item:
            try:
                r = await self.http_client.get(
                    url="https://analniy-demon.ru/market_api.php",
                    params=params
                )
                r = r.json()    
            except httpx.ReadTimeout:
                print(item_id, "timeout")
                return item_id, False
            except httpx.PoolTimeout:
                print(f"{item_id}: pool timeout")
                return item_id, False
            except httpx.ConnectTimeout:
                print(f"{item_id}: connect timeout")
                return item_id, False
            except httpx.ReadTimeout:
                print(f"{item_id}: read timeout")
                return item_id, False
            except httpx.HTTPStatusError as e:
                print(f"{item_id}: bad status {e.response.status_code}")
                return item_id, False
            except httpx.RequestError as e:
                print(f"{item_id}: request error {type(e).__name__}: {e}")
                return item_id, False


            if not r.get("ok"):
                print(f"{item_id}: wrong item id")
                return item_id, True
            else:
                # print(r)
                item_code = item_id
                item_name = r.get("result", {}).get("item", {}).get("rusfull", {})
                price = r.get("result", {}).get("item", {}).get("last_price", {})
                
                image_path = r.get("result", {}).get("item", {}).get("img_url", {})
                image_link = utils.parse_img_path(image_path)

                stats = r.get("result", {}).get("item", {}).get("spec", {})
                stat_type = None
                stat_num = None
                is_animated = False

                try:
                    stats_dict = json.loads(stats) if isinstance(stats, str) else stats
                except (TypeError, json.JSONDecodeError):
                    stats_dict = {}

                if not isinstance(stats_dict, dict):
                    stats_dict = {}

                if stats_dict.get("att") is not None:
                    stat_type = 1
                    stat_num = stats_dict.get("att")
                elif stats_dict.get("def") is not None:
                    stat_type = 2
                    stat_num = stats_dict.get("def")

                is_animated = bool(stats_dict.get("anim"))
                
                queries.add_item(
                    item_code=item_code,
                    name=item_name,
                    image_link=image_link,
                    link_code=item_code,
                    price=price,
                    stat_type=stat_type,
                    stat_num=stat_num,
                    is_animated=is_animated,
                    
                )
                print(f"added {item_id}")

                print(item_code, f"aka {item_name} added to db")
        else:
            print(f"{item_id}: already in db")
        return item_id, True
    
    async def polling(self, message: Message):
        uid = message.from_user.id
        is_admin = queries.get_user(uid)
        if is_admin["is_admin"] == 0:
            return 0
        else:
            polling = queries.get_global_settings()
            if polling["polling"] == 0:
                queries.update_global_settings("polling", 1)
                await self.start_updating(message)
            else:
                queries.update_global_settings("polling", 0)
                self.iteration = 0
                self.progress = 0


    async def start_updating(self, message: Message):
        print("begin")
        uid = message.from_user.id
        is_admin = queries.get_user(uid)
        items = queries.get_all_items()
        items_count = len(items)
        if is_admin["is_admin"] == 0:
            return 0
        else:
            while True:

                self.iteration += 1
                failed_ids = []
                for i in range(items_count//30 + 1):
                    polling = queries.get_global_settings()
                    if polling["polling"] == 0:
                        return 1
                    tasks = []
                    for k in range(30):
                        if (i*30 + k) >= items_count:
                            break
                        code = int(items[(i*30 + k)]["item_code"])

                        # if code > 100:
                        #     break

                        tasks.append(self.compare(code))
                    res = await asyncio.gather(*tasks)

                    try:
                        for item_id, ok in res:
                            if not ok:
                                failed_ids.append(item_id)
                    except Exception as e:
                        print(e)

                    await asyncio.sleep(0.5)

                print("failed: ", failed_ids)

                while len(failed_ids) > 0:
                    print("here")
                    ids = failed_ids
                    tasks = []
                    failed_ids = []
                    for id in ids:
                        tasks.append(self.compare(id))
                    res = await asyncio.gather(*tasks)
                    
                    try:
                        for item_id, ok in res:
                            if not ok:
                                failed_ids.append(item_id)
                    except Exception as e:
                        print(e)
        
    async def compare(self, item_id: int):
        favs = queries.get_favourites_by_item_id(item_id)
        if not favs:
            return item_id, True
        
        self.progress = round(item_id/1360, 2) * 100
        print("begin:", item_id)
        params = {
            "platform": "tg",
            "rawData": os.getenv("PLAYER_HASH"),
            "url": f"https://stage-app52440787-c7d40ae3d108.pages.vk-apps.com/index.html#/item/{item_id}",
            "type": "getItemInfo",
            "uniqueItemId": item_id
        }
        try:
            r = await self.http_client.get(
                url="https://analniy-demon.ru/market_api.php",
                params=params
            )
            r = r.json()    
        except httpx.ReadTimeout:
            print(item_id, "timeout")
            return item_id, False
        except httpx.PoolTimeout:
            print(f"{item_id}: pool timeout")
            return item_id, False
        except httpx.ConnectTimeout:
            print(f"{item_id}: connect timeout")
            return item_id, False
        except httpx.ReadTimeout:
            print(f"{item_id}: read timeout")
            return item_id, False
        except httpx.HTTPStatusError as e:
            print(f"{item_id}: bad status {e.response.status_code}")
            return item_id, False
        except httpx.RequestError as e:
            print(f"{item_id}: request error")
            return item_id, False
        except json.decoder.JSONDecodeError:
            print(item_id, "json error")
            return item_id, False


        if not r.get("ok"):
            print(f"{item_id}: wrong item id")
            return item_id, True
        else:
            # print(r)
            item_code = item_id
            item_name = r.get("result", {}).get("item", {}).get("rusfull", {})
            # print(item_name)
            price = r.get("result", {}).get("item", {}).get("last_price", {})
            
            buy_order = 0
            sell_order = 0
            buy_order_arr = r.get("result", {}).get("buy_orders", 0)
            if buy_order_arr:
                buy_order = int(buy_order_arr[0]["price"])
            sell_order_arr = r.get("result", {}).get("sell_orders", 0)
            if sell_order_arr:
                sell_order = int(sell_order_arr[0]["price"])

            old_item = queries.get_item_by_code(item_id)

            is_animated = old_item["is_animated"]

            old_buy_order = int(old_item["buy_orders"])
            old_sell_order = int(old_item["sell_orders"])

            
            if old_sell_order != sell_order:
                price_diff = sell_order - old_sell_order
                type = "sell"
                text = self.make_text(item_code, type, sell_order, old_sell_order)
                queries.update_item(item_id, sell_orders=sell_order)

            elif old_buy_order != buy_order:
                queries.update_item(item_id, buy_orders=buy_order)
                if buy_order > sell_order*0.6 and sell_order != 0:
                    type = "buy"
                    text = self.make_text(item_code, type, buy_order)

            else:
                return item_id, True

            photo_path = old_item["image_link"]

            chats = []
            for i in favs:
                ownerid = i["owner_id"]
                settings = queries.get_settings(ownerid)
                if settings["notifications_enabled"] == 1:
                    chats.append(ownerid)
            print(chats)

            try:
                for i in chats:
                    await self.sender.send(text, url=photo_path, chat_id=i, is_gif=is_animated)
            except Exception as e:
                print(e)
                return item_id, False
            return item_id, True



    def format_num(self, num):
        if num < 0:
            return '-' + self.format_number_with_dots(abs(num))
        num_str = str(num)
        parts = []
        while num_str:
            parts.append(num_str[-3:])
            num_str = num_str[:-3]
        parts.reverse()
        return '.'.join(parts)
    
    def make_text(self, item_code: int, type: str, new_price: int, old_price: int | None = None):
        item = queries.get_item_by_code(item_code)
        name = item["name"]
        stat_type = item["stat_type"]
        stat_num = item["stat_num"]
        is_animated = item["is_animated"]

        if stat_type == 1:
            stat_text = "💥"
        elif stat_type == 2:
            stat_text = "🛡️"
        else: stat_text = ""

        if stat_num is None:
            stat_num = ""

        stat_text += str(stat_num)


        price_text = self.format_num(new_price)
        link = f"<b><a href=\"https://t.me/banditchatbot/market?startapp={item_code}\">{name}</a></b> ({stat_text}) "

        if type == "sell":
            old_price_text = self.format_num(old_price)
            try:
                percentage = round((1.0 - round(new_price / old_price, 2)) * 100 * -1, 2)
                template = f"Добавлен ордер на продажу {link} за "
                if abs(percentage) == 0:
                    if new_price > old_price:
                        percentage = 0.01
                    else:
                        percentage = -0.01
                if percentage > 0:
                    percentage = "+" + str(percentage)
                    template = f"Цена на {link} выросла! Новая цена: "
            except ZeroDivisionError:
                percentage = "-"
                template = f"Добавлен ордер на продажу {link} за "
            text=f"""<b>Изменение цены!</b>

<blockquote>{template} ${price_text} ( {percentage}% ). Старая цена: ${old_price_text}.</blockquote>"""
        else:
            text=f"""<b>Новый запрос на покупку!</b>
            
<blockquote>Добавлен выгодный запрос на покупку {link} ${price_text}</blockquote>"""
        
        text += f"\n\nТег предмета: #0x{item_code}"
        return text

    async def clear_list(self, message: Message):
        uid = message.from_user.id
        is_admin = queries.get_user(uid)
        items = queries.get_all_items()
        if is_admin["is_admin"] == 0:
            return 0
        else:
            arr = []
            for i in items:
                arr.append(i["id"])
            
            n = sorted(arr)
            k = ""
            for m in n:
                name = queries.get_item_by_code(m)
                if name == k:
                    queries.delete_item(m)
                    print("deleted", m)
                k = name
            return 1
                

    async def userlist(self, message: Message):
        uid = message.from_user.id
        is_admin = queries.get_user(uid)
        print(is_admin)
        items = queries.get_all_items()
        if is_admin["is_admin"] == 0:
            return 0
        else:
            text = queries.get_users()
            await message.answer(text=str(text))