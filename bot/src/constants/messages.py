from routes.commands import COMMANDS
from models.schemas import LinkResponse


class BasicCommandMessage:
    """Класс с константами ответов на базовые команды."""

    START_ANSWER: str = "Давайте начнем работу!"
    UNKNOWN_MESSAGES: str = "Похоже я вас не понял!\n\nВоспользуйтесь командой /help"

    @staticmethod
    def get_help_answer() -> str:
        """Создание отчета по командам для /help."""
        answer = "Воспользуйтесь командами.\n\n" + "\n".join(
            f"/{cmd['command']} - {cmd['description']}" for cmd in COMMANDS
        )
        return answer


class TrackMessages:
    """Класс с константами ответов для команды /track."""

    START_TRACK: str = "Введите ссылку для отслеживания!\n/cancel для отмены."
    APPEND_CANCEL: str = "Добавление ссылки отменено."
    TAG_APPEND: str = (
        "Введите теги к вашей ссылке через запятую.\nНапример: работа, баг, срочно\n"
        "Введите /skip, что бы пропустить этот шаг или оставьте поле пустым.\n"
        "/cancel для отмены."
    )
    TAG_SKIP: str = "Теги не будут сохранены."
    ERROR: str = "Произошла ошибка.\nПопробуйте еще раз."
    LINKS_ARE_MISSING: str = "У вас нет отслеживаемых ссылок"
    INVALID_URL: str = (
        "Упс...\nПроизошла ошибка.\nПроверьте ваш url и попробуйте еще раз!"
    )
    INVALID_CHAT: str = (
        "Упс...\nПроизошла ошибка.\nВозможно сервер недоступен, попробуйте еще раз!"
    )

    @staticmethod
    def get_tags_answer(tags: list[str]) -> str:
        return f"Теги сохранены: {', '.join(tags)}"

    @staticmethod
    def get_url_answer(url: str) -> str:
        return f"Ссылка добавлена:\n{url}"

    @staticmethod
    def get_links(links: list[LinkResponse]) -> str:
        links_with_tags = [[link.url, link.tags] for link in links]

        answer = []

        for link_with_tags in links_with_tags:
            if link_with_tags[1]:
                answer.append(
                    f"{link_with_tags[0]}\nС тегами: {', '.join(link_with_tags[1])}"
                )
            else:
                answer.append(f"{link_with_tags[0]}\n")

        return "Ваши отслеживаемые ссылки:\n" + "\n".join(answer)


class UntrackMessages:
    """Класс с константами ответов для команды /untrack."""

    START_UNTRACK: str = "Введите ссылку для прекращения отслеживания или /cancel."
    CANCEL_UNTRACK: str = "Команда /untrack отменена."
    ERROR: str = "Произошла ошибка.\nПопробуйте еще раз."

    @staticmethod
    def get_untrack_answer(url: str) -> str:
        return f"Ссылка {url} удалена."


class ListMessages:
    """Класс с константами для команды /list."""

    EXIT_LIST: str = "Вышли из режима"
    COMMAND_WARNING: str = "Отмените /list что бы продолжить общение"
