# Smart Career Roadmap Generator

A Python + Django + MySQL web app that recommends careers to students based on
their skills and interests, and gives them a personalised, AI-assisted
learning roadmap to follow.

## 1. Overview

Students sign up, enter their skills/interests, and get matched to suitable
career paths. From there they can generate a personalised AI roadmap for any
career, follow a step-by-step learning roadmap, take skill assessment tests,
browse curated learning resources, upload their resume, and track their
progress from a dashboard. Admins and counselors have their own panels to
manage students and career data.

## 2. Features

- Student registration/login with role-based access (Student / Admin / Counselor)
- Profile management (skills, interests, education info, certificates, projects, achievements)
- Career recommendation engine (matches student skills/interests against career requirements)
- **AI-powered roadmap generator** - enter a career, your skills, experience level and
  learning goal, and get a personalised roadmap (recommended skills, topics, learning
  sequence, project ideas, resources, estimated timeline)
- Step-by-step roadmap tracking with progress percentage
- Skill assessment (MCQ tests with a countdown timer and score history)
- Learning resources library with search, filtering and bookmarks
- Resume upload with version history
- Notifications (personal + broadcast announcements from admin)
- Admin panel - dashboard stats, manage students, send announcements, plus full
  Django admin for managing career paths, roadmaps, resources and tests
- Counselor panel - view students, leave notes, suggest a career

## 3. Technology Stack

- **Backend:** Python, Django 4.2
- **Frontend:** Django Templates, HTML5, CSS3, vanilla JavaScript (no React/Bootstrap)
- **Database:** MySQL
- **AI Integration:** Simple REST call to an OpenAI-compatible chat completion API,
  with an automatic rule-based fallback when no API key is configured

This project is a single Django application (there is no separate frontend
build/server) - Django serves the HTML pages directly, so there's only one
`backend` to run.

## 4. Project Structure

```
smart-career-roadmap-updated/
├── career_roadmap/        -> Django project settings, root urls
├── accounts/               -> Auth, roles, student profile, certificates/projects
├── core/                    -> Dashboard, career recommendation, AI roadmap,
│                               roadmap tracking, resources, skill assessment,
│                               resume, notifications, admin & counselor panels
├── templates/               -> All HTML files (organised per app + shared partials)
├── static/                   -> CSS, JS, images
├── media/                     -> Uploaded resumes and profile pictures (created at runtime)
├── requirements.txt
├── .env.example                -> Copy this to .env and fill in your own values
└── manage.py
```

## 5. Python Version

This project is built on Django 4.2. Use **Python 3.11.x or 3.12.x**.

Very new Python versions (such as 3.13/3.14) can cause installation errors on
Windows because some packages (Pillow, MySQL drivers) don't have ready-made
installers for them yet, which forces `pip` to try compiling them from source
using a C compiler that most machines don't have set up. Python 3.11/3.12 is
stable, widely used with Django, and every package in `requirements.txt` has
a ready-made installer for it, so `pip install` works with no extra setup.

## 6. Backend Setup

```bash
# create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# install dependencies
pip install -r requirements.txt
```

## 7. MySQL / Database Setup

Open MySQL and create the database:
```sql
CREATE DATABASE career_roadmap_db;
```

Then create the tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 8. Environment Variables

Copy `.env.example` to `.env` and fill in your real values:
```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key (any long random string for local dev) |
| `DEBUG` | `True` for local development |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Your MySQL connection details |
| `AI_API_KEY` | Your OpenAI (or compatible) API key. Leave blank to use the built-in fallback roadmap logic |
| `AI_API_URL`, `AI_MODEL` | Only change if you're using a different OpenAI-compatible provider |

**Never commit your real `.env` file.** It is already listed in `.gitignore`.

## 9. Running the Backend

```bash
# create your superuser (optional, for full Django admin access)
python manage.py createsuperuser

# fill in sample careers, roadmaps, resources, a skill test, testimonials,
# and a demo admin/counselor account
python manage.py seed_data

# run the project
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser. There is no separate
frontend to start - the same server renders the website.

## 10. How to Use the AI Roadmap Generator

1. Log in as a student and go to **Career Recommendation** from the sidebar.
2. Enter your skills, interests, preferred domain, experience level and
   learning goal, then click **Get My Recommendations**.
3. On any matched career card, click **🤖 AI Roadmap**.
4. The page shows a loading spinner, sends your details to the backend, and
   displays the generated roadmap (recommended skills, learning sequence,
   project ideas, resources, and estimated stages) without a page reload.
5. Click **Generate Another** to regenerate the roadmap for the same career.

If `AI_API_KEY` is not set in `.env`, or the AI API call fails for any reason
(no internet, invalid key, rate limit, etc.), the app automatically falls
back to a roadmap built from the career/roadmap data already stored in the
database, so the page never breaks or shows a blank screen. A small badge on
the result tells you whether the roadmap came from the AI API or the fallback.

## 11. Admin Login / Setup

Two ways to get an Admin or Counselor account:

**Option A - use the seeded demo accounts** (created automatically by `seed_data`):
- Admin: username `admin_demo`, password `Admin@12345`
- Counselor: username `counselor_demo`, password `Counselor@12345`

(Change these passwords before using this project anywhere beyond local demos.)

**Option B - promote an existing account:**
1. Register normally through the website (every sign-up becomes a Student).
2. Open `/django-admin/`, find that user's Profile, and change the `role`
   field to `admin` or `counselor`.

**Where admin features live:**
- `/management/dashboard/` - custom admin dashboard (stats, recent students, send announcement)
- `/management/students/` - list of all registered students
- `/django-admin/` - full Django admin for managing career paths, roadmaps,
  roadmap stages/items, learning resources, skill tests and questions
- `/counselor/dashboard/` - counselor panel to view students and leave notes

## 12. Common Errors

- **"No module named MySQLdb" or a pip build/compiler error while installing** →
  make sure you're using Python 3.11.x or 3.12.x (see section 5), then run
  `pip install -r requirements.txt` again. This project uses `PyMySQL` as the
  MySQL driver, which installs without needing a C compiler or the MySQL
  Connector/C, so this error usually means the virtual environment is using
  the wrong Python version or the install didn't finish.
- **Access denied for user** → check `DB_USER` / `DB_PASSWORD` in `.env`
  match your real MySQL login.
- **Static files not loading** → make sure `DEBUG=True` in `.env` while developing locally.
- **AI roadmap always shows the fallback badge** → check that `AI_API_KEY`
  is set correctly in `.env` and that your machine has internet access.
