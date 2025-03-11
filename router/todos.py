from pydantic import BaseModel, Field
from typing import Annotated, Optional
from sqlalchemy.orm import session
from fastapi import APIRouter, Depends, HTTPException, Request, Path
from ..models import Todos, Users
from ..database import sessionLocal
from starlette import status
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=['todos']
)

class ToDoRequest(BaseModel):
    id: Optional[int] = Field(description="Id is primary key so it will set automatically", default=None)
    title: str = Field(description="Title of todo item", min_length=3)
    description: str = Field(description="Description of todo item", min_length=3, max_length=100)
    priority: int = Field(description="Define priority of todo item", gt=0, lt=6)
    complete: bool


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory='ToDoApp/templates')

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page/", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages ####
@router.get('/todo-page')
async def render_todo_page(request: Request, db: db_dependency):
    try:
        if request.cookies.get('access_token') is None:
            return redirect_to_login()

        user = get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()


        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        return templates.TemplateResponse("todo.html", {'request': request, 'todos': todos, 'user': user})
    except:
        redirect_to_login()

@router.get("/add-todo-page")
async def add_new_todo(request: Request):
    try:
        if request.cookies.get('access_token') is None:
            return redirect_to_login()

        user = get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {'request': request, 'user': user})
    except:
        redirect_to_login()

@router.get('/edit-todo-page/{todo_id}')
async def render_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):

    try:
        if request.cookies.get('access_token') is None:
            return redirect_to_login()

        user = get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()


        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        print("tido id==", todo.id)

        return templates.TemplateResponse("edit-todo.html", {'request': request, 'todo': todo, 'user': user})
    except:
        redirect_to_login()

### End Points ###

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(user.get('id') == Todos.owner_id).all()

@router.get("/todo/list", status_code=status.HTTP_200_OK)
async def all_todo_list(db: db_dependency):
    return db.query(Todos).all()

@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all_users(db: db_dependency):
    return db.query(Users).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    tododata = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(user.get('id') == Todos.owner_id).first()
    if tododata is not None:
        return tododata
    raise HTTPException(status_code=404, detail="To do item not found")

@router.post('/todo/', status_code=status.HTTP_201_CREATED)
async def create_todo_item(user: user_dependency,
                           db: db_dependency,
                           todo_request: ToDoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    todoModel = Todos(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todoModel)
    db.commit()

@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependency,
        db:db_dependency,
        todo_request : ToDoRequest,
        todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(user.get('id') == Todos.owner_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo item for given item does not exist")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}")
async def delete_todo_item(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(user.get('id') == Todos.owner_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo item for given item does not exist")

    db.query(Todos).filter(Todos.id == todo_id) \
        .filter(user.get('id') == Todos.owner_id).delete()
    db.commit()

