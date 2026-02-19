# Antipatterns

Типичные ошибки при генерации/запуске кода. 
Каждая ошибка имеет трейсбэк и конкретное решение.

---

## [AP-001] Cannot find module

Ошибка

**Трейсбэк:**

**Причина:**
Зависимость не установлена / не указана в package.json.

**Статус:** открыто\закрыто.

**Решение:**
Добавить express в dependencies и выполнить npm install.

---

## [AP-002] Использование ORM-объекта после закрытия сессии

**Описание:** В `bot/handlers/start.py` и `bot/handlers/menu.py` объект `User` получают внутри `async with async_session() as session` и затем используют (передают в тексты/клавиатуры) уже после выхода из контекста сессии. Работает только за счёт `expire_on_commit=False` и пока используются только уже загруженные атрибуты; при обращении к неподгруженным полям или смене настроек сессии возможны LazyLoaded/DetachedInstance ошибки.

**Статус:** закрыто.

**Решение:** Код не менялся (минимальные изменения). Рекомендация: не добавлять к модели `User` ленивые `relationship`, используемые в handlers; при необходимости передавать из сессии только нужные скалярные поля (например, через DTO или словарь), собранные внутри контекста сессии. Файлы: `bot/handlers/start.py`, `bot/handlers/menu.py`.

---

## [AP-003] Вызов edit_text без проверки изменения контента

**Описание:** В обработчиках callback в `bot/handlers/menu.py` всегда вызывается `callback.message.edit_text(...)`. Telegram API возвращает ошибку, если новое содержимое сообщения (текст и/или reply_markup) совпадает со старым. Обработчик не проверяет, изменился ли контент, и не обрабатывает исключение «Message is not modified».

**Статус:** закрыто.

**Решение:** Введена функция `_safe_edit_text(message, text, reply_markup)`: вызов `message.edit_text(...)` и перехват `TelegramBadRequest`; если в тексте ошибки есть «message is not modified», исключение игнорируется, иначе пробрасывается. Все вызовы `edit_text` в обработчиках меню заменены на `_safe_edit_text`. Файл: `bot/handlers/menu.py`.

---

## [AP-004] Обращение к результату scalar_one_or_none() как к Row (row[0])

**Описание:** В `database/task_repo.py` в функции `get_nearest_deadline` результат `result.scalar_one_or_none()` сохраняется в `row`, затем возвращается `row[0] if row else None`. Для запроса с одной колонкой `select(Task.deadline)` метод `scalar_one_or_none()` в SQLAlchemy 2.0 возвращает скалярное значение (например, `datetime`), а не объект Row. Обращение `row[0]` к скаляру приводит к `TypeError` при наличии хотя бы одной активной задачи.

**Статус:** закрыто.

**Решение:** Возвращать скаляр напрямую: `return result.scalar_one_or_none()`. Файл: `database/task_repo.py`.

---

## [AP-005] Дублирование функции _safe_edit в нескольких модулях

**Описание:** Одна и та же логика «edit_text + перехват TelegramBadRequest для "message is not modified"» реализована отдельно в `bot/handlers/task_create.py` (`_safe_edit`) и в `bot/handlers/task_list.py` (`_safe_edit`). В `bot/handlers/menu.py` используется своя функция `_safe_edit_text`. Три копии усложняют поддержку и повышают риск расхождений при изменении поведения.

**Статус:** закрыто.

**Решение:** Вынесена общая функция `safe_edit_text(message, text, reply_markup)` в модуль `bot/safe_edit.py`. Обработчики в `menu.py`, `task_create.py` и `task_list.py` импортируют и используют её; локальные копии удалены.

---

## [AP-006] HTTP-запросы внутри транзакции БД

**Статус:** Исправлено

**Описание:** В `bot/logic/tasks.py` внутри контекста `async with async_session()`: (транзакция) выполняется отправка сообщений в Telegram (`await bot.send_message(...)`). Сетевые запросы могут быть медленными, что удерживает транзакцию и соединение с БД дольше необходимого, снижая пропускную способность и увеличивая риск блокировок.

**Решение:** Логика разделена на два этапа: (1) В транзакции собираются данные и обновляется состояние. Уведомления сохраняются в список `notifications`. (2) После `commit()` и выхода из контекста сессии выполняется цикл отправки сообщений из списка `notifications`. Файл: `bot/logic/tasks.py`.

---

## [AP-007] Устаревшие комментарии в коде

**Описание:** В `database/task_repo.py` для функции `complete_task` сохранен комментарий `Phase 2: no XP`, хотя в текущей версии проекта XP уже начисляется в вызывающем коде (handlers). Это вводит в заблуждение при чтении кода репозитория.

**Статус:** открыто.

**Решение:** Актуализировать комментарии в соответствии с текущим этапом реализации (Phase 5).

---

## [AP-008] Использование Emoji в консольном выводе тестов без явной кодировки

**Описание:** Скрипты верификации (например, `tests/verify_phase5.py`) используют символы Emoji (✅, ❌, █) в `print()`. На Windows это приводит к `UnicodeEncodeError`, если не установлена переменная окружения `PYTHONIOENCODING=utf-8`. Это затрудняет запуск тестов "из коробки" в различных окружениях.

**Статус:** открыто.

**Решение:** Либо избегать использования сложных Unicode-символов в консольном выводе, либо добавить в начало скриптов инициализацию, обеспечивающую корректную работу с UTF-8 в консоли.

---

## [AP-009] Неполный regex для парсинга дней в deadline_parser

**Описание:** В `bot/deadline_parser.py` regex для парсинга "через N дней" был `r'через\s+(\d+)\s+дн'`, что не соответствовало полному слову "день" (только "дн"). При вводе "через 1 день" парсер возвращал `None`, хотя "через 2 дня" и "через 5 дней" работали корректно.

**Статус:** закрыто.

**Причина:** Regex `дн` соответствовал только началам слов "дня", "дней", но не полному слову "день".

**Решение:** Regex изменён на `r'через\s+(\d+)\s+(дн|день)'` для поддержки всех вариантов написания. Файл: `bot/deadline_parser.py`.

---

## [AP-010] Смешивание timezone-aware и naive datetime

**Описание:** При сохранении задачи в БД возникала ошибка `can't subtract offset-naive and offset-aware datetimes`. Функция `parse_deadline` возвращает datetime с tzinfo, а модель использует `TIMESTAMP WITHOUT TIME ZONE` с naive datetime по умолчанию.

**Статус:** закрыто.

**Причина:** Несогласованность между парсером дедлайнов (возвращает aware datetime) и моделью БД (ожидает naive datetime). asyncpg не может обработать смешивание aware и naive datetime в одном SQL-запросе.

**Решение:** В функции `create_task` добавлено удаление tzinfo перед сохранением: `if deadline.tzinfo is not None: deadline = deadline.replace(tzinfo=None)`. Альтернативное решение — использовать `TIMESTAMP WITH TIME ZONE` в модели. Файл: `database/task_repo.py`.

---

## [AP-011] Использование selectinload для несуществующего relationship

**Описание:** В `database/task_repo.py` функции `get_overdue_tasks` и `get_tasks_for_reminder` используют `selectinload(Task.user)`, но relationship не был определён в модели `Task`. Это приводило к `AttributeError: type object 'Task' has no attribute 'user'`.

**Статус:** закрыто.

**Причина:** Код репозитория был написан с предположением о наличии relationship, но модель не содержала его определения.

**Решение:** В модель `Task` добавлен relationship: `user = relationship("User", backref="tasks")`. Также добавлен импорт `relationship` из `sqlalchemy.orm`. Файл: `database/models.py`.

---

## [AP-012] Сравнение naive и aware datetime в функциях форматирования

**Описание:** В `bot/time_utils.py` функции `format_remaining` и `format_remaining_short` использовали `get_now_utc()` (возвращает timezone-aware datetime) для сравнения с `deadline` из БД, который хранится как naive UTC datetime. Это приводило к `TypeError: can't compare offset-naive and offset-aware datetimes`.

**Статус:** закрыто.

**Причина:** Несогласованность между источниками времени: `get_now_utc()` возвращает aware datetime, а БД хранит naive datetime.

**Решение:** Заменено использование `get_now_utc()` на `datetime.utcnow()` в функциях сравнения. В `format_deadline_date` добавлено приведение naive datetime к aware перед `astimezone()`. Файл: `bot/time_utils.py`.

