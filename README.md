# Романов Олег 11-906

Для того, чтобы отправить обработанное изображение в новый бакет, используется код, который можно найти в файле send_completed_photo.py (Необходимо подставить aws keys).

Созданы бакеты itis-2022-2023-vvot38-photos и itis-2022-2023-vvot38-faces

Создана база даннынных vvot38-db-photo-face в сервисе «Yandex Managed Service for YDB»

В файле api-gateway описана конфигурация GATEWAY.

В файле photo_processing_function.py описана функция для получения данных для обработки

Dockerfile - докерфайл для контейнера:
```
.docker % docker build . -t cr.yandex/crploaenhl6f940c9kpu/vvot38
```
```
.docker % docker push cr.yandex/crploaenhl6f940c9kpu/vvot38:latest
```
Был создан контейнер vvot38-face-cut по загруженному образу и с переменными окружения AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY.

Создан тригер с именем vvot38-task-trigger

В Telegram был создан бот с помощью бота @BotFather и был получен token. Далее создан Webhook посредством вставивки значения в ссылку. ссылка:
https://api.telegram.org/bot{token}/setWebhook?url={СсылкаДляВызоваФункции"vvot38-boot"}

