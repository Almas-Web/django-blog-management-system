Django Blog Management API

A production-style Blog Management REST API built with Django REST Framework, PostgreSQL, JWT authentication, Docker, GitHub Actions CI/CD, and Render deployment.

🚀 Live Demo

Swagger API Documentation:https://django-blog-management-system.onrender.com/api/docs/

OpenAPI Schema:https://django-blog-management-system.onrender.com/api/schema/

💻 GitHub

https://github.com/Almas-Web/django-blog-management-system

✨ Features

Authentication & Account

User registration

Email verification

JWT authentication

Access and refresh tokens

Refresh token rotation

Token blacklisting

Password reset

Change password

User profile management

Profile image support

Blog Management

Create blog posts

Retrieve blog posts

Update blog posts

Delete blog posts

User-specific blog management

Pagination

Filtering

Search

API & Security

Django REST Framework

JWT-based authentication

Protected API endpoints

API throttling / rate limiting

CORS configuration

Environment-based secret configuration

OpenAPI 3.0 documentation

Swagger UI

ReDoc

Production & DevOps

Dockerized Django application

PostgreSQL database

Gunicorn WSGI server

Docker Compose for local development

GitHub Actions CI/CD

Render deployment

🛠️ Tech Stack

Technology

Purpose

Python 3.11

Programming Language

Django

Web Framework

Django REST Framework

REST API

PostgreSQL

Database

Simple JWT

Authentication

drf-spectacular

API Documentation

Docker

Containerization

Docker Compose

Local Container Orchestration

Gunicorn

Production WSGI Server

GitHub Actions

CI/CD

Render

Deployment

📁 Project Structure

Blog-Management-System/
│
├── account/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── blog/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── src/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── templates/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── .env

⚙️ Local Setup

1. Clone the repository

git clone https://github.com/Almas-Web/django-blog-management-system.git
cd django-blog-management-system

2. Create virtual environment

python -m venv venv

3. Activate virtual environment

Windows:

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate

4. Install dependencies

pip install -r requirements.txt

5. Configure environment variables

Create a .env file:

DEBUG=False

SECRET_KEY=your-secret-key

ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

OPENAI_API_KEY=your-openai-api-key

DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

Never commit your .env file or expose secret keys publicly.

6. Apply migrations

python manage.py makemigrations
python manage.py migrate

7. Run the development server

python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/

🐳 Run with Docker

Build and start the containers:

docker compose up --build

Stop the containers:

docker compose down

The application will be available at:

http://localhost:8000/

📚 API Documentation

Swagger UI:

/api/docs/

OpenAPI schema:

/api/schema/

ReDoc:

/api/redoc/

Production Swagger:

https://django-blog-management-system.onrender.com/api/docs/

🔑 API Endpoints

Account

/api/account/signup/
/api/account/login/
/api/account/verify-email/
/api/account/resend-verification-email/
/api/account/forgot-password/
/api/account/reset-password/
/api/account/change-password/

Blog

/api/blogs/

The complete API specification and request/response schemas are available through Swagger UI.

🔐 Authentication

The API uses JWT authentication.

For protected endpoints, send the access token using:

Authorization: Bearer <access_token>

Access and refresh tokens are managed using Django REST Framework Simple JWT.

🗄️ Database

The project uses PostgreSQL.

For Docker development, PostgreSQL runs as a separate service and Django connects to it through the Docker Compose network.

🔄 CI/CD

GitHub Actions is configured to automatically run the project's CI workflow when changes are pushed to GitHub.

Typical workflow:

Developer
   ↓
Git Push
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Automated Checks / Tests
   ↓
Deployment

🚀 Deployment

The application is containerized with Docker and deployed to Render.

Production stack:

Django REST Framework
        ↓
     Gunicorn
        ↓
      Docker
        ↓
     Render
        ↓
   PostgreSQL

🧪 Testing

Run Django system checks:

python manage.py check

Run the test suite:

python manage.py test

🔒 Security

Secrets are stored in environment variables.

JWT authentication protects private endpoints.

Passwords are hashed using Django's password hashing system.

Refresh token rotation and blacklisting are enabled.

API throttling is configured.

Production configuration separates secrets from source code.

📌 Project Status

Status: Completed

The project includes API development, authentication, database integration, API documentation, Dockerization, CI/CD configuration, and production deployment.

👨‍💻 Developer

Almas Hossen

Python Backend Developer

GitHub:https://github.com/Almas-Web

📄 License

This project is intended for portfolio and demonstration purposes.