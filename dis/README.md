# Data Ingestion Service (DIS)

Микросервис для получения и начальной обработки данных от IoT устройств.

## Функциональность

- Получение сообщений от датчиков из топиков MQTT
- Сохранение полученных данных в ClickHouse
- Отправка данных в Kafka для дальнейшей обработки

## Архитектура

Сервис использует:
- **MQTT** для получения данных от устройств
- **ClickHouse** для хранения временных рядов данных от датчиков
- **Kafka** для передачи данных другим микросервисам

## Установка и запуск

### Запуск с использованием Docker Compose

1. Клонировать репозиторий:
```
git clone https://github.com/yourusername/dis.git
cd dis
```

2. Запустить сервис и необходимые зависимости:
```
docker-compose up -d
```

Это запустит:
- MQTT брокер (Mosquitto)
- ClickHouse базу данных
- Kafka и Zookeeper
- Веб-интерфейс для Kafka
- Сам сервис DIS

### Запуск в локальном окружении

1. Установить зависимости:
```
pip install -r requirements.txt
```

2. Настроить переменные окружения (создать файл .env на основе env.example)

3. Запустить сервис:
```
python src/main.py
```

## Тестирование

Для генерации тестовых данных используйте скрипт:

```
python src/test_publisher.py
```

## Доступ к сервисам

- **MQTT**: localhost:1883 (MQTT), localhost:9001 (веб-сокеты)
- **ClickHouse**: localhost:8123 (HTTP), localhost:9000 (TCP)
- **Kafka**: localhost:9092
- **Kafka UI**: http://localhost:8080

## Мониторинг

Логи доступны через Docker:

```
docker logs -f data-ingestion-service
``` 