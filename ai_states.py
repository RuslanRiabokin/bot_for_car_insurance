from aiogram.fsm.state import StatesGroup, State

class AIAssistantState(StatesGroup):
    waiting_for_documents = State()
    documents_received = State()
