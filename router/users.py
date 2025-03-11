from typing import Annotated

from pydantic import BaseModel
from sqlalchemy.orm import session
from fastapi import APIRouter, Depends, HTTPException, Request,Path
from ..models import Todos, Users
from ..database import sessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix= '/users',
    tags = ['Users']
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerify(BaseModel):
    password: str
    new_password: str

template = Jinja2Templates(directory="ToDoApp/templates")

@router.get("/user-profile")
def user_profile(request: Request):
    return template.TemplateResponse("profile.html", {"request": request})

@router.get("/current_user", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authorization fail')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/change_password/{password}", status_code=status.HTTP_200_OK)
async def change_password(
        user: user_dependency,
        db: db_dependency,
        user_verification: UserVerify
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authorization fail')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=401, detail='User does not exist')

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect password')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)
    db.commit()


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_200_OK)
async def read_all(
        user: user_dependency,
        db: db_dependency,
        phone_number: str
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authorization fail')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=401, detail='User does not exist')

    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()
