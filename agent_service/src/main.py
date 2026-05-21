from config import settings
from logger_config import init_logger


if __name__ == "__main__":
    init_logger()
    print(settings.kafka.topic)
