# MealQ: Smart Cafeteria Queue Management System

MealQ is a web-based cafeteria queue management system designed to make meal service more organised, predictable and efficient.

The system allows students to view meal sessions and join an organised queue, while administrators can schedule meals, manage meal types and students, monitor active queues, and control batch-based meal serving.

MealQ was developed to address challenges such as long queues, unpredictable meal serving times, and difficulty coordinating students and cafeteria servers during busy meal periods.


## Features

### Student Features

* Student authentication and account verification
* Email-based multi-factor authentication (MFA)
* Secure login using a password and one-time verification code
* Student dashboard
* View available and active meal sessions
* View queue/batch information
* View meal schedules
* View personal profile
* Respond to meal-serving requests
* Track queue participation

### Administrator Features

* Secure administrator authentication
* Email-based MFA during login
* Administrator dashboard
* Create and manage meal sessions
* Schedule meals
* Manage meal types
* Manage students
* Manage system users
* Monitor active meal sessions
* Monitor serving batches
* Control meal-serving flow

### Meal Queue Management

MealQ uses a batch-based queue system instead of requiring students to form one large physical queue.

A meal session can define:

* Batch size
* Batch release interval
* Response window
* Scheduled start time
* Meal type
* Meal information

The system progressively releases students in batches and tracks the status of each batch.

Typical batch states include:

```text
WAITING → CALLED → COMPLETED
```

A meal session progresses through:

```text
SCHEDULED → ACTIVE → COMPLETED
```

The system is designed to automatically manage the serving flow based on the configured schedule and batch settings.

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic
* JWT authentication
* PyOTP
* Brevo
* Uvicorn

### Frontend

* Next.js
* React
* TypeScript
* CSS
* REST API integration

### Development & Deployment

* GitHub
* Render
* Vercel
* PostgreSQL


## Project Structure

The frontend and backend are contained in a single repository.

```text
MealQ/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   ├── .env
│   └── mealq.db
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── types/
│   ├── public/
│   ├── package.json
│
├── tests/
│
├── .gitignore
└── README.md
```



# Backend

The backend provides the REST API and contains the application's business logic.

The backend follows a layered structure:

```text
Routers
   ↓
Services
   ↓
Repositories
   ↓
Models
↓
database.py
↓
main.py
```

### Routers
Routers handle HTTP requests and responses. 

### Services
Services contain business logic such as:

### Repositories
Repositories handle database operations such as:

### Models

Models define the database entities used by the application.


# Frontend

The frontend is built using Next.js and TypeScript.

The application provides separate experiences for students and administrators.

### Student Area

```text
/student
```

Student navigation includes areas such as:

* Overview
* Profile
* Meal information
* Queue information

### Administrator Area

```text
/admin
```

Administrator navigation includes:

* Dashboard
* Meal Sessions
* Schedules
* Meal Types
* Students
* Users


# Meal Session Workflow

Administrators can create a meal session with configuration such as:

```text
Meal Type
     ↓
Scheduled Start Time
     ↓
Batch Size
     ↓
Release Interval
     ↓
Response Window
```


# API

The backend exposes a REST API under:

```text
/api/v1
```

Examples of endpoints include:

```text
POST /api/v1/auth/login
POST /api/v1/auth/verify-mfa
POST /api/v1/auth/logout

GET /api/v1/users/me

GET /api/v1/meal-sessions/active

GET /api/v1/meal-sessions/{id}/monitor
```

The frontend communicates with the backend through the configured API URL.


# Local Development
Make sure you have:

* Python 3.10+
* Node.js
* npm
* PostgreSQL 


## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd MealQ
```


# Backend Setup

## 2. Create and Activate the Python Environment

From the repository:

```bash
python -m venv env
```

Activate it on Linux/macOS:

```bash
source env/bin/activate
```


## 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 4. Configure Backend Environment Variables

Create:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/mealq

SECRET_KEY=your-secret-key
ALGORITHM=HS256

BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=your-sender-email
BREVO_SENDER_NAME=MealQ
```

Do not commit `.env` to GitHub.

## 5. Start the Backend

From the `backend` directory:

```bash
python -m uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://localhost:8000
```

API documentation is available through FastAPI at:

```text
http://localhost:8000/docs
```


# Frontend Setup

## 6. Install Frontend Dependencies

Open another terminal:

```bash
cd frontend
npm install
```


## 7. Configure Frontend Environment Variables

Create:

```text
frontend/.env.local
```

Example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```


## 8. Start the Frontend

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```
