# Backend README

## Blog Backend API

Flask-based RESTful API for the blog application.

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database

```bash
# The database will be created automatically on first run
python run.py
```

### 5. Create Admin User

```bash
python scripts/create_admin.py
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:5000/api/v1/docs
- OpenAPI JSON: http://localhost:5000/api/v1/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Admin login
- `POST /api/v1/auth/logout` - Admin logout
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Articles
- `GET /api/v1/articles` - List articles
- `GET /api/v1/articles/<slug>` - Get article by slug
- `POST /api/v1/articles` - Create article (auth required)
- `PUT /api/v1/articles/<slug>` - Update article (auth required)
- `DELETE /api/v1/articles/<slug>` - Delete article (auth required)

### Categories
- `GET /api/v1/categories` - List categories
- `POST /api/v1/categories` - Create category (auth required)
- `DELETE /api/v1/categories/<id>` - Delete category (auth required)

### Tags
- `GET /api/v1/tags` - List tags
- `POST /api/v1/tags` - Create tag (auth required)
- `DELETE /api/v1/tags/<id>` - Delete tag (auth required)

### Comments
- `GET /api/v1/comments` - List comments
- `DELETE /api/v1/comments/<id>` - Delete comment (auth required)
- `PUT /api/v1/comments/<id>/approve` - Approve comment (auth required)

### Settings
- `GET /api/v1/settings` - Get site settings
- `PUT /api/v1/settings` - Update settings (auth required)

### Upload
- `POST /api/v1/upload` - Upload file (auth required)

## Development

### Run Server

```bash
python run.py
```

### Run Tests

```bash
pytest
```

## Production

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Docker

```bash
docker-compose up -d
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Extensions initialization
│   ├── models/              # Database models
│   │   ├── admin.py
│   │   ├── article.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   ├── comment.py
│   │   ├── site_setting.py
│   │   └── operation_log.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── articles.py
│   │       ├── categories.py
│   │       ├── tags.py
│   │       ├── comments.py
│   │       ├── settings.py
│   │       └── upload.py
│   └── utils/
│       ├── jwt.py
│       └── password.py
├── scripts/
│   ├── create_admin.py
│   └── migrate_data.py
├── tests/
├── uploads/
├── requirements.txt
├── .env.example
└── run.py
```
