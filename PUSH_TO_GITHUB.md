# Пуш бота в GitHub

Репозиторий: **https://github.com/Kriveto4ka/GamificateBot.git**

## 1. Установите Git (если ещё не установлен)

- Скачайте: https://git-scm.com/download/win  
- Установите и **перезапустите терминал** (или Cursor).

## 2. Выполните команды в папке проекта

Откройте терминал в `c:\Users\sevak\Desktop\TgBot` и выполните по порядку:

```bash
git init
git add .
git commit -m "Initial commit: GamificateBot"
git branch -M main
git remote add origin https://github.com/Kriveto4ka/GamificateBot.git
git push -u origin main
```

GitHub запросит логин и **Personal Access Token** (пароль от аккаунта больше не подходит — создайте токен в GitHub → Settings → Developer settings → Personal access tokens).

Если репозиторий на GitHub уже создан и в нём есть файлы (например, README), сначала выполните:

```bash
git pull origin main --allow-unrelated-histories
```

затем снова:

```bash
git push -u origin main
```

## Вариант через SSH

Если настроен SSH-ключ в GitHub:

```bash
git remote add origin git@github.com:Kriveto4ka/GamificateBot.git
```
