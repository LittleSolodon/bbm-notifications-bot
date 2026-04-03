from aiogram.types import ReplyKeyboardMarkup 
from aiogram.fsm.state import State
from dataclasses import dataclass

@dataclass(frozen=True)
class ScreenResponse:
    text: str
    reply_markup: ReplyKeyboardMarkup
    new_state: State | None
    additional_data: dict
    clear: bool = False