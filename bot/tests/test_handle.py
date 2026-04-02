import pytest
from routes.basic_commands import handle_start, handle_help, handle_unknown_message
from routes.commands import COMMANDS


class TestHandlers:
    """Класс тестировщик для обработчиков сообщений."""

    @pytest.mark.asyncio
    async def test_start_command(self, message_factory):
        """Тест: /start должен отвечать приветствием."""
        message = message_factory("/start")

        await handle_start(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Давайте начнем работу!" in call_args

    @pytest.mark.asyncio
    async def test_help_command(self, message_factory):
        """Тест: /help должен отвечать списком команд."""
        message = message_factory("/help")

        await handle_help(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]

        for cmd in COMMANDS:
            assert f"/{cmd['command']}" in call_args
            assert cmd["description"] in call_args

    @pytest.mark.asyncio
    async def test_unknown_command(self, message_factory):
        """Тест: неизвестная команда должна вызывать сообщение об ошибке."""
        message = message_factory("/unknown_command")

        await handle_unknown_message(message)

        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Похоже я вас не понял!" in call_args
