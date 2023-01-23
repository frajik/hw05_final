# Проект "Yatube"

## Описание проекта:
 **Проект Yatube** - социальная сеть для блогеров, с возможностью публикаций постов, подписки на группы и авторов, а также комментирования постов.

## Используемые технологии:
- [Python 3.7](https://www.python.org/)
- [Django 2.2.16](https://www.djangoproject.com/)


## Как запустить проект:
1. Клонируем репозиторий к себе на компьютер:
```
    git@github.com:frajik/hw05_final.git
```

2. Переходим в репозиторий:
```
    cd hw05_final
```

3. Создаем и активируем рабочее окружение:
```
    - python -m venv venv
    - source venv/scripts/activate
```

4. Устанавливаем зависимости из файла requirements.txt:
```
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt
```

5. Выполняем миграции:
```
    - python manage.py migrate
```

6. Запускаем проект:
```
    - python manage.py runserver
```

## Возможности пользователей:
### Анонимный пользователь:
  - Просматривать публикации;
  - Просматривать информацию о сообществах;
  - Просматривать комментарии;

### Авторизованный пользователь:
  - Просматривать, публиковать, удалять и редактировать свои публикации;
  - Просматривать информацию о сообществах;
  - Просматривать и публиковать комментарии от своего имени к публикациям других пользователей (включая самого себя), удалять и редактировать свои комментарии;
  - Подписываться на других пользователей и просматривать свои подписки.
  - Примечание: Доступ ко всем операциям записи, обновления и удаления доступны только после аутентификации и получения токена.


## Достпуные эндпоинты:
  - **posts/** - Отображение постов и публикаций (GET, POST);
  - **posts/{id}** - Получение, изменение, удаление поста с соответствующим id (GET, PUT, PATCH, DELETE);
  - **posts/{post_id}/comments/** - Получение комментариев к посту с соответствующим post_id и публикация новых комментариев(GET, POST);
  - **posts/{post_id}/comments/{id}** - Получение, изменение, удаление комментария с соответствующим id к посту с соответствующим post_id (GET, PUT, PATCH, DELETE);
  - **posts/groups/** - Получение описания зарегестрированных сообществ (GET);
  - **posts/groups/{id}/** - Получение описания сообщества с соответствующим id (GET);
  - **posts/follow/** - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя (GET, POST).
