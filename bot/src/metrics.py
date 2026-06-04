from prometheus_client import Counter, Histogram


command_requests = Counter(
    "command_requests_total",
    "Счётчик обработанных команд",
    ["command"],
)

command_duration = Histogram(
    "command_duration_ms_total",
    "Длительность команд в миллисекундах",
    ["scope", "scope_type"],
    buckets=(10, 50, 100, 200, 500, 1000, 2000),
)

sent_notifications = Counter(
    "sent_notification_total",
    "Счётчик отправленных уведомлений",
)
