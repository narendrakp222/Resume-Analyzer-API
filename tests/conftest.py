import os
import fitz  # PyMuPDF
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db
from app.core.config import settings

# Test database URL (SQLite in memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Clean up any test uploaded files
    if os.path.exists(settings.UPLOAD_DIR):
        for fname in os.listdir(settings.UPLOAD_DIR):
            if fname != ".gitkeep":
                fpath = os.path.join(settings.UPLOAD_DIR, fname)
                try:
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                except Exception:
                    pass


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """
    Generate a real PDF byte stream in memory using PyMuPDF for testing.
    """
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "John Doe\n"
        "Email: john@example.com | Phone: +1-123-456-7890 | GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe\n"
        "Education: Bachelor of Science in Computer Science, State University\n"
        "Skills: Python, FastAPI, PostgreSQL, SQL, JavaScript, React, Docker, Git, REST API, Machine Learning\n"
        "Projects:\n"
        "- E-Commerce API: Built using Python and FastAPI, serving 5000+ daily active users and reducing API latency by 40%.\n"
        "- Resume Analyzer: Designed automated NLP pipeline with spaCy and PyMuPDF.\n"
    )
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest_asyncio.fixture
async def authenticated_client(client, db_session):
    # Register user
    register_res = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testPassword123"
        }
    )
    assert register_res.status_code == 201

    # Login user
    login_res = await client.post(
        "/auth/login",
        json={
            "username_or_email": "testuser",
            "password": "testPassword123"
        }
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
