import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.auth import create_access_token, hash_password
import pytest_asyncio
from app.main import app
from app.database import Base, get_db
from app.config import settings
# Isolated Test Database Connection String
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:secretpassword@localhost:5432/choresTracker_test"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before testing starts, then drop them when finished."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Provides a transactional database session per test function."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest_asyncio.fixture  
async def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
@pytest.fixture
def test_parent_user(db_session):
    """Creates a sample parent user in the test database."""
    from app.models import Parent
    
    user = Parent(
        username="testparent",
        email="parent@test.com",
        fullName="Test Parent",  # <--- ADD THIS LINE to satisfy the NOT NULL constraint!
        hashed_password=hash_password("securepassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
        
@pytest.fixture
def test_child_user(db_session, test_parent_user):
    """Creates a sample child user linked to a parent."""
    from app.models import Child
    
    child = Child(
        username="testchild",
        email="child@test.com",
        fullName="Test Child",
        hashed_password=hash_password("securepassword123"),
        parent_id=test_parent_user.id
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(child)
    return child
    #app.dependency_overrides.clear()

# from app.auth import get_current_child  # Import your actual dependency

# @pytest_asyncio.fixture
# async def get_child_client(db_session, test_child_user):
#     #Provides an AsyncClient authenticated directly as a Child instance.
    
#     # 1. Override get_current_user to return the Child model instance directly
#     def _override_get_current_user():
#         return test_child_user

#     def _override_get_db():
#         try:
#             yield db_session
#         finally:
#             pass

#     app.dependency_overrides[get_current_child] = _override_get_current_user
#     app.dependency_overrides[get_db] = _override_get_db

#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         yield ac

#     app.dependency_overrides.clear()


# # conftest.py

# @pytest.fixture
# def auth_child_client(client, get_child_client):
#     #Provides an AsyncClient authenticated as a Child.
#     print("\nDEBUG CHILD ID:", get_child_client.id)
#     # Verify child.id is no longer None
#     token = create_access_token(
#         data={"sub": str(get_child_client.id) , "role": "child"}  # Or test_child_user.username / email depending on your auth backend
#     )
    
#     # Clone headers to avoid mutating client state globally
#     client.headers = client.headers.copy()
#     client.headers.update({"Authorization": f"Bearer {token}"})
#     return client

from app.auth import get_current_child, get_current_user  # Import your dependencies

@pytest_asyncio.fixture
async def auth_child_client(db_session, test_child_user):
    """Provides an AsyncClient authenticated directly as a Child instance."""
    
    # Override BOTH auth dependencies to return test_child_user directly
    def _override_get_current_child():
        return test_child_user

    def _override_get_current_user():
        return test_child_user

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_current_child] = _override_get_current_child
    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()