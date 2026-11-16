# TaskSplit Week 1

TaskSplit helps student project groups keep tasks, assignments, deadlines, and progress in one shared workspace. This checkout contains the Week 1 foundation for a five-week development plan.

## Current scope

- Django project and `tasks` app with SQLite database migrations.
- Registration with a display name, email, and password. Login uses email.
- Login, POST-based logout, password validation, and CSRF-protected forms.
- Create a group as its leader, or join a group using its full group code.
- View your groups, their members, and their tasks. Access requires group membership.
- Database fields for task description, assignee, deadline, status, and priority.
- Task entry and updates through Django admin during Week 1.
- Minimal responsive pages using the supplied TaskSplit logo, light account pages, dark workspace panels, and blue buttons.

The custom account model is configured before the first migration so email login can grow with the project. A group code currently uses a full UUID, such as `f9a51b07-773b-45cc-bca2-0541157bc2a5`. Each group's creator becomes its leader and a member. Any registered student can create a group in this initial version. The project administrator is a Django superuser. Group leaders use regular student accounts.

## Run on this computer

Open PowerShell in this folder. The prepared environment on this computer uses MSYS2 Python, which puts its executable in `.venv/bin`.

```powershell
& .\.venv\bin\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Stop the server with Ctrl+C.

The migrations have already been applied to the local database. To apply future migrations, run the following command.

```powershell
& .\.venv\bin\python.exe manage.py migrate
```

### Administrator account

Choose your own administrator email, display name, and password using the interactive command.

```powershell
& .\.venv\bin\python.exe manage.py createsuperuser
```

Sign in at http://127.0.0.1:8000/admin/ using that email and password. Register student accounts through the TaskSplit registration page.

### Fresh installation on another Windows computer

Use Python 3.10 or newer. Standard Windows CPython normally creates `.venv/Scripts`.

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe manage.py migrate
& .\.venv\Scripts\python.exe manage.py createsuperuser
& .\.venv\Scripts\python.exe manage.py runserver
```

For MSYS2 Python, replace `Scripts` with `bin`. Django serves this application through `manage.py runserver`. The project can be stored inside the XAMPP folder and uses its own Django development server and SQLite database.

## Week 1 demonstration

1. Register a student account and create a group.
2. Copy the full group code displayed on the group's page.
3. Log out, register another student, and join with that code.
4. Sign into Django admin with your administrator account in a separate browser session.
5. Open Tasks and add a task. Choose the group, one of its memberships as the assignee, and a deadline. An empty assignee leaves the task unassigned.
6. Refresh the student group's page to see the saved task, deadline, priority, and status.
7. Use a student account outside the group to verify that the group's URL returns a 404 page.

Django admin supplies its standard interface. The student-facing TaskSplit pages use a simple design based on the supplied prototype. The administrator maintains task records during this first stage. The group's leader-facing task forms are planned for Week 2.

## Project structure

- `manage.py` runs Django commands.
- `config/settings.py` configures the database, accounts, templates, and Philippine timezone.
- `config/urls.py` connects admin, login, logout, and application routes.
- `tasks/models.py` defines User, Project, Membership, and Task.
- `tasks/forms.py` validates registration, login, group creation, and group codes.
- `tasks/views.py` handles requests and group membership checks.
- `tasks/admin.py` registers database records for administration.
- `tasks/migrations/0001_initial.py` builds the database schema.
- `templates/` contains the HTML pages.
- `tasks/static/tasks/` contains the shared stylesheet and supplied logo.
- `tasks/tests.py` checks authentication, membership, validation, and admin task entry.

## Verify changes

```powershell
& .\.venv\bin\python.exe manage.py check
& .\.venv\bin\python.exe manage.py makemigrations --check --dry-run
& .\.venv\bin\python.exe manage.py test
```

Tests use a separate temporary database. The SQLite database, virtual environment, and Python caches are ignored by Git. Share the source files and rebuild the environment using `requirements.txt` on another computer.

The Week 1 verification passed 17 tests, Django system checks, migration consistency checks, and live HTTP checks for the home, registration, login, and protected groups routes. After the design update, all 17 tests passed again. The shared stylesheet and logo returned successful HTTP responses, and the authenticated home, group list, and group creation pages were visually checked in Chrome.

These settings support local classroom development. `DJANGO_SECRET_KEY` and `DJANGO_DEBUG` can be provided through environment variables when configuring a future hosting environment.

## Suggested remaining weeks

Confirm the schedule against your instructor's actual deadlines.

- Week 2 adds leader task creation, editing, assignment, and deadline updates, plus member status updates with role checks.
- Week 3 adds personal task filtering, workload and progress summaries, and a contribution report/export.
- Week 4 refines the visual interface based on your mockups and adds deadline reminders with agreed delivery rules.
- Week 5 covers integration testing, fixes, documentation, and the demonstration. If ML is required for TaskSplit, agree on a task-related prediction and dataset before training, saving a model with joblib, validating its inputs in Django, and recording prediction history.

## Week 1 progress report notes

The following notes match the supplied report template's sections. Enter your actual reporting dates and course details, and review the wording before submission.

### Activities completed this week

We reviewed the TaskSplit requirements and established the Django project structure. We created the account, project, membership, and task database models and applied their migrations. We implemented account registration and email login, group creation, joining through group codes, and a basic group page showing members and stored tasks. We registered the models in Django admin and checked authentication, group access, form validation, and task entry. We added a simple responsive design with the supplied TaskSplit logo, light account pages, dark workspace panels, and blue buttons.

### Activities in process

Leader-facing task management and member progress updates are planned for the next development stage. The database already includes task assignments, deadlines, priorities, and progress statuses.

### Next action

Build task creation and editing forms for group leaders, then add member status updates and permission checks.

### Due date

Enter the Week 2 deadline provided by the instructor.

### Risk and issues

The final reporting schedule and the requirement for ML integration need confirmation. Contribution-report access for instructors and the reminder delivery method also need clarification. TaskSplit's prediction target and training dataset need to be chosen if ML is included.

### Activities to be started next week

Implement task forms, member assignment, deadline editing, and progress updates. Check the leader and member permissions through the normal application pages.
