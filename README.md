# Taskroom

Taskroom is a focused task-management workspace. Users can create an account, manage their own tasks, filter and search them, track completion progress, and use the JSON API from an authenticated session.

## Technologies

- **Python 3.10+** and **Django 5** for the web application and authentication
- **Django REST Framework** for the task CRUD API
- **SQLite** for local persistence
- **HTML templates, CSS, and vanilla JavaScript** for the frontend
- **Django sessions and CSRF protection** for browser authentication and API requests

## Installation

From the project directory, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

On macOS or Linux, use the equivalent activation command:

```bash
source .venv/bin/activate
```

## Database Setup

Taskroom uses SQLite by default. Apply Django’s built-in and application migrations before the first run:

```powershell
python manage.py migrate
```

This creates the local `db.sqlite3` database, which is intentionally ignored by Git. To create an optional administrator account for `/admin/`:

```powershell
python manage.py createsuperuser
```

The normal first-time user flow is available at `/register/`; no admin account is required to use the task board.

## Run Locally

Start Django’s development server:

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. The main routes are:

- `/register/` - create an account
- `/login/` - sign in
- `/` - authenticated task workspace
- `/admin/` - Django administration
- `/api/tasks/` - authenticated task API

## Features And Technical Decisions

- Registration uses Django’s built-in `UserCreationForm`, including password confirmation and validation.
- A new account is signed in automatically after successful registration.
- Each task has an owner. API querysets are filtered by the authenticated user, preventing users from viewing or modifying another user’s tasks.
- The task board uses the Fetch API and a small vanilla JavaScript state layer, keeping the frontend dependency-free.
- Search, status filters, ordering, create, edit, complete, and delete operations are exposed through the DRF API.
- API task lists use page-number pagination with 20 tasks per page. Request another page with `?page=2`.
- The greeting and date are generated from Django’s timezone-aware clock and personalized with the signed-in username.
- The task dialog uses native HTML dialog behavior. Cancel controls are explicit non-submit buttons so they cannot accidentally save a task.
- SQLite keeps local development simple. A production deployment should use PostgreSQL or another managed database.

## API Reference

All endpoints require an authenticated Django session and JSON request bodies where applicable.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/tasks/` | List the signed-in user's tasks |
| `POST` | `/api/tasks/` | Create a task with `title`, `description`, `status`, `priority`, and optional `due_date` |
| `GET` | `/api/tasks/<id>/` | Retrieve one owned task |
| `PATCH` | `/api/tasks/<id>/` | Update selected fields |
| `PUT` | `/api/tasks/<id>/` | Replace an owned task |
| `DELETE` | `/api/tasks/<id>/` | Delete an owned task |

Useful query parameters include `?search=release`, `?status=done`, `?ordering=-due_date`, and `?page=2`. Paginated responses include `count`, `next`, `previous`, and `results`.

## Tests

Run the Django test suite with:

```powershell
python manage.py test
```

Run Django’s system checks with:

```powershell
python manage.py check
```

## Deployment

There is currently no live demo URL. This workspace has no Git remote, hosting configuration, deployment credentials, or production server setup, so the application could not be deployed from this environment.

Before deploying, configure these production requirements:

1. Set `DEBUG=False` and load `SECRET_KEY` from an environment variable.
2. Configure `ALLOWED_HOSTS` and secure HTTPS settings.
3. Use PostgreSQL or another persistent managed database instead of local SQLite.
4. Add a production WSGI server such as Gunicorn and configure static file collection with `python manage.py collectstatic`.
5. Run `python manage.py migrate` during release deployment.