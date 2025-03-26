from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def game_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Классика 👨‍🎓", callback_data="type_classic")],
        [InlineKeyboardButton(text="Тематическая классика 🌍", callback_data="type_thematicclassic")],
        [InlineKeyboardButton(text="Вся классика 📚", callback_data="type_allclassic")],
        [InlineKeyboardButton(text="Кино и музыка 🎬", callback_data="type_kim")],
        [InlineKeyboardButton(text="Тематический КиМ 🎼", callback_data="type_thematickim")],
        [InlineKeyboardButton(text="Весь КиМ 🎭", callback_data="type_allkim")],
        [InlineKeyboardButton(text="Все игры 📎", callback_data="type_allgames")],
    ])

def season_keyboard(game_type):
    seasons = ["❄️ Зима: 2025",
               "🍁 Осень: 2024", "🌞 Лето: 2024", "🌸 Весна: 2024", "❄️ Зима: 2024",
               "🍁 Осень: 2023", "🌞 Лето: 2023", "🌸 Весна: 2023", "❄️ Зима: 2023",
               "🍁 Осень: 2022", "🌞 Лето: 2022", "🌸 Весна: 2022", "❄️ Зима: 2022",
               "🍁 Осень: 2021", "🌞 Лето: 2021", "🌸 Весна: 2021", "❄️ Зима: 2021",
               "🍁 Осень: 2020"]
    if 'kim' in game_type:
        seasons = ["🍁 Осень: 2024", "🌸 Весна: 2024", "🍁 Осень: 2023", "🌸 Весна: 2023", "🍁 Осень: 2022"]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [InlineKeyboardButton(text=season, callback_data=f"season_{i}") for i, season in enumerate(seasons)]

    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]
        keyboard.inline_keyboard.append(row)
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Все время ⏰", callback_data="all_games")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Вернуться к выбору типа игры", callback_data="back_to_show_games")])
    return keyboard