from abc import ABC, abstractmethod


class BaseUrlValidator(ABC):
    """Интерфейс валидаторов."""

    @staticmethod
    @abstractmethod
    def validate_url(url: str) -> bool:
        """Валидация."""
        pass


class GitHubUrlValidator(BaseUrlValidator):
    """Валидатор для гитхаба."""

    @staticmethod
    def validate_url(url: str) -> bool:
        len_split_url = 5  # "https", "", github.com, name, respos

        if "github.com" not in url:
            return False

        return len(url.split("/")) == len_split_url


class StackOverFlowUrlValidator(BaseUrlValidator):
    """Валидация для stackoverflow."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Валидация ссылки."""
        if "stackoverflow.com" not in url:
            return False

        if "questions" not in url:
            return False

        url_parts = url.split("/")

        questions_index = url_parts.index("questions")
        if questions_index + 1 >= len(url_parts):
            return False

        return True


VALIDATORS = [GitHubUrlValidator, StackOverFlowUrlValidator]
