# Анонимный Telegram Чат-бот

Бот для анонимной коммуникации между пользователями через Telegram.

## Что умеет бот

- Пересылает сообщения анонимно в канал и другим пользователям
- Поддерживает текст, фото, стикеры, видеокружки и пересланные сообщения
- Сохраняет форматирование текста
- Простая регистрация через команду /start

## Установка и запуск

### Подготовка

1. Создайте бота через [@BotFather](https://t.me/botfather) и получите токен бота

2. Создайте канал в Telegram и добавьте вашего бота как администратора

3. Получите ID канала:
   - Отправьте любое сообщение в ваш канал
   - Перешлите это сообщение боту [@getidsbot](https://t.me/getidsbot)
   - Найдите значение "Forwarded from chat" в ответе бота - это ID вашего канала

### Способ 1: Установка через Docker (рекомендуется)

1. Установите Docker:
   - Через [Docker Desktop](https://www.docker.com/products/docker-desktop/) на Windows или Mac
   - Или через Homebrew (только на Mac): `brew install --cask docker`

2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Danyache/telegram_anonymous_chat_bot.git
   cd telegram_anonymous_chat_bot
   ```

3. Настройте файл `.env`:
   - Скопируйте пример конфигурации вручную, удалив расширение файла или следующей командой: `cp .env.example .env`
   - Откройте файл `.env` в любом текстовом редакторе
   - Замените значения `BOT_TOKEN` и `CHANNEL_ID` на ваши данные

4. Запустите бота:
   ```bash
   docker-compose up -d
   ```

5. Проверьте, что бот работает:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

### Способ 2: Запуск без Docker

1. Установите Python 3.7 или новее

2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Danyache/telegram_anonymous_chat_bot.git
   cd telegram_anonymous_chat_bot
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте файл `.env`:
   - Скопируйте пример конфигурации: `cp .env.example .env`
   - Откройте файл `.env` в любом текстовом редакторе
   - Замените значения BOT_TOKEN и CHANNEL_ID на ваши данные

5. Запустите бота:
   ```bash
   python bot.py
   ```

## Перезапуск и обновление

### Для Docker:

```bash
# Перезапуск
docker-compose restart

# Обновление (после внесения изменений)
docker-compose down
docker-compose up -d --build
```

### Без Docker:

```bash
# Остановите текущий процесс (Ctrl+C)
# Запустите заново
python bot.py
```

## Устранение неполадок

Если сообщения не отправляются в канал:
1. Убедитесь, что бот добавлен в канал как администратор
2. Проверьте правильность ID канала в файле .env
3. Запустите команду `/testchannel` в чате с ботом
4. Проверьте логи: `docker-compose logs` или файл `logs/bot.log`
