# Homework Bot
Бот-ассистент для Telegram.
Позволяет удобно отслеживать статус проекта через telegram.

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
git@github.com:Wiz410/homework_bot.git
cd homework_bot
```

Создайте файл `.env`:
```bash
touch .env
```

И заполните его:
```env
PRACTICUM_TOKEN=API_Token_YP https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a.
TELEGRAM_TOKEN=API_Token https://t.me/BotFather
TELEGRAM_CHAT_ID=ID_user https://t.me/userinfobot
```

Запустите бота:
```bash
python homework.py
```

#### Авторы
- [Danila Polunin](https://github.com/Wiz410)