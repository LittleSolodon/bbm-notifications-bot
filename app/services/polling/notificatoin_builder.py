from db import queries
import app.services.polling.utils as utils


def make_text(data: list[utils.CompareItemData], items_data: list) -> list:
    backup = ""
    text = ""
    array = []
    templ = "Изменения цен:\n\n"
    start_new_message = True
    counter = 0
    for ij in range(len(data)):
        counter += 1
        compared_data = data[ij]
        if start_new_message:
            text = templ
            start_new_message = False
            
        id = compared_data.id
        price_text = utils.format_with_dots(compared_data.price)
        old_price_text = utils.format_with_dots(compared_data.old_price)

        item = next(d for d in items_data if d["item_code"] == id)

        name = item["name"]
        stat_type = item["stat_type"]
        stat_num = item["stat_num"]
        link_code = item["link_code"]

        if stat_type == 1:
            stat_text = "💥"
        elif stat_type == 2:
            stat_text = "🛡️"
        else: stat_text = ""

        if stat_num is None:
            stat_num = ""

        stat_text += str(stat_num)
        link_template = f"<b><a href=\"https://t.me/banditchatbot/market?startapp={link_code}\">{name}</a></b> ({stat_text}) "

        if compared_data.old_price != 0 and compared_data.type in [0, 1]:
            percentage = round((1.0 - round(compared_data.price / compared_data.old_price, 2)) * 100 * -1, 2)
            if abs(percentage) == 0:
                if compared_data.price > compared_data.old_price:
                    percentage = 0.01
                else:
                    percentage = -0.01
            if percentage > 0:
                percentage_text = "+" + str(percentage)
            else:
                percentage_text = str(percentage)
            percentage_text = "(" + percentage_text + ")"
        else:
            percentage_text = ""

        if compared_data.type == 0:
            item_text = f"Цена на {link_template} выросла!\nНовая цена: ${price_text} {percentage_text}.\nСтарая цена: {old_price_text}"
        elif compared_data.type == 1:
            item_text = f"Цена на {link_template} понизилась!\nНовая цена: ${price_text} {percentage_text}.\nСтарая цена: {old_price_text}"
        elif compared_data.type == 3:
            item_text = f"Последний товар {link_template} продан за {old_price_text}"
        elif compared_data.type == 4:
            item_text = f"Выставлен {link_template} за {price_text}"
        elif compared_data.type == 2:
            item_text = f"Добавлен выгодный ордер на покупку {link_template} за {price_text}"

        tag = f"#0x{id}"

        text = text + "<blockquote>" + item_text + "\n" + tag + "</blockquote>\n" 

        if len(text) < 1024:
            backup = text
        else: 
            ij -= 1
            array.append({
                'text': backup,
                'count': counter
            })
            backup = ""
            text = ""
            start_new_message = True
            counter = 0
            continue

        if ij == len(data) - 1:
            array.append({
                'text': backup,
                'count': counter
            })
    return array

def make_media(data: list[utils.CompareItemData], items_data: list) -> list[dict]:
    urls = []
    for i in data:
        item = next(d for d in items_data if d["item_code"] == i.id)
        is_gif = item['is_animated']
        urls.append({
            'url': item['image_link'],
            'is_gif': is_gif}
            )
    return urls