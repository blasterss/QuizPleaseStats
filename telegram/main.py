import datetime
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import bold
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
import asyncpg

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Определение состояний бота
class GameForm(StatesGroup):
    game_type = State()
    season = State()
    team_name = State()

def str_to_date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, '%d.%m.%Y').date()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"<b>Привет, {message.from_user.full_name}!</b>\n"
        "Я бот для просмотра статистики по играм \"Квиз, плиз!\".\n"
        "Чтобы начать работу, введите команду /show_games.",
        parse_mode="HTML"
    )
    print(f"Пользователь {message.from_user.full_name} начал работу с ботом")

@dp.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
    await message.answer(
        f"**{bold('Квиз, плиз! (статистика)')}**\n"
        "Данный телеграм бот создан для просмотра простой статистики по сезонам игр \"Квиз, плиз!\".\n"
        "Для начала работы воспользуйтесь командой /show_games.\n"
        "У бота нет прямого доступа к базам данных игр.\n"
        "Вся информация по играм была взята с официального сайта: 'https://spb.quizplease.ru/schedule-past?QpGameSearch%5BcityId%5D=17&QpGameSearch%5Bmonth%5D=0&QpGameSearch%5Btype%5D=all&QpGameSearch%5Bbars%5D=all'.\n"
        "Возможны некоторые неточности в результатах в связи с изменением типа игр от 21.08.2024.\n"
    )

# Обработчик команды /show_games
@dp.message(Command("show_games"))
async def show_games(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Классика 👨‍🎓", callback_data="type_classic")],
        [InlineKeyboardButton(text="Тематическая классика 🌍", callback_data="type_thematicclassic")],
        [InlineKeyboardButton(text="Вся классика 📚", callback_data="type_allclassic")],
        [InlineKeyboardButton(text="Кино и музыка 🎬", callback_data="type_kim")],
        [InlineKeyboardButton(text="Тематический КиМ 🎼", callback_data="type_thematickim")],
        [InlineKeyboardButton(text="Весь КиМ 🎭", callback_data="type_allkim")],
        [InlineKeyboardButton(text="Все игры 📎", callback_data="type_allgames")],
    ])
    
    await message.delete()
    bot_message = await message.answer("Выберите тип игры:", reply_markup=keyboard)
    await state.update_data(last_bot_message_id=bot_message.message_id)
    await state.set_state(GameForm.game_type)

# Обработка выбора типа игры
@dp.callback_query(GameForm.game_type)
async def process_game_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    game_type = callback.data.split('_')[1]
    await state.update_data(game_type=game_type)
    
    seasons = ["🍁 Осень: 2024", "🌞 Лето: 2024", "🌸 Весна: 2024", "❄️ Зима: 2024",
               "🍁 Осень: 2023", "🌞 Лето: 2023", "🌸 Весна: 2023", "❄️ Зима: 2023",
               "🍁 Осень: 2022", "🌞 Лето: 2022", "🌸 Весна: 2022", "❄️ Зима: 2022",
               "🍁 Осень: 2021", "🌞 Лето: 2021", "🌸 Весна: 2021", "❄️ Зима: 2021",
               "🍁 Осень: 2020"]
    if 'kim' in game_type:
        seasons = ["🌸 Весна: 2024", "🍁 Осень: 2023", "🌸 Весна: 2023", "🍁 Осень: 2022"]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [InlineKeyboardButton(text=season, callback_data=f"season_{i}") for i, season in enumerate(seasons)]

    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]
        keyboard.inline_keyboard.append(row)
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Все время ⏰", callback_data="all_games")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Вернуться к выбору типа игры", callback_data="back_to_show_games")])
    
    await callback.message.delete()
    bot_message = await callback.message.answer("Выберите сезон:", reply_markup=keyboard)
    await state.update_data(last_bot_message_id=bot_message.message_id)
    await state.set_state(GameForm.season)

# Обработка выбора сезона
@dp.callback_query(GameForm.season)
async def process_season(callback: CallbackQuery, state: FSMContext):
    if callback.data == "back_to_show_games":
        await show_games(callback.message, state)
        return
    
    await callback.answer()
    user_data = await state.get_data()
    game_type = user_data.get('game_type')

    kim_dates = ['21.03.2024', '21.09.2023', '16.03.2023', '22.09.2022']
    classic_dates = [
        '29.08.2024', '30.05.2024', '29.02.2024', '30.11.2023', 
        '07.09.2023', '01.06.2023', '02.03.2023', '01.12.2022',
        '01.09.2022', '02.06.2022', '03.03.2022', '01.12.2021', 
        '31.08.2021', '02.06.2021', '03.03.2021', '02.12.2020', 
        '06.09.2020']

    classic_dates.insert(0, datetime.datetime.now().date().strftime('%d.%m.%Y'))
    kim_dates.insert(0, datetime.datetime.now().date().strftime('%d.%m.%Y'))

    if callback.data == "all_games":
        if 'kim' in game_type:
            start_season = str_to_date(kim_dates[-1])
            end_season = str_to_date(kim_dates[0])
        else:
            start_season = str_to_date(classic_dates[-1])
            end_season = str_to_date(classic_dates[0])
    else:
        index = int(callback.data.split('_')[1])

        if index + 1 < len(classic_dates):
            start_season = str_to_date(classic_dates[index + 1])
            end_season = str_to_date(classic_dates[index])
            if 'kim' in game_type:
                start_season = str_to_date(kim_dates[index + 1])
                end_season = str_to_date(kim_dates[index])
        else:
            await callback.message.answer("Ошибка: выберите правильный сезон.")
            return

    await state.update_data(start_season=start_season, end_season=end_season)
    print(start_season, end_season)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Вернуться к выбору сезона", callback_data="back_to_game_type")]
    ])
    
    await callback.message.delete()
    bot_message = await callback.message.answer("Введите название команды:", reply_markup=keyboard)
    await state.update_data(last_bot_message_id=bot_message.message_id)
    await state.set_state(GameForm.team_name)

# Обработка ввода названия команды
@dp.message(GameForm.team_name)
async def process_team_name(message: types.Message, state: FSMContext):
    team_name = message.text.strip()
    await state.update_data(team_name=team_name)
    user_data = await state.get_data()
    
    db: asyncpg.Pool = dp['db']
    
    query = """
        WITH most_popular_day AS (
            SELECT 
                day_of_week,
                COUNT(*) AS occurrences
            FROM 
                {}
            WHERE 
                date >= $1
                AND date < $2
                AND team_name ILIKE $3
            GROUP BY 
                day_of_week
            ORDER BY 
                occurrences DESC
            LIMIT 1
        ),
        most_popular_package AS (
            SELECT 
                package_number,
                COUNT(*) AS occurrences
            FROM 
                {}
            WHERE 
                date >= $1
                AND date < $2
                AND team_name ILIKE $3
            GROUP BY 
                package_number
            ORDER BY 
                occurrences DESC
            LIMIT 1
        ),
        most_popular_restaurant AS (
            SELECT 
                restaurant,
                COUNT(*) AS occurrences
            FROM 
                {}
            WHERE 
                date >= $1
                AND date < $2
                AND team_name ILIKE $3
            GROUP BY 
                restaurant
            ORDER BY 
                occurrences DESC
            LIMIT 1
        )
        SELECT 
            COUNT(*) AS games_played, 
            ROUND(AVG(total_points)::numeric, 2) AS average_score,
            ROUND(AVG(place)::numeric, 2) AS average_place,
            (SELECT day_of_week FROM most_popular_day) AS most_popular_value_day,
            (SELECT occurrences FROM most_popular_day) AS occurrences_day,
            (SELECT package_number FROM most_popular_package) AS most_popular_value_package,
            (SELECT occurrences FROM most_popular_package) AS occurrences_package,
            (SELECT restaurant FROM most_popular_restaurant) AS most_popular_value_restaurant,
            (SELECT occurrences FROM most_popular_restaurant) AS occurrences_restaurant
        FROM 
            {}
        WHERE 
            date >= $1
            AND date < $2
            AND team_name ILIKE $3
    """

    comp_teams = """        
        WITH team_games AS (
            SELECT 
                team_name,
                game_name,
                package_number
            FROM {}
            WHERE 
                date >= $1
                AND date < $2
                AND team_name ILIKE $3
        ),
        all_games AS (
            SELECT 
                tg.team_name AS current_team,
                g.team_name AS opponent_team
            FROM team_games tg
            JOIN {} g
            ON tg.game_name = g.game_name
            AND tg.package_number = g.package_number
            WHERE g.team_name NOT ILIKE $3
        )
        SELECT 
            opponent_team,
            COUNT(*) AS games_played
        FROM all_games
        GROUP BY opponent_team
        ORDER BY games_played DESC
        LIMIT 3;
    """

    # Форматирование запросов
    table_name = user_data['game_type']
    formatted_query = query.format(table_name, table_name, table_name, table_name)
    formatted_comp = comp_teams.format(table_name, table_name)

    try:
        async with db.acquire() as connection:
            # Получение данных по основному запросу
            print("start query")
            result = await connection.fetchrow(formatted_query, user_data['start_season'], user_data['end_season'], user_data['team_name'])
            # print(result)
            # Получение данных по топ-командам
            result2 = await connection.fetch(formatted_comp, user_data['start_season'], user_data['end_season'], user_data['team_name'])

        if result:
            games_played = result['games_played']
            average_score = result['average_score']
            average_place = result['average_place']
            most_popular_value_day = result['most_popular_value_day']
            occurrences_day = result['occurrences_day']
            most_popular_value_package = result['most_popular_value_package']
            occurrences_package = result['occurrences_package']
            most_popular_value_restaurant = result['most_popular_value_restaurant']
            occurrences_restaurant = result['occurrences_restaurant']

            top_competitors = [
                {"opponent_team": row['opponent_team'], "games_played": row['games_played']}
                for row in result2
            ]
            top_competitors_formatted = '\n'.join([f'  • {row["opponent_team"]} ({row["games_played"]} игр)' for row in top_competitors])

            response = (
                f"<b>Результаты для команды \"{user_data['team_name']}\":</b>\n"
                f"• Тип игры: {user_data['game_type']}\n"
                f"• Сезон: {user_data['start_season']} - {user_data['end_season']}\n"
                f"• Количество игр: {games_played}\n"
                f"• Средний балл: {average_score}\n"
                f"• Среднее место: {average_place}\n"
                f"• Самый часто играющийся пакет: {most_popular_value_package}, ({occurrences_package} раз)\n"
                f"• Самый частый день недели: {most_popular_value_day}, ({occurrences_day} раз)\n"
                f"• Самый популярный ресторан: {most_popular_value_restaurant}, ({occurrences_restaurant} раз)\n"
                f"• Самые часто встречающиеся команды:\n"
                f"{top_competitors_formatted}"
            )

        else:
            response = "Данные не найдены для указанной команды. Пожалуйста, попробуйте снова."
    except Exception as e:
        response = f"Произошла ошибка: {str(e)}"

    # Удаление сообщений
    user_message_id = message.message_id
    state_data = await state.get_data()
    bot_message_id = state_data.get('last_bot_message_id')
    
    if bot_message_id:
        print(f"Попытка удалить сообщение бота с ID: {bot_message_id}")
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение бота: {e}")
    else:
        print("Идентификатор сообщения бота не найден.")
    
    await message.delete()
    
    await message.answer(response, parse_mode="HTML")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Вернуться к выбору сезона", callback_data="back_to_game_type")]
    ])
    
    bot_message = await message.answer("Введите название команды:", reply_markup=keyboard)
    await state.update_data(last_bot_message_id=bot_message.message_id)
    await state.set_state(GameForm.team_name)

# Обработка возврата на предыдущие шаги
@dp.callback_query(lambda c: c.data == "back_to_game_type")
async def back_to_game_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await process_game_type(callback, state)

@dp.callback_query(lambda c: c.data == "back_to_show_games")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_games(callback.message, state)

# Установка подключения к базе данных при старте бота
async def on_startup():
    dp['db'] = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print("База данных подключена.")

# Закрытие подключения к базе данных при остановке бота
async def on_shutdown():
    await dp['db'].close()
    print("База данных отключена.")

# Запуск бота
async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == '__main__':
    asyncio.run(main())
