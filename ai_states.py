from aiogram.fsm.state import StatesGroup, State

class AIAssistantState(StatesGroup):
    """
    Defines the finite states used by the AI insurance assistant.
    """

    waiting_for_documents = State()
    """User has started interaction and is expected to upload passport and vehicle documents."""

    documents_received = State()
    """Documents have been received and are being analyzed or confirmed."""

    waiting_price_confirmation = State()
    """Waiting for the user to confirm the fixed insurance price."""

    policy_ready = State()
    """User confirmed the price, and the policy is ready to be generated."""

    sending_pdf = State()
    """The insurance policy PDF is being generated and sent to the user."""
