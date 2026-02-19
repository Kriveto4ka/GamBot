# Результаты этапа 2: Управление задачами

## Статус: выполнен

## Критерии готовности (из phase-2.md)

| Критерий | Статус |
|----------|--------|
| «Новая задача» запускает пошаговый процесс; можно отменить на любом шаге | ✅ |
| Название: пустое — ошибка (E2), >200 — обрезка + уведомление (E3) | ✅ |
| Сложность выбирается кнопками (4 варианта) | ✅ |
| Дедлайн: быстрые кнопки и ручной ввод; прошлое — ошибка (E1), неверный формат — повтор с примерами (E4) | ✅ |
| «Мои задачи»: список кнопками или сообщение «Нет активных задач» (E7) | ✅ |
| Клик по задаче — детали; «Выполнено» помечает выполненной (без XP), «Удалить» — удаляет (R4) | ✅ |
| «Просроченные» — список просроченных задач (R5) | ✅ |
| В главном меню отображается число активных задач; на экране персонажа — число задач и ближайший дедлайн | ✅ |
| Данные задач сохраняются в БД (NR4) | ✅ |

## Реализованные компоненты

### Модели и БД

- **database/models.py**: модель **Task** (SPEC 7.2): user_id, title(200), difficulty, deadline, status (active/completed/failed/deleted), completed_at. Enum TaskDifficulty, TaskStatus.
- **database/task_repo.py**: create_task, get_active_tasks, get_failed_tasks, count_active, get_task_by_id, get_nearest_deadline, complete_task (phase 2: только смена статуса + total_completed), delete_task.
- Таблица `tasks` создаётся через init_db (Base.metadata.create_all).

### Парсинг дедлайнов (R20, E1, E4)

- **bot/deadline_parser.py**: parse_deadline(text, now) — форматы «завтра 18:00», «сегодня 21:00», «25.01 15:30», «25.01.2025 15:30», «через 2 часа», «через 1 день»; is_future(dt); format_deadline_examples(); TITLE_MAX_LEN=200.
- Время в UTC (часовой пояс пользователя — этап 4 по decisions.md).

### Константы и утилиты

- **bot/constants.py**: DIFFICULTY_LABELS, DIFFICULTY_XP_DAMAGE, format_difficulty_short (для экранов).
- **bot/time_utils.py**: format_remaining (осталось: 5ч 23мин), format_deadline_date (25.01, 18:00 / завтра, 18:00).

### Тексты (SPEC 8.5–8.10, E1–E7)

- **bot/texts.py**: task_list_header, task_list_empty, task_detail_message, task_created_message, task_completed_message_phase2; шаги создания (step1/2/3); ошибки empty_title, title_truncated, deadline_past, deadline_invalid, task_not_found; failed_tasks_header/empty.

### Клавиатуры

- **bot/keyboards.py**: cancel_keyboard, difficulty_keyboard, deadline_quick_keyboard (Через 1ч/3ч, Сегодня 21:00, Завтра 10:00/18:00, Ввести), task_created_keyboard, task_list_keyboard, task_detail_keyboard, task_list_item_keyboard, back_to_tasks_keyboard.

### FSM создания задачи

- **bot/handlers/task_create.py**: NewTaskStates (title → difficulty → deadline). Обработчики: task:new (старт), task:create_cancel, ввод названия (E2/E3), task:diff:* (выбор сложности), task:dl:* (быстрый дедлайн или ручной ввод), текст дедлайна (parse_deadline, E1/E4). _finish_create создаёт задачу и показывает 8.10.

### Список и действия с задачами

- **bot/handlers/task_list.py**: task:list (список активных или E7), task:detail:<id> (детали, E6), task:done:<id> (выполнено, phase 2 без XP), task:del:<id> (удалить), task:failed (список просроченных R5).

### Интеграция

- **bot/handlers/menu.py**: _get_user_and_tasks возвращает (user, active_count, next_deadline_text); главное меню и экран персонажа используют реальные count_active и get_nearest_deadline.
- **bot/handlers/start.py**: при повторном /start показывается главное меню с count_active.
- **main.py**: MemoryStorage для FSM, подключены task_create_router и task_list_router; заглушка «Скоро» только для «Статистика».

## Как проверить

1. **Новая задача**: Меню → Новая задача → ввести название → выбрать сложность → выбрать дедлайн (кнопка или текст). Отмена на любом шаге возвращает в меню.
2. **Пустое название**: ввод пустой строки → «Название не может быть пустым».
3. **Длинное название**: >200 символов → обрезка и уведомление, затем шаг сложности.
4. **Дедлайн в прошлом**: ввод прошедшей даты → «Дедлайн должен быть в будущем».
5. **Неверный формат даты**: произвольный текст → «Не удалось разобрать дату» + примеры.
6. **Мои задачи**: с задачами — список кнопками; без — «Нет активных задач». Клик по задаче — детали, «Выполнено» / «Удалить» / «К задачам».
7. **Просроченные**: кнопка в списке задач (на этапе 2 просроченных нет, т.к. нет scheduler).
8. **Меню и персонаж**: в меню отображается «Мои задачи (N)», на экране персонажа — «Активных задач: N», «Ближайший дедлайн: …».

## Ссылки на спецификацию

- R1–R5, R14–R16, R19–R20 — реализованы.
- E1–E4, E6, E7 — обработаны.
- Экраны 8.5–8.10 — реализованы.
- Этап 2 не включает начисление XP (этап 3) и проверку просрочки (этап 3); статус «просроченные» (failed) будет выставляться планировщиком.
