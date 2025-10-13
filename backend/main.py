from fastapi import FastAPI
from routers import todo, users
app = FastAPI()

app.include_router(users.router)
# app.include_router(todo.router)


@app.get("/")
def main():
    return {"response": "Hello from todo-app!"}
