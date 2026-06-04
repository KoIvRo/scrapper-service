# PromQL запросы для дашбордов Grafana

## RED дашборд

### Rate (количество запросов)

```
http_requests_total
```

### Errors (ошибки)

```
http_requests_total{status="5xx"}
```

### Duration (средняя длительность запроса)

```
http_request_duration_highr_seconds_sum / http_request_duration_highr_seconds_count
```

### Memory (используемая память)

```
process_resident_memory_bytes
```

---

## Бизнес дашборд

### Количество отправленных нотификаций

```
sent_notification_total
```

### Количество активных ссылок

```
links_on_track_total
```

### Количество API-запросов к Scrapper

```
api_requests_total
```

### Количество команд бота

```
command_requests_total
```

### Среднее время scrape по источникам

```
request_duration_ms_total_sum / request_duration_ms_total_count
```

### Среднее время обработки команд бота

```
command_duration_ms_total_sum / command_duration_ms_total_count
```

---

## RED дашборд (Bot)

### Rate

```
http_requests_total
```

### Errors

```
http_requests_total{status="5xx"}
```

### Duration

```
http_request_duration_highr_seconds_sum / http_request_duration_highr_seconds_count
```

### Memory

```
process_resident_memory_bytes
```

---

## Бизнес дашборд (Bot)

### Количество отправленных нотификаций

```
sent_notification_total
```

### Количество команд

```
command_requests_total
```

### Среднее время обработки команд

```
command_duration_ms_total_sum / command_duration_ms_total_count
```
