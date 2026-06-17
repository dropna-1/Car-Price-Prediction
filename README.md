# Car price prediction API
REST API built with FastAPI for car management 
and price prediction using Machine Learning .

## Features
- user authentication (JWT)
- Car CRUD operations
- Buy/Sell cars
- Machine Learning price prediction 
- Database migrations with Alembic
- Automated tests with Pytest

## Technologies
- FastAPI
- scikit-learn
- SQLAlchemy
- PostgreSQL
- Alembic
- pytest

## Installation
Clone repository:
```bash
git clone <repository-url>
cd project-name
```

Create virtual environment:
```bash
python -m venv venv
```

Activate environment:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create '.env' from '.env.example'
Example:
```env
DATABASE_URL = 
TEST_DATA_BASE = 
SECRET_KEY = 
```

Run migrations:
```bash
alembic upgrade head
```
---
To test, you need to change 'DATABASE_URL' to 
'TEST_DATABASE_URL'
inside the env.py folder and inside os.getenv() and run
the above command again
---


Start server:
```bash
uvicorn app.main:app --reload
```

## Run tests
```bash
pytest
```

## API Docs (Swagger UI)
```text
http://127.0.0.1:8000/docs
```

