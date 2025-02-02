# Эксперимент: Сравнение производительности MongoDB и PostgreSQL

**Объем данных:**
- PostgreSQL:
  - Лайков: 10,193,767
  - Рецензий: 503,763
  - Закладок: 503,763
- MongoDB:
  - Лайков: 10,002,114
  - Рецензий: 502,114
  - Закладок: 502,114

## Воспроизведение эксперимента

1. Запустите docker-compose для запуска баз данных MongoDB и PostgreSQL.
2. Запустите скрипт `run_initial_data.py` для первоначального заполнения баз синтетическими данными.
3. Запустите скрипт `test_read_write_performance.py` для запуска тестов скорости.

## Результаты

### Время появления лайка

| База данных | Среднее время появления лайка (сек) |
|-------------|-------------------------------------|
| PostgreSQL  | 3.256                               |
| MongoDB     | 87.77                               |

### Среднее время выполнения операций (в миллисекундах)

#### PostgreSQL

| Операция           | Среднее время выполнения |
|--------------------|--------------------------|
| insert_like        | 5.42 мс                  |
| insert_review      | 5.05 мс                  |
| insert_bookmark    | 4.98 мс                  |
| get_likes_count    | 1021.87 мс               |
| get_average_rating | 1057.17 мс               |
| get_reviews        | 138.17 мс                |

#### MongoDB

| Операция           | Среднее время выполнения |
|--------------------|--------------------------|
| insert_like        | 1.98 мс                  |
| insert_review      | 1.72 мс                  |
| insert_bookmark    | 1.67 мс                  |
| get_likes_count    | 12591.20 мс              |
| get_average_rating | 12698.77 мс              |
| get_reviews        | 0.10 мс                  |

## Описание тестов

1. **get_likes_count**: Тест подсчитывает общее количество лайков для фильма

2. **get_average_rating**: Тест вычисляет средний рейтинг для указанного фильма.

3. **get_reviews**: Тест возвращает последние 10 рецензий для указанного фильма, отсортированные по дате.

## Вывод

MongoDB показывает лучший результат по скорости вставки данных и получения отдельных данных (рецензий), однако медленнее производит аггрегацию и чтение большого количества данных. Возможной причиной является то, что Монго запущена на тесте в минимальной конфигурации.