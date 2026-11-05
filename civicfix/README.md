# FixMyStreet: Real-Time Local Problem Reporting Platform

A full-stack web application that lets citizens report local civic issues (garbage overflow, broken streetlights, road damage, water leakage) with a photo and a map location. Each report is automatically routed to the right department and tracked from reporting to resolution. Citizens, department officers and admins each get their own dashboard, and status changes appear on screen without a page reload.

Built with **Django** and **SQLite**.

---

## Features

- **Citizen reporting:** title, category, description, photo upload, address and a map pin (click the map, drag the pin, or use "Use my location").
- **Automatic department routing:** every issue is assigned to a department based on its category.
- **Status tracking:** Assigned, In progress, Resolved or Rejected, with a timeline that records who changed the status, when, and an optional note.
- **Role-based dashboards:**
  - **Citizen:** sees only their own reports.
  - **Officer:** sees only the issues of their department and can update status.
  - **Admin:** sees every issue, can change status, reassign departments, and use the Django admin panel.
- **Live updates:** dashboards, the home page and issue pages refresh every 5 seconds (status counts, issue list, map markers and timeline).
- **Filters:** filter the dashboard by status and category.
- **Authentication:** register with username, email and password. Log in with either **username or email**. The first page for visitors is the login page.
- **Interactive map:** Leaflet with OpenStreetMap tiles. No API key needed.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 5 |
| Database | SQLite (via the Django ORM) |
| Frontend | Django templates, HTML, CSS, vanilla JavaScript |
| Maps | Leaflet.js + OpenStreetMap |
| Image uploads | Pillow |
| Live updates | JSON API + polling every 5 seconds |

## Department routing

| Category | Department |
|---|---|
| Garbage overflow | Sanitation |
| Broken streetlight | Electrical |
| Road damage | Roads & Public Works |
| Water leakage | Water Supply |
| Other | General Administration |

Routing is done in `Issue.save()` in `issues/models.py`. An admin can reassign the department later from the issue page.

---

## Setup

### Requirements
- Python 3.10 or newer
- Internet access in the browser (map tiles and Leaflet load from CDNs)

### Windows

```bat
cd civicfix
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### macOS / Linux

```bash
cd civicfix
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

`seed_demo` creates the departments, the demo users below and four sample issues. It is safe to run more than once.

## Demo accounts

Password for every account: **`demo1234`**

| Role | Username | Email |
|---|---|---|
| Citizen | `citizen1` | `citizen1@example.com` |
| Officer (Sanitation) | `officer_sanitation` | `officer_sanitation@example.com` |
| Officer (Electrical) | `officer_electrical` | `officer_electrical@example.com` |
| Officer (Roads & Public Works) | `officer_roads` | `officer_roads@example.com` |
| Officer (Water Supply) | `officer_water` | `officer_water@example.com` |
| Officer (General Administration) | `officer_general` | `officer_general@example.com` |
| Admin | `admin1` | `admin1@example.com` |

Users created before the email feature was added have no email. Run `python manage.py seed_demo` again to fill it in, or log in with the username.

---

## How to test

Open two browser windows, one normal and one Incognito, so you can see a citizen and an officer at the same time.

1. **Report an issue (citizen).** Log in as `citizen1`, click *Report an issue*, fill the form, upload a photo and click the map to place a pin. After submitting, the issue page shows status **Assigned** and the department **Sanitation** (for a garbage report).
2. **Update the status (officer).** In the other window, log in as `officer_sanitation`, open the issue, set the status to *In progress*, add a note and save.
3. **Watch the live update.** The citizen's issue page changes to *In progress* within 5 seconds, without a refresh, and the note appears in the timeline.
4. **Check role-based access.** Log in as `officer_electrical`: the garbage issue must not be visible. Register a new citizen: their dashboard must be empty. A citizen cannot change a status (the form is hidden and a direct POST returns 403).
5. **Admin view.** Log in as `admin1`: all issues are visible, the department can be changed, and `/admin/` shows all database tables.
6. **Check the routing.** Submit one report per category and confirm each lands in the department listed in the table above.

---

## Project structure

```
civicfix/
├── manage.py
├── requirements.txt
├── README.md
├── civicfix/                  # project configuration
│   ├── settings.py
│   ├── urls.py                # admin, login, logout, includes issues.urls
│   └── wsgi.py
├── issues/                    # the main app
│   ├── models.py              # Department, Profile, Issue, StatusUpdate
│   ├── views.py               # pages + JSON API
│   ├── forms.py               # IssueForm, RegisterForm, LoginForm
│   ├── backends.py            # login with username or email
│   ├── admin.py
│   ├── urls.py                # app routes
│   ├── templatetags/extras.py
│   └── management/commands/seed_demo.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── report.html
│   ├── issue_detail.html
│   └── registration/          # login.html, form.html (register)
└── static/
    ├── css/app.css
    └── js/app.js              # maps, polling, live updates
```

Note: there are two `urls.py` files. `civicfix/urls.py` is the project router and includes the app. `issues/urls.py` holds the app routes and must **not** include itself.

## Data model

- **Department:** `name`
- **Profile:** `user`, `role` (citizen / officer / admin), `department` (for officers)
- **Issue:** `title`, `description`, `category`, `photo`, `latitude`, `longitude`, `address`, `status`, `department`, `reporter`, `created_at`, `updated_at`
- **StatusUpdate:** `issue`, `status`, `note`, `by`, `created_at` (this is the timeline)

## Pages and routes

| URL | Purpose | Access |
|---|---|---|
| `/` | Home: stats and live map (redirects to login if logged out) | Logged in |
| `/login/`, `/register/` | Authentication | Everyone |
| `/report/` | Report a new issue | Citizens |
| `/dashboard/` | Role-based issue list, stats, filters, map | Logged in |
| `/issue/<id>/` | Issue details, live timeline, status form | Owner, department officers, admins |
| `/admin/` | Django admin | Staff / superusers |

### JSON API (used for live updates)

| Endpoint | Returns |
|---|---|
| `GET /api/issues/?status=&category=` | Issues visible to the current user, plus status counts |
| `GET /api/issues/?public=1` | All issues (used by the map) |
| `GET /api/issue/<id>/` | One issue with its full timeline |

---

## Troubleshooting

**Map shows "403 Access blocked" tiles.** OpenStreetMap needs a Referer header. This project already sets `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"` in `settings.py` and `referrerPolicy: "origin"` in `static/js/app.js`. Restart the server and hard refresh the browser (Ctrl + Shift + R).

**`RecursionError: maximum recursion depth exceeded` on startup.** `issues/urls.py` contains the project's `include("issues.urls")` line. Replace its content with the app routes only (see the table above).

**"Use my location" does nothing.** Browsers allow geolocation only on `localhost`, `127.0.0.1` or HTTPS pages, and only after you allow the permission. You can always click the map instead.

**Photos do not show.** Make sure Pillow is installed and that `MEDIA_URL` and `MEDIA_ROOT` are set (they are by default). Uploaded files are saved in the `media/` folder.

**Cannot log in with email.** Confirm `AUTHENTICATION_BACKENDS = ["issues.backends.EmailOrUsernameBackend"]` is in `settings.py` and that the user has an email saved.

---

## Limitations and future work

- Live updates use **polling** (every 5 seconds). WebSockets via Django Channels would make them truly push-based.
- No email or SMS notifications yet.
- No comments, upvotes or duplicate detection.
- `DEBUG = True` and the secret key in `settings.py` are for development only. Before deploying, set `DEBUG = False`, use a secret key from an environment variable, set `ALLOWED_HOSTS`, and serve media files properly (for example with Nginx and Gunicorn).

## License
MIT