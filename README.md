# Homework Bot
Бот-ассистент для Telegram — удобный способ отслеживать статус проекта.

Бот может:
- Опрашивать раз в 10 минут API Практикум Домашка.
- Анализировать ответ API и отправлять соответствующее сообщением в Telegram.
- Логировать свою работу и сообщать о важных проблемах сообщением в Telegram.

## Технологии
- [Python 3.9.10](https://docs.python.org/3.9/index.html)
- [Python-telegram-bot 13.7](https://pypi.org/project/python-telegram-bot/13.7/)
- [Python-dotenv 0.19.0](https://pypi.org/project/python-dotenv/0.19.0/)
- [Logging 0.5.1.2](https://docs.python.org/3.9/library/logging.html)

### Запуск проекта
Клонируйте проект и перейдите в его директорию:
```bash
git clone git@github.com:Wiz410/homework_bot.git
cd homework_bot
```

Cоздайте и активируйте виртуальное окружение:
- Для Windows
```bash
python -m venv venv
source venv/Scripts/activate
```

- Для Linux и macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости из файла `requirements.txt`:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создайте файл `.env`:
```bash
touch .env
```

И заполните его:
```env
PRACTICUM_TOKEN=API_Token_YP ...
TELEGRAM_TOKEN=API_Token https://t.me/BotFather
TELEGRAM_CHAT_ID=ID_user https://t.me/userinfobot
```

Запустите бота:
```bash
python homework.py
```

#### Автор
- [Danila Polunin](https://github.com/Wiz410)
