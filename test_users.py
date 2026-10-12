from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from datetime import date
from sqlalchemy import select
from main import app
import pytest,pytest_asyncio
from sqlalchemy.pool import NullPool    



from database import get_db
from models import Base,User,Post
from Utilities.security import hash_password

# TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TEST_DATABASE_URL ="postgresql+asyncpg://postgres:Vik%40ash1@localhost:5432/fastapi_test"

test_engine = create_async_engine(TEST_DATABASE_URL,poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine,expire_on_commit=False)

async def init_test_db():
    async with test_engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)


async def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        await db.close()



app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest_asyncio.fixture(scope ="session",autouse=True)
async def start_schema():
    await init_test_db()

@pytest_asyncio.fixture
async def test_user():
    db =TestSessionLocal()

    user = User(
        name ="Test User",
        email="vikashjhaaaaa@gmail.com",
        password=hash_password('1234').decode()
    )
    db.add(user)
    await db.commit()
    try:
        yield user
    finally:
        await db.delete(user)
        await db.commit()
        await db.close()

@pytest_asyncio.fixture
async def test_user2():
    db =TestSessionLocal()

    user = User(
        name ="Test User 2",
        email="testuser12@gmail.com",
        password=hash_password('1234').decode()
    )
    db.add(user)
    
    await db.commit()
    await db.refresh(user)

    post = Post(
        title ='Post 1',
        created = date.today(),
        user_id = user.id
    )
    db.add(post)
    await db.commit()



    try:
        yield user,post
    finally:
        
        await db.delete(post)
        await db.delete(user)
        await db.commit()
        await db.close()

@pytest.fixture
def authenticated_client(test_user):
    login_request = client.post("/api-registeration-v1/login",json={"email":test_user.email,"password":"1234"})
    token = login_request.json()['access_token']

    headers = {
        "Authorization":f"Bearer {token}"
    }
    client.headers = headers
    return client

def test_login(authenticated_client,test_user):

    user_response = authenticated_client.get(f"/api-version-v1/users/{test_user.id}")

    assert user_response.status_code == 200

def test_wrong_password(test_user):
    user_response = client.post("/api-registeration-v1/login",json={
        "email":test_user.email,
        "password":"1235"
    })

    assert user_response.status_code == 401

def test_non_existent_user():
    login_user = client.post("/api-registeration-v1/login",
                             json={
                                 "email":"Vikashjha1323@gmail.com",
                                  "password":"1234"
                             })
    assert login_user.status_code == 401



def test_delete_post_creation(authenticated_client,test_user,test_user2):
    user2, post = test_user2
    user_post = authenticated_client.delete(f"/api-registeration-v1/users/{user2.id}/posts/{post.id}")


    assert user_post.status_code == 404

@pytest_asyncio.fixture
async def test_post_create(authenticated_client,test_user):
    details = authenticated_client.post("/api-post-v1/Post",
                                        json={"title":"I am pro"})

    db = TestSessionLocal()

    statement = (
        select(Post)
        .filter(Post.user_id == test_user.id)
    )
    result = await db.execute(statement)
    same_user = result.scalars().first()
    await db.close()
    assert same_user.user_id == test_user.id

def test_read_post(authenticated_client,test_user2):
    user2, post = test_user2
    details = authenticated_client.get(f"/api-post-v1/Post/{post.id}")

    assert details.status_code == 200   

@pytest_asyncio.fixture
async def test_user3():
    db = TestSessionLocal()

    user = User(
        name = "Test User 3",
        email ="testuser78@gmail.com",
        password = hash_password('1234').decode()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    post = Post(
        title ='Post 2',
        created = date.today(),
        user_id = user.id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    login_request = client.post(
        "/api-registeration-v1/login",
        json = {
            "email":user.email,
            "password": "1234"
        }
    )
    token = login_request.json()['access_token']

    headers = {
        "Authorization":f"Bearer {token}"
    }

    authenticated = TestClient(app)

    authenticated.headers = headers
    try:
        yield user,post,authenticated
    finally:
        
        await db.delete(post)
        await db.delete(user)
        await db.commit()
        await db.close()
    

def test_update_post(test_user3):
    user3 ,post,authenticated = test_user3
    detail = authenticated.patch(f"/api-post-v1/Post/{post.id}",
                                 json={
                                     "title":"Updated title"
                                 })

    assert detail.status_code ==200