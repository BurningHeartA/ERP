# ERP-система для ООО «Экструзионное оборудование»

Прототип системы планирования ресурсов для малого металлообрабатывающего предприятия. Выпускная квалификационная работа.

## Состав проекта

| Компонент | Технологии | Назначение |
|-----------|-----------|------------|
| `backend/` | Python, Django, Django REST Framework | REST API, бизнес-логика, база данных |
| `desktop/` | Python, PyQt5 | Десктопное приложение для сотрудников |
| `web/` | JavaScript, React | Веб-портал для клиентов |

## Системные требования

- **ОС:** Windows 10/11
- **Python:** 3.10 или выше
- **Node.js:** 18 или выше (для веб-портала)
- **Свободное место:** ~400 МБ

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/DepartmentOfSoftwareEngineeringFEFU/B9122-02.03.03_TP-Grishkov_Leonid_Petrovich.git
cd B9122-02.03.03_TP-Grishkov_Leonid_Petrovich
```

### 2. Установить Python-зависимости

```bash
python -m venv venv
source venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Подготовить базу данных и запустить сервер (из корня проекта)

```bash

cd backend
python manage.py reset_db
python manage.py runserver
```
Сервер будет доступен по адресу http://127.0.0.1:8000/

### 4. Запустить десктопное приложение (второй терминал, из корня проекта)

```bash

source venv\Scripts\activate
cd desktop
python main.py
```

### 5. Запустить веб-портал (третий терминал, опционально)

```bash
source venv\Scripts\activate
cd web
npm install
npm run dev
```
Веб-портал будет доступен по адресу http://localhost:5173/


## Данные для входа

| Роль | Логин | Пароль |
|-----------|-----------|------------|
| Директор | director | director |
| Сотрудник | antonov_sp | employee123 (пароль для всех рядовых сотрудников) |
| Клиент | client1 | client123 (пароль для всех клиентов, не являющихся сотрудниками) |

Список логинов других Сотрудников, а также Клиентов, можно посмотреть в адмиин-панели Django по адресу http://127.0.0.1:8000/admin/ (вход доступен только для Директора).

## Интерфейс проекта

Со скриншотами интерфейса проекта вы можете ознакомиться в screenshots.pdf или отдельно в папке screnshots/