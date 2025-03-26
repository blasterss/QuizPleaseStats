
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from fsm import GameForm
from aiogram.fsm.context import FSMContext
from keyboards import game_type_keyboard, season_keyboard
from database import fetch_game_stats, fetch_top_competitors

async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"<b>Привет, {message.from_user.full_name}!</b>\n"
        "Я бот для просмотра статистики по играм \"Квиз, плиз!\".\n"
        "Чтобы начать работу, введите команду /show_games.",
        parse_mode="HTML"
    )

async def show_games(message: Message, state: FSMContext):
    await message.delete()
    bot_message = await message.answer("Выберите тип игры:", reply_markup=game_type_keyboard())
    await state.update_data(last_bot_message_id=bot_message.message_id)
    await state.set_state(GameForm.game_type)

async def process_game_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    game_type = callback.data.split('_')[1]
    await state.update_data(game_type=game_type)
    
    bot_message = await callback.message.answer("Выберите сезон:", reply_markup=season_keyboard(game_type))
    await state.update_data(last_bot_message_id=bot_message.message_id)
    await state.set_state(GameForm.season)

async def process_team_name(message: Message, state: FSMContext):
    team_name = message.text.strip()
    await state.update_data(team_name=team_name)
    user_data = await state.get_data()

    # Запрос к базе данных
    stats = await fetch_game_stats(user_data)
    top_competitors = await fetch_top_competitors(user_data)

    response = f"Результаты для команды \"{team_name}\":\n{stats}\nТоп соперников:\n{top_competitors}"
    
    await message.answer(response, parse_mode="HTML")

def setup_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(show_games, Command("show_games"))
    dp.callback_query.register(process_game_type, GameForm.game_type)
    dp.message.register(process_team_name, GameForm.team_name)