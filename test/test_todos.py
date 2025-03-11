from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base
from ..router.auth import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    test_db = TestingSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close_all()


def override_get_current_user():
    return {'username': 'amitsol', 'id' : 1, 'role': 'admin'}

"""Create a new database session with a rollback at the end of the test."""
""" @pytest.fixture(scope="function")
def db_session():

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client

"""


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture()
def test_todo():
    todo = Todos(
        complete=False,
        description='Read book everyday to enhance your knowledge',
        owner_id=1,
        priority=2,
        title='Read 5 min book after tea',
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

def test_read_all_authenticate(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    #assert response.json() == []
    #assert response.json() == [{'complete': False, 'description': 'Finished all your work in early morning','id': 1,
    #                           'owner_id': 1,'priority': 1,'title': 'wake up at 5:00 AM'},
    #                           {'complete': False, 'description': 'Do Medidation in morning', 'id': 6,
    #                            'owner_id': 1, 'priority': 2, 'title': 'Meditation for 5 minute'},
    #                          {'complete': True, 'description': 'Complete Fast API cource', 'id': 7,
    #                           'owner_id': 1, 'priority': 3, 'title': 'Finished chapter 11 in Fast API'}
    #                           ]


def test_create_todo(test_todo):
    request_data = {
        'title': 'New TODO!',
        'description' : 'New todo description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todos/todo/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

