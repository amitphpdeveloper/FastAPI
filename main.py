from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine
from .router import auth, todos, admin, users
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="ToDoApp/static"), name="static")

@app.get("/")
async def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
async def health_check():
    return {'status': 'Healthy'}

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

