from prometheus_client import Gauge, Histogram, Counter

links_on_track = Gauge(
    "links_on_track_total",
    "Количество отслеживаемых ссылок",
    ["tracked_source"],
)

request_duration = Histogram(
    "request_duration_ms_total",
    "Длительность операций в миллисекундах",
    ["scope", "scope_type"],
    buckets=(10, 50, 100, 200, 500, 1000, 2000, 5000),
)

api_requests = Counter(
    "api_requests_total",
    "Счётчик API-запросов",
    ["source"],
)
