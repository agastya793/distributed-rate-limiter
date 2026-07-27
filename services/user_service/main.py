from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="User Microservice",
    version="1.0.0"
)

USERS_DB = [
    {"id": "1", "username": "shubham", "email": "shubham@example.com", "role": "admin"},
    {"id": "2", "username": "alice", "email": "alice@example.com", "role": "premium"},
    {"id": "3", "username": "bob", "email": "bob@example.com", "role": "free"},
]


@app.get("/")
@app.get("/health")
def health():
    return {"service": "User Service", "status": "healthy"}


@app.get("/users")
def get_users():
    return {
        "service": "User Service",
        "count": len(USERS_DB),
        "users": USERS_DB
    }


@app.get("/users/{user_id}")
def get_user_by_id(user_id: str):
    user = next((u for u in USERS_DB if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"service": "User Service", "user": user}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
