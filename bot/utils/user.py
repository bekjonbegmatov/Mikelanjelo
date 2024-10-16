from aiogram.fsm.state import State , StatesGroup

class User_Registration(StatesGroup):
    gender = State()
    first_name = State()
    last_name = State()
    description = State()
    city = State()
    interests = State()
    age = State()
    photo = State()
    who_interested = State()
    
class User_Like_Message(StatesGroup):
    user_id_to = State()
    test = State()
    