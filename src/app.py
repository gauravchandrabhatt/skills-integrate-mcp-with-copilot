"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import hashlib
import json
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

security = HTTPBasic()
users_file = current_dir / "users.json"


def load_users():
    with users_file.open(encoding="utf-8") as file:
        return json.load(file)


users = load_users()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = users.get(credentials.username)
    password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    if not user or password_hash != user["password_hash"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": credentials.username, **user}


def is_staff(user):
    return user["role"] in {"teacher", "admin", "coordinator"}

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(current_user=Depends(get_current_user)):
    response = {}
    for name, activity in activities.items():
        response[name] = {
            **activity,
            "participant_count": len(activity["participants"]),
            "remaining_spots": activity["max_participants"] - len(activity["participants"]),
            "can_manage_enrollments": is_staff(current_user),
        }
        if not is_staff(current_user):
            response[name]["participants"] = []
    return response


@app.get("/me")
def get_current_user_profile(current_user=Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "linked_students": current_user.get("linked_students", []),
    }


@app.get("/me/enrollments")
def get_my_enrollments(current_user=Depends(get_current_user)):
    student_emails = [current_user["username"]]
    if current_user["role"] == "parent":
        student_emails = current_user.get("linked_students", [])

    enrollments = {
        student_email: [
            activity_name
            for activity_name, activity in activities.items()
            if student_email in activity["participants"]
        ]
        for student_email in student_emails
    }
    return {"enrollments": enrollments}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, current_user=Depends(get_current_user)):
    """Sign up a student for an activity"""
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Only student accounts can request enrollment",
        )

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    email = current_user["username"]
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: str | None = None,
    current_user=Depends(get_current_user),
):
    """Unregister a student from an activity"""
    if is_staff(current_user):
        if not email:
            raise HTTPException(status_code=400, detail="A student email is required")
    elif current_user["role"] == "student":
        email = current_user["username"]
    else:
        raise HTTPException(
            status_code=403,
            detail="Parents cannot remove enrollments",
        )

    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
