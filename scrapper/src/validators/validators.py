import re
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

    PATTERN = re.compile(
        r'^https?://'
        r'(?:www\.)?'
        r'github\.com/'
        r'[\w.-]+/'
        r'[\w.-]+'
        r'(?:/.*)?$'
    )

    @staticmethod
    def validate_url(url: str) -> bool:
        """Валидация ссылки."""
        return bool(GitHubUrlValidator.PATTERN.match(url))


class StackOverFlowUrlValidator(BaseUrlValidator):
    """Валидация для stackoverflow."""

    PATTERN = re.compile(
        r'^https?://'
        r'(?:www\.)?'
        r'stackoverflow\.com/'
        r'questions/'
        r'\d+'
        r'(?:/[\w-]*)?'
        r'(?:/.*)?$'
    )

    @staticmethod
    def validate_url(url: str) -> bool:
        """Валидация ссылки."""
        return bool(StackOverFlowUrlValidator.PATTERN.match(url))

VALIDATORS = [GitHubUrlValidator, StackOverFlowUrlValidator]
