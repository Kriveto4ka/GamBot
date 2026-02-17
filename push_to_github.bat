@echo off
chcp 65001 >nul
cd /d "%~dp0"

where git >nul 2>&1
if errorlevel 1 (
    echo Git не найден. Установите: https://git-scm.com/download/win
    pause
    exit /b 1
)

if not exist .git (
    git init
    git add .
    git commit -m "Initial commit: GamificateBot"
    git branch -M main
    git remote add origin https://github.com/Kriveto4ka/GamificateBot.git
) else (
    git add .
    git status
    git commit -m "Update: GamificateBot" 2>nul || echo Nothing to commit
    git remote remove origin 2>nul
    git remote add origin https://github.com/Kriveto4ka/GamificateBot.git
)

echo.
echo Пуш в https://github.com/Kriveto4ka/GamificateBot.git ...
git push -u origin main

if errorlevel 1 (
    echo.
    echo Если репозиторий уже есть с файлами, выполните вручную:
    echo   git pull origin main --allow-unrelated-histories
    echo   git push -u origin main
)
pause
