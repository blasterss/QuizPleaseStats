from aiogram.fsm.state import StatesGroup, State

class GameForm(StatesGroup):
    game_type = State()
    season = State()
    team_name = State()