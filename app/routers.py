from app.services.navigation import NavigationService
from app.services.polling.manager import PollingManager
from app.models import ScreenResponse
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LinkPreviewOptions
from aiogram import Bot, Dispatcher, Router, F
from app import states

router = Router()

async def render(message: Message, state: FSMContext, res: ScreenResponse):
    if res.clear:
        await state.clear()
    if res.additional_data:
        await state.update_data(**res.additional_data)
    if res.new_state is not None:
        # print("changing to", res.new_state)
        await state.set_state(res.new_state)
    
    lpr = True
    if res.additional_data:
        lpr = False if res.additional_data.get("enable_link_preview") else True

    await message.answer(res.text, 
                         reply_markup=res.reply_markup, 
                         parse_mode="HTML", 
                         link_preview_options=LinkPreviewOptions(
                             is_disabled=lpr
                         )
                        )

def build_services() -> NavigationService:
    return NavigationService()

nav = build_services()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    resp = await nav.welcome(message)
    await render(message, state, resp)

# @router.message(Command("update_list"))
# async def update_items(message: Message, state: FSMContext, notification_service: NotificationService) -> None:
#     await notification_service.update_list(message)
#     await message.answer("finished")

    # resp = await nav.update_list(message, http_client=notification_service)
    # await render(message, state, resp)

@router.message(Command("polling"))
async def pollig(message: Message, polling_manager: PollingManager) -> None:
    switch = await polling_manager.switch(message)
    if not switch:
        return await message.answer("no access")
    elif switch == 'on': return await message.answer("turned on")
    elif switch == 'off': return await message.answer("turned off")
    

# @router.message(Command("status"))
# async def status(message: Message, state: FSMContext, polling_manager: PollingManager) -> None:
#     await message.answer(text=f"Повтор: {notification_service.iteration}\nПрогресс: {notification_service.progress}%")

@router.message(Command("my_state"))
async def mstate(message: Message, state: FSMContext) -> None:
    cs = await state.get_state()
    await message.answer(f"current_state: {cs}")

# @router.message(Command("clear_list"))
# async def clear_list(message: Message, notification_service: NotificationService) -> None:
#     await notification_service.clear_list(message)

# @router.message(Command("users"))
# async def users(message: Message, notification_service: NotificationService) -> None:
#     await notification_service.userlist(message)


@router.message(StateFilter(states.MainMenu.screen), F.text == "Уведомления")
async def notif_menu(message: Message, state: FSMContext) -> None:
    resp = await nav.notif_settings(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.screen), 
                F.text.in_({"✅ Включить уведомления", "❌ Выключить уведомления"}))
async def change_notifications(message: Message, state: FSMContext) -> None:
    resp = await nav.alter_settings(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.screen), F.text == "⬅️ Назад")
async def go_back(message: Message, state: FSMContext) -> None:
    resp = await nav.welcome(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.screen), F.text == "🌟 Избранное")
async def favourites(message: Message, state: FSMContext) -> None:
    resp = await nav.fav(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.fav_menu), F.text == "Добавить предметы в избранное")
async def add_to_fav(message: Message, state: FSMContext) -> None:
    resp = await nav.add_to_fav(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.input), F.text != "⬅️ Назад")
async def fav_input(message: Message, state: FSMContext) -> None:
    resp = await nav.parse_links(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.input), F.text == "⬅️ Назад")
async def fav_go_back(message: Message, state: FSMContext) -> None:
    resp = await nav.fav(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.fav_menu), F.text == "Удалить из избранного")
async def fav_del(message: Message, state: FSMContext) -> None:
    resp = await nav.remove_from_fav(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.fav_remove), F.text != "⬅️ Назад")
async def fav_del_input(message: Message, state: FSMContext) -> None:
    resp = await nav.rem(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.fav_remove), F.text == "⬅️ Назад")
async def fav_del_go_back(message: Message, state: FSMContext) -> None:
    resp = await nav.fav(message)
    await render(message, state, resp)

@router.message(StateFilter(states.NotifSettings.screen), F.text == "Фильтры")
async def filters(message: Message, state: FSMContext) -> None:
    resp = await nav.not_implemented()
    await render(message, state, resp)

@router.message(StateFilter(states.MainMenu.screen), F.text == "Управление аккаунтом")
async def run_account(message: Message, state: FSMContext) -> None:
    resp = await nav.not_implemented()
    await render(message, state, resp)

@router.message()
async def update_items(message: Message, state: FSMContext) -> None:
    resp = await nav.fallback()
    await render(message, state, resp)

