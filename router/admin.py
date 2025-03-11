from typing import Annotated
from sqlalchemy.orm import session
from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos, Users
from ..database import sessionLocal
from starlette import status
from .auth import get_current_user

router = APIRouter(
    prefix= '/admin',
    tags = ['admin']
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authorization fail')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}")
async def delete_todo_item(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo item for given item does not exist")

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()