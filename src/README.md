# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities with an authenticated student account
- View linked student enrollments with an authenticated parent account
- Manage enrollment records with teacher or admin accounts

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get activities and privacy-preserving capacity information           |
| GET    | `/me`                                                             | Get the authenticated user's role and linked students              |
| GET    | `/me/enrollments`                                                 | Get the user's enrollments or linked student enrollments           |
| POST   | `/activities/{activity_name}/signup`                             | Sign up the authenticated student for an activity                  |
| DELETE | `/activities/{activity_name}/unregister?email=...`               | Unregister the current student or a staff-selected student         |

All endpoints use HTTP Basic authentication. The repository includes these
development accounts in `users.json`:

| Account | Password | Role |
| ------- | -------- | ---- |
| `student@mergington.edu` | `studentpass` | Student |
| `parent@mergington.edu` | `parentpass` | Parent linked to the demo student |
| `teacher@mergington.edu` | `teacherpass` | Teacher |
| `admin@mergington.edu` | `adminpass` | Administrator |

Student signup identity is taken from the authenticated account; callers
cannot submit another student's email. Participant names are returned only to
staff accounts.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
