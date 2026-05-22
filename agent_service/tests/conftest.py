import sys
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.dto import LinkUpdate


@pytest.fixture
def mock_link_update():
    return LinkUpdate(
        id=1,
        url="https://stackoverflow.com/questions/123/test",
        author="KoIvRo",
        description="Hello, World! Реклама",
        tgChatIds=[100],
    )
