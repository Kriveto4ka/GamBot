# DNA Map: GameTODO Bot
DNA Map связывает требования проекта (из SPEC.md), этапы реализации, техническую документацию и тесты. Документ помогает быстро найти соответствие между функциональными требованиями и их реализацией.

---

## 1. Общие требования

| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| **NR7** — Токен бота в переменных окружения | SPEC.md (4.3. Безопасность) | config.py, main.py | Проверка в тестах, переменная окружения BOT_TOKEN |
| **NR9** — База данных PostgreSQL в Docker | SPEC.md (4.4. Инфраструктура) | docker-compose.yml, Dockerfile | Запуск через docker-compose up |

---

## 2. Этап 1: Базовый бот

### Функциональные требования
| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| **R6** — Просмотр статуса персонажа | SPEC.md (3.2), phase-1.md | bot/handlers/menu.py, bot/texts.py | tests/test_character.py |
| **R12** — Работа через inline-кнопки | SPEC.md (3.4), phase-1.md | bot/keyboards.py, main.py | Тесты на начальное взаимодействие |
| **R13** — Главное меню после /start | SPEC.md (3.4), phase-1.md | bot/handlers/start.py, bot/texts.py | Тест на /start и главное меню |
| **R17** — Экран персонажа | SPEC.md (3.4), phase-1.md | bot/handlers/menu.py | tests/test_character.py |

### Тестирование
- Проверка создания персонажа: tests/test_character.py
- Проверка главного меню: tests/test_menu.py (имплицитно в start)

---

## 3. Этап 2: Управление задачами

### Функциональные требования
| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| **R1** — Создание задачи | SPEC.md (3.1), phase-2.md | bot/handlers/task_create.py, database/task_repo.py | Тесты на FSM создания |
| **R2** — Просмотр списка задач | SPEC.md (3.1), phase-2.md | bot/handlers/task_list.py | Тест на список задач |
| **R3** — Отметить выполненной | SPEC.md (3.1), phase-2.md | bot/handlers/task_list.py, database/task_repo.py | Тест на выполнение задачи |
| **R4** — Удалить задачу | SPEC.md (3.1), phase-2.md | bot/handlers/task_list.py, database/task_repo.py | Тест на удаление |
| **R5** — Просмотр просроченных | SPEC.md (3.1), phase-2.md | bot/handlers/task_list.py | Тест на просроченные |
| **R14** — Пошаговый процесс создания | SPEC.md (3.4), phase-2.md | bot/handlers/task_create.py (FSM) | Тесты на FSM создания |
| **R15** — Быстрый выбор дедлайна | SPEC.md (3.4), phase-2.md | bot/keyboards.py, bot/handlers/task_create.py | Тест на дедлайн |
| **R16** — Детали задачи | SPEC.md (3.4), phase-2.md | bot/handlers/task_list.py, bot/texts.py | Тест на детали |
| **R20** — Парсер дедлайнов | SPEC.md (3.4), phase-2.md | bot/deadline_parser.py | tests/test_deadline_parser.py |

### Граничные случаи
| Кейс | Где описано | Где реализовано | Чем проверяется |
|------|--------------|-----------------|------------------|
| **E1** — Дедлайн в прошлом | SPEC.md (5.1), phase-2.md | bot/deadline_parser.py | tests/test_deadline_parser.py |
| **E2** — Пустое название | SPEC.md (5.1), phase-2.md | bot/handlers/task_create.py | Тест на создание |
| **E3** — Название >200 символов | SPEC.md (5.1), phase-2.md | bot/handlers/task_create.py | Тест на создание |
| **E4** — Некорректный формат даты | SPEC.md (5.1), phase-2.md | bot/deadline_parser.py | tests/test_deadline_parser.py |
| **E6** — Задача не существует | SPEC.md (5.2), phase-2.md | bot/handlers/task_list.py | Тест на детали |
| **E7** — Нет активных задач | SPEC.md (5.2), phase-2.md | bot/handlers/task_list.py | Тест на список задач |

### Тестирование
- Парсер дедлайнов: tests/test_deadline_parser.py
- Логика задач: tests/test_task_repo.py

---

## 4. Этап 3: Игровая механика

### Функциональные требования
| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| **2.2** — Система уровней | SPEC.md (2.2), phase-3.md | bot/logic/game.py | tests/test_game_logic.py |
| **2.3** — Сложности и награды | SPEC.md (2.3), phase-3.md | config.py, bot/logic/game.py | tests/test_game_logic.py |
| **2.4** — Механика урона | SPEC.md (2.4), phase-3.md | bot/logic/tasks.py | tests/test_game_logic.py |
| **2.5** — Смерть персонажа | SPEC.md (2.5), phase-3.md | bot/logic/game.py, bot/logic/tasks.py | tests/test_game_logic.py |
| **NR2** — Проверка дедлайнов каждые 5 минут | SPEC.md (4.1), phase-3.md | main.py (APScheduler), bot/logic/tasks.py | Тест на планировщик |

### Тестирование
- Игровая механика: tests/test_game_logic.py
- Логика задач: tests/test_tasks.py

---

## 5. Этап 4: Смерть и уведомления

### Функциональные требования
| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| **R8** — Напоминание за 1 час | SPEC.md (3.3), phase-4.md | bot/logic/notifications.py | Тест на напоминания |
| **R9** — Уведомление о просрочке | SPEC.md (3.3), phase-3.md | bot/logic/tasks.py | Тест на уведомления |
| **R10** — Уведомление о level-up | SPEC.md (3.3), phase-4.md | bot/handlers/task_list.py | Тест на выполнение задач |
| **R11** — Уведомление о смерти | SPEC.md (3.3), phase-4.md | bot/logic/tasks.py | Тест на смерть персонажа |

### Механика смерти
| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| Сброс уровня | SPEC.md (2.5), phase-4.md | bot/logic/game.py | tests/test_game_logic.py |
| Сброс XP | SPEC.md (2.5), phase-4.md | bot/logic/game.py | tests/test_game_logic.py |
| Восстановление HP | SPEC.md (2.5), phase-4.md | bot/logic/game.py | tests/test_game_logic.py |
| Удаление активных задач | SPEC.md (2.5), phase-4.md | bot/logic/tasks.py, database/task_repo.py | Тест на смерть персонажа |

### Тестирование
- Уведомления: tests/test_notifications.py
- Смерть персонажа: tests/test_game_logic.py

---

## 6. Этап 5: Статистика и polish

### Функциональные требования
| Требование | Где описано | Где реализовано | Чем проверяется |
|------------|--------------|-----------------|------------------|
| **R7** — Статистика пользователя | SPEC.md (3.2), phase-5.md | bot/handlers/statistics.py, database/user_repo.py | Тест на статистику |
| **R18** — Экран статистики | SPEC.md (3.4), phase-5.md | bot/handlers/statistics.py, bot/texts.py | Тест на статистику |

### Граничные случаи
| Кейс | Где описано | Где реализовано | Чем проверяется |
|------|--------------|-----------------|------------------|
| **E5** — Просроченная задача выполнена | SPEC.md (5.2), phase-5.md | bot/handlers/task_list.py | Тест на выполнение |

### Тестирование
- Статистика: tests/test_statistics.py

---

## 7. Архитектура и технологии

| Компонент | Где описано | Где реализовано | Чем проверяется |
|-----------|--------------|-----------------|------------------|
| **MVC-like слои** | ARCHITECTURE.md | bot/ (presentation), bot/logic/ (business), database/ (data access) | Код-ревью, соответствие структуре |
| **База данных** | DNA.md, ARCHITECTURE.md | database/models.py, database/engine.py | Проверка на миграции, интеграционные тесты |
| **Конфигурация** | DNA.md | config.py | Проверка переменных окружения |

---

## 8. Антипаттерны и ошибки

| Антипаттерн | Где описано | Где исправлено | Чем проверяется |
|--------------|--------------|-----------------|------------------|
| Смешивание naive и aware дат | ANTIPATTERNS.md | bot/time_utils.py, database/task_repo.py | Тест на дедлайны |
| Отсутствие relationship в модели | ANTIPATTERNS.md | database/models.py | Тест на репозиторий задач |
| HTTP-запросы внутри транзакции | ANTIPATTERNS.md | bot/logic/tasks.py | Тесты на задачи |
| Message is not modified | ANTIPATTERNS.md | bot/safe_edit.py | Тесты на редактирование сообщений |
