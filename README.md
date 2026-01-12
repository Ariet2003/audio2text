# Telegram Bot для управления задачами через аудио

Профессиональный Telegram бот на Aiogram для добавления задач через голосовые сообщения с интеграцией Google Sheets.

## Возможности

- 🎤 Распознавание речи из аудио файлов (русский язык)
- ➕ Добавление задач в Google Sheets через голосовые сообщения
- 📋 Просмотр всех задач из Google Sheets
- 🔗 Прямая ссылка на Google Sheet

## Установка

1. Клонируйте репозиторий или скачайте файлы проекта

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите дополнительные зависимости для работы с аудио:
```bash
# Для macOS
brew install portaudio ffmpeg

# Для Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio ffmpeg

# Для Windows
# 1. Скачайте и установите PyAudio wheel с https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# 2. Скачайте и установите ffmpeg с https://ffmpeg.org/download.html
#    Добавьте ffmpeg в PATH
```

## Настройка

### 1. Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота

### 2. Google Sheets API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API и Google Drive API
4. Создайте Service Account:
   - Перейдите в "IAM & Admin" → "Service Accounts"
   - Создайте новый Service Account
   - Скачайте JSON файл с ключами (credentials.json)
5. Создайте Google Sheet и поделитесь им с email из Service Account (дайте права редактора)
6. Скопируйте ID Sheet из URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

### 3. Конфигурация

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Заполните `.env` файл:
```
BOT_TOKEN=ваш_токен_бота
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=ваш_sheet_id
GOOGLE_SHEET_NAME=Tasks
GOOGLE_SHEET_LINK=https://docs.google.com/spreadsheets/d/ваш_sheet_id/edit
```

3. Поместите `credentials.json` в корневую директорию проекта

## Запуск

```bash
python bot.py
```

## Структура проекта

```
audio2text/
├── bot.py                 # Основной файл бота
├── config.py              # Конфигурация
├── audio_recognizer.py    # Модуль распознавания речи
├── google_sheets.py       # Модуль работы с Google Sheets
├── main.py                # Оригинальный файл распознавания
├── requirements.txt       # Зависимости
├── .env                   # Переменные окружения (не в git)
├── .env.example           # Пример конфигурации
├── credentials.json       # Google Service Account ключи (не в git)
└── README.md              # Документация
```

## Использование

1. Запустите бота командой `/start`
2. Используйте кнопки меню:
   - **➕ Добавить задачу** - отправьте голосовое сообщение или аудио файл
   - **📋 Посмотреть задачи** - просмотрите все задачи из Google Sheet
   - **🔗 Ссылка на Google sheet** - получите прямую ссылку на таблицу

## Технологии

- **Aiogram 3.3** - современный фреймворк для Telegram ботов
- **SpeechRecognition** - библиотека для распознавания речи
- **gspread** - библиотека для работы с Google Sheets API
- **python-dotenv** - управление переменными окружения

## Лицензия

MIT
