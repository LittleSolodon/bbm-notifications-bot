import re
from aiogram.types import Message
from pathlib import Path

def get_user_name(msg: Message):
    last = "" if not msg.from_user.last_name else msg.from_user.last_name
    return msg.from_user.first_name + " " + last

def parse_img_path(file_path: str) -> str:
    filename = Path(file_path).name
    return f"https://analniy-demon.ru/market_img/{filename}"

def parse_startapp_ids(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"startapp=(\d+)", text)]
