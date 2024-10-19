# Проект Foodgram

## Описание

**Foodgram** - это проект, посвященный рецептам. Пользователи могут создавать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок», позволяющий создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

## Функциональность

- Создание своих рецептов с указанием ингредиентов и описанием способа приготовления;
- Просмотр рецептов других пользователей с возможностью фильтрации по тегам;
- Добавление рецептов в избранное;
- Подписка на других авторов и просмотр их рецептов в ленте подписок;
- Создание и загрузка списка покупок, автоматически формирующегося на основе добавленных рецептов;

## Ресурсы API

1. Пользователи:
   - `GET /api/users/` - Список пользователей
   - `POST /api/users/` - Регистрация пользователя
   - `GET /api/users/{id}/` - Профиль пользователя
   - `GET /api/users/me/` - Текущий пользователь
   - `PUT /api/users/me/avatar/` - Добавление аватара
   - `DELETE /api/users/me/avatar/` - Удаление аватара
   - `POST /api/users/set_password/` - Изменение пароля

2. Теги:
   - `GET /api/tags/` - Список тегов
   - `GET /api/tags/{id}/` - Получение тега

3. Рецепты:
   - `GET /api/recipes/` - Список рецептов
   - `POST /api/recipes/` - Создание рецепта
   - `GET /api/recipes/{id}/` - Получение рецепта
   - `PATCH /api/recipes/{id}/` - Обновление рецепта
   - `DELETE /api/recipes/{id}/` - Удаление рецепта
   - `GET /api/recipes/{id}/get-link/` - Получить короткую ссылку на рецепт

4. Избранное:
   - `POST /api/recipes/{id}/favorite/` - Добавить рецепт в избранное
   - `DELETE /api/recipes/{id}/favorite/` - Удалить рецепт из избранного

5. Список покупок:
   - `POST /api/recipes/{id}/shopping_cart/` - Добавить рецепт в список покупок
   - `DELETE /api/recipes/{id}/shopping_cart/` - Удалить рецепт из списка покупок
   - `GET /api/recipes/download_shopping_cart/` - Скачать список покупок

6. Подписки:
   - `GET /api/users/subscriptions/` - Мои подписки
   - `POST /api/users/{id}/subscribe/` - Подписаться на пользователя
   - `DELETE /api/users/{id}/subscribe/` - Отписаться от пользователя

7. Ингредиенты:
   - `GET /api/ingredients/` - Список ингредиентов
   - `GET /api/ingredients/{id}/` - Получение ингредиента

8. Аутентификация:
   - `POST /api/auth/token/login/` - Получить токен авторизации
   - `POST /api/auth/token/logout/` - Удаление токена

## Установка и запуск проекта

### Клонирование репозитория

```bash
git clone https://github.com/olejnikoves3/foodgram.git
```

### Настройка переменных окружения

В корневой директории создайте файл `.env` с содержимым:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram_pwd
DB_NAME=foodgram

DB_HOST=db
DB_PORT=5432
```

### Запуск приложения локально в Docker

В корневой дирректории выполните команду:

```bash
docker compose up -d --build
```

### Доступ к приложению

Приложение будет доступно по адресу: `http://localhost:8000/`