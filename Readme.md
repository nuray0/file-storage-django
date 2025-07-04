# 📁 Сервис-хранилище файлов на Django

Этот проект — REST-сервис на Django для загрузки и скачивания файлов. Загруженные файлы разбиваются на части, архивируются, сохраняются на диск и логируются в базу данных.

---

## 📌 Технические требования

- **Python**: 3.12.8  
- **Фреймворк**: Django  
- **База данных**: SQLite (по умолчанию)  
- **Доп. библиотеки**: только стандартные библиотеки Python  
- **Максимальный размер файла**: 16 МБ  
- **Архивирование**: `.zip`, до 16 частей  
- **Логирование действий**: модель `ActionLog`

---

## 🚀 Запуск проекта

1. Создайте виртуальное окружение и активируйте ее:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Примените миграции:
   ```bash
   python manage.py migrate
   ```

4. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

---

## 📤 Загрузка файла

Пример curl-запроса:
```bash
curl -F "file=@/путь/к/вашему/test_file.txt" http://127.0.0.1:8000/upload/
```
Для теста можно загрузить тестовый файл из директории проекта
```bash
curl -F "file=@test_file.txt" http://127.0.0.1:8000/upload/
```


Пример успешного ответа:
```json
{
  "message": "File uploaded and archived",
  "archive_name": "test_file_xxx.zip",
  "original_filename": "test_file",
  "file_extension": "txt",
  "download_url": "http://127.0.0.1:8000/download/test_file_xxx.zip"
}
```

---

## 📥 Получение файла - 2 способа

1. Через curl (подставьте download_url из ответа на загрузку):
```bash
curl -L http://127.0.0.1:8000/download/test_file_xxx.zip \
  --output your_filename.txt
```
2. Через браузер:
Откройте ссылку download_url из ответа, например:
http://127.0.0.1:8000/download/test_file_xxx.zip

Файл будет собран из архива и возвращён в исходном виде.

---

## 🗂 Структура проекта

```
file_storage_project_django/
├── file_storage/
│   ├── views.py
│   ├── models.py
│   ├── urls.py
│   └── test_file_storage.py
├── file_storage_project/
│   └── settings.py
├── media/
│   ├── input/
│   └── output/
├── manage.py
├── requirements.txt
└── Readme.md
```

---

## 📎 Примечания

- Проект использует только стандартные библиотеки Python и Django.  
- Поддержка одного пользователя (без авторизации).  
- Ошибки корректно обрабатываются:
  - превышен размер файла  
  - не найден архив  

---

## 🔧 Возможности для улучшения

- Авторизация и сохранение `user_id`  
- Загрузка в базу данных вместо файловой системы  
- Контейнеризация через Docker  
- Поддержка CI/CD  

---

## 🧪 Тестирование

```bash
python manage.py test
```

Покрытие: загрузка, скачивание, превышение лимита, ошибки.
