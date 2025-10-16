from fastapi import FastAPI
from routers import todo, users, admin
from auth import auth
app = FastAPI()

app.include_router(users.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(auth.router)


@app.get("/")
def main():
    return {"response": "Hello from todo-app!"}
