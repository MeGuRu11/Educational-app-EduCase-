# tests/conftest.py
"""
Фикстуры для тестирования (in-memory DB, services).
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from core.di_container import Container
from models.user import Role
from repositories.user_repo import RoleRepository, UserRepository
from services.auth_service import AuthService
from services.user_service import UserService


@pytest.fixture
def session():
    """Создаёт In-Memory SQLite базу данных для тестов."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def container(session):
    """Мок DI-контейнера с подменённой сессией."""
    c = Container()
    # Override provider behavior to return our test session
    c.db_session.override(session)
    yield c
    c.db_session.reset_override()


@pytest.fixture
def seed_users(session):
    """Seed базовая структура для тестов auth_service."""
    # Создаём роли
    r_repo = RoleRepository(session)
    admin_role = r_repo.create(name="admin", display_name="Admin", permissions='{"all": true}')
    student_role = r_repo.create(name="student", display_name="Student", permissions='{}')
    
    # Создаём юзеров через UserService (там есть хэширование bcrypt)
    u_repo = UserRepository(session)
    u_service = UserService(u_repo, r_repo)
    
    admin = u_service.create_user("admin", "admin_pass", "Admin Adminov", "admin")
    student = u_service.create_user("test_user", "test_pass", "Test User", "student")
    
    return {
        "admin": admin,
        "student": student,
        "admin_pass": "admin_pass",
        "student_pass": "test_pass"
    }


@pytest.fixture
def auth_service(container):
    return container.auth_service
