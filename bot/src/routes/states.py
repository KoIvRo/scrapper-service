from aiogram.fsm.state import State, StatesGroup


class ListStates(StatesGroup):
    """Состояния для команды /list."""

    waiting_for_command = State()


class TrackStates(StatesGroup):
    """Состояния для команды /track."""

    waiting_for_links = State()
    waiting_for_tags = State()


class UntrackStates(StatesGroup):
    """Состояния для команды /untrack."""

    waiting_for_links = State()
