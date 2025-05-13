from aiogram.fsm.state import StatesGroup, State

class AIAssistantState(StatesGroup):
    waiting_for_documents = State()
    documents_received = State()
    waiting_price_confirmation = State()
    policy_ready = State()
    sending_pdf = State()