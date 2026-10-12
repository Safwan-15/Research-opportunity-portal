# University Research Opportunity Portal

GitHub Repository: https://github.com/Safwan-15/Research-opportunity-portal

Course: Computer Networks | BS (AI 5A) | Fall-2026

## Tech Stack
- Backend: Python (Flask)
- Database: MySQL
- Frontend: HTML, CSS, JavaScript, Bootstrap

## Project Structure
```
backend/      Flask REST API
frontend/     index.html
database/     schema.sql
postman/      Exported Postman/Bruno collection
```

## Setup

### 1. Database
Open MySQL and run:
```
mysql -u root -p < database/schema.sql
```

### 2. Backend
```
cd backend
python -m venv venv
venv\Scripts\activate          (Windows)
source venv/bin/activate       (Linux/Mac)
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and put in your MySQL password. Then run:
```
python app.py
```
The API runs at http://127.0.0.1:5000

### 3. Frontend
Open `frontend/index.html` in a browser (or use the VS Code Live Server extension).

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/opportunities | Create |
| GET | /api/opportunities | Get all |
| GET | /api/opportunities/:id | Get one |
| PUT | /api/opportunities/:id | Update |
| DELETE | /api/opportunities/:id | Delete |

Status codes used: 200, 201, 400, 404, 500.
