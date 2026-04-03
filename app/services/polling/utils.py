from db import queries
from dataclasses import dataclass
from aiogram.types import Message


@dataclass
class CompareItemData():
    id: int
    type: int 
    # -1 не поменялось
    # 0 подорожало
    # 1 подешевело 
    # 2 выгодное предложение
    # 3 продан последний
    # 4 выставлен единственный

    price: int
    old_price: int


def get_actual_items() -> list[int]:
    all_favs = queries.get_all_unique_favourite_item_ids()
    print('utils: got ids')
    return all_favs

def break_into_batches(items: list) -> list[list[int]]:
    batch_size = 30
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

def clear_response(r: dict):
    try:
        id = r.get('resp').get('result').get('item').get('id')

        sell_arr = r.get('resp').get('result').get('sell_orders')
        buy_arr = r.get('resp').get('result').get('buy_orders')
    except Exception as e:
        print("json response parsing error:", e)
        return
    if not sell_arr:
        sell_price = 0
    else:
        sell_price = int(sell_arr[0].get('price'))
    if not buy_arr:
        buy_price = 0
    else:
        buy_price = int(buy_arr[0].get('price'))

    return {
        'id': id,
        'sell_price': sell_price,
        'buy_price':buy_price
    }


def compare_item(r: dict) -> CompareItemData | bool:
    id = r['id']
    sell_price = r['sell_price']
    buy_price = r['buy_price']
    
    old_item = queries.get_item_by_code(id)
    old_sell_price = old_item.get('sell_orders')
    old_buy_price = old_item.get('buy_orders')

    if old_sell_price != sell_price:
        if sell_price == 0:
            type = 3
        elif old_sell_price == 0:
            type = 4
        elif sell_price > old_sell_price:
            type = 0
        elif sell_price < old_sell_price:
            type = 1
        price = sell_price
        old_price = old_sell_price
        

    elif old_buy_price != buy_price and buy_price >= sell_price*0.6:
        type = 2
        price = buy_price
        old_price = 0

    elif old_sell_price == sell_price:
        return False

    changes = CompareItemData(id=id, type=type, price=price, old_price=old_price)
    print(type)
    return changes
    
def update_db(data: CompareItemData):
    if data.type in [0, 1, 3, 4]:
        queries.update_item(data.id, sell_orders=data.price)
    elif data.type == 2:
        queries.update_item(data.id, buy_orders=data.price)

def find_recievers(data: list[CompareItemData]):
    arr = []
    for i in data:
        chat = queries.get_all_unique_favourite_owner_ids(int(i.id))
        arr.append(chat)
    chats = []
    for a in arr:
        chats.extend(a)
    chats = list(dict.fromkeys(chats))
    return chats

def format_with_dots(n: int) -> str:
    return f"{n:,}".replace(',', '.')


def item_data_for_batch(bath_data: list[CompareItemData]):
    items = []
    for i in bath_data:
        item = queries.get_item_by_code(i.id)
        items.append(item)
    return items

def check_access(msg: Message) -> bool:
    user = queries.get_user(msg.from_user.id)
    if user['is_admin']:
        return True
    else:
        return False

def correct_media_array(text_arr: list, media_arr: list):
    new_media_arr = []
    added = 0
    for i in text_arr:
        batch_len = i['count']
        new_media_arr.append(media_arr[added:batch_len+added])
        added += batch_len
    
    return new_media_arr