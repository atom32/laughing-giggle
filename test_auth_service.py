"""
Unit tests for AuthService
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text, Integer, String, Boolean, DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.services.auth_service import AuthService
from app.core.security import verify_password, hash_password


# Create a test-specific User model to avoid UUID issues
class TestBase(DeclarativeBase):
    """Test-specific base class."""
    pass


class TestUser(TestBase):
    """Test User model without UUID dependencies."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    def set_password(self, password: str) -> None:
        """Set the user's password by hashing it."""
        self.password_hash = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return verify_password(password, self.password_hash)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp to current time."""
        self.last_login = datetime.utcnow()


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db():
    """Create a test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create only the test User table
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    
    # Create session
    TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with TestSessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def auth_service(test_db):
    """Create an AuthService instance with test database."""
    return AuthService(test_db)


@pytest.fixture
async def test_user(auth_service):
    """Create a test user."""
    user = await auth_service.register_user("testuser", "password123")
    return user


class TestAuthService:
    """Test cases for AuthService."""
    
    async def test_register_user_success(self, auth_service):
        """Test successful user registration."""
        user = await auth_service.register_user("newuser", "password123")
        
        assert user is not None
        assert user.username == "newuser"
        assert user.is_active is True
        assert user.is_admin is False
        assert user.created_at is not None
        assert verify_password("password123", user.password_hash)
    
    async def test_register_user_with_admin(self, auth_service):
        """Test user registration with admin privileges."""
        user = await auth_service.register_user("adminuser", "password123", is_admin=True)
        
        assert user is not None
        assert user.username == "adminuser"
        assert user.is_admin is True  
    async def test_register_user_duplicate_username(self, auth_service):
        """Test registration with duplicate username."""
        # Register first user
        user1 = await auth_service.register_user("duplicate", "password123")
        assert user1 is not None
        
        # Try to register with same username
        user2 = await auth_service.register_user("duplicate", "password456")
        assert user2 is None
    
    async def test_register_user_case_insensitive(self, auth_service):
        """Test that usernames are case insensitive."""
        user1 = await auth_service.register_user("TestUser", "password123")
        assert user1 is not None
        assert user1.username == "testuser"  # Should be lowercase
        
        # Try with different case
        user2 = await auth_service.register_user("testuser", "password456")
        assert user2 is None
    
    async def test_register_user_invalid_username(self, auth_service):
        """Test registration with invalid username."""
        with pytest.raises(ValueError, match="Username must be at least 3 characters long"):
            await auth_service.register_user("ab", "password123")
        
        with pytest.raises(ValueError, match="Username must be at least 3 characters long"):
            await auth_service.register_user("", "password123")
        
        with pytest.raises(ValueError, match="Username must be at least 3 characters long"):
            await auth_service.register_user("  ", "password123")
    
    async def test_register_user_invalid_password(self, auth_service):
        """Test registration with invalid password."""
        with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
            await auth_service.register_user("testuser", "12345")
        
        with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
            await auth_service.register_user("testuser", "")
    
    async def test_authenticate_user_success(self, auth_service, test_user):
        """Test successful user authentication."""
        user = await auth_service.authenticate_user("testuser", "password123")
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == "testuser"
        assert user.last_login is not None
    
    async def test_authenticate_user_wrong_password(self, auth_service, test_user):
        """Test authentication with wrong password."""
        user = await auth_service.authenticate_user("testuser", "wrongpassword")
        assert user is None
    
    async def test_authenticate_user_nonexistent(self, auth_service):
        """Test authentication with nonexistent user."""
        user = await auth_service.authenticate_user("nonexistent", "password123")
        assert user is None 
    async def test_authenticate_user_inactive(self, auth_service, test_user):
        """Test authentication with inactive user."""
        # Deactivate user
        await auth_service.deactivate_user(test_user.id)
        
        user = await auth_service.authenticate_user("testuser", "password123")
        assert user is None
    
    async def test_get_user_by_username(self, auth_service, test_user):
        """Test getting user by username."""
        user = await auth_service.get_user_by_username("testuser")
        assert user is not None
        assert user.id == test_user.id
        
        # Test case insensitive
        user = await auth_service.get_user_by_username("TestUser")
        assert user is not None
        assert user.id == test_user.id
        
        # Test nonexistent
        user = await auth_service.get_user_by_username("nonexistent")
        assert user is None
    
    async def test_get_user_by_id(self, auth_service, test_user):
        """Test getting user by ID."""
        user = await auth_service.get_user_by_id(test_user.id)
        assert user is not None
        assert user.username == "testuser"
        
        # Test nonexistent
        user = await auth_service.get_user_by_id(99999)
        assert user is None
    
    async def test_create_access_token(self, auth_service, test_user):
        """Test creating access token."""
        token = auth_service.create_access_token(test_user)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    async def test_verify_token(self, auth_service, test_user):
        """Test token verification."""
        token = auth_service.create_access_token(test_user)
        
        verified_user = await auth_service.verify_token(token)
        assert verified_user is not None
        assert verified_user.id == test_user.id
        assert verified_user.username == test_user.username
    
    async def test_verify_invalid_token(self, auth_service):
        """Test verification of invalid token."""
        user = await auth_service.verify_token("invalid.token.here")
        assert user is None 
    async def test_change_password_success(self, auth_service, test_user):
        """Test successful password change."""
        result = await auth_service.change_password(
            test_user.id, "password123", "newpassword123"
        )
        assert result is True
        
        # Verify old password no longer works
        user = await auth_service.authenticate_user("testuser", "password123")
        assert user is None
        
        # Verify new password works
        user = await auth_service.authenticate_user("testuser", "newpassword123")
        assert user is not None
    
    async def test_change_password_wrong_old_password(self, auth_service, test_user):
        """Test password change with wrong old password."""
        result = await auth_service.change_password(
            test_user.id, "wrongpassword", "newpassword123"
        )
        assert result is False
    
    async def test_deactivate_user(self, auth_service, test_user):
        """Test user deactivation."""
        result = await auth_service.deactivate_user(test_user.id)
        assert result is True
        
        # Verify user is deactivated
        user = await auth_service.get_user_by_id(test_user.id)
        assert user is not None
        assert user.is_active is False
    
    async def test_activate_user(self, auth_service, test_user):
        """Test user activation."""
        # First deactivate
        await auth_service.deactivate_user(test_user.id)
        
        # Then activate
        result = await auth_service.activate_user(test_user.id)
        assert result is True
        
        # Verify user is activated
        user = await auth_service.get_user_by_id(test_user.id)
        assert user is not None
        assert user.is_active is True