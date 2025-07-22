"""
Unit tests for User model and password operations
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.models.user import User
from app.core.security import hash_password, verify_password
from passlib.exc import UnknownHashError

# Create a minimal Base for testing
class Base(DeclarativeBase):
    pass

# Monkey patch the User model to use our test Base
User.metadata = Base.metadata


class TestUserModel:
    """Test cases for User model functionality."""
    
    @pytest.fixture(scope="function")
    def db_session(self):
        """Create a test database session."""
        # Use in-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:", echo=False)
        
        # Create only the User table for testing
        User.__table__.create(engine)
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    def test_user_creation(self, db_session):
        """Test basic user creation."""
        user = User(
            username="testuser",
            password_hash="dummy_hash",
            is_admin=False,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        retrieved_user = db_session.query(User).filter_by(username="testuser").first()
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"
        assert retrieved_user.is_admin is False
        assert retrieved_user.is_active is True
        assert retrieved_user.created_at is not None
        assert isinstance(retrieved_user.created_at, datetime)
    
    def test_user_unique_username(self, db_session):
        """Test that usernames must be unique."""
        user1 = User(
            username="testuser",
            password_hash="hash1",
            is_admin=False,
            is_active=True
        )
        
        user2 = User(
            username="testuser",  # Same username
            password_hash="hash2",
            is_admin=False,
            is_active=True
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # Should raise an integrity error due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()
    
    def test_set_password(self, db_session):
        """Test password hashing functionality."""
        user = User(
            username="testuser",
            password_hash="dummy",
            is_admin=False,
            is_active=True
        )
        
        # Set password using the method
        user.set_password("mypassword123")
        
        # Verify password was hashed
        assert user.password_hash != "mypassword123"
        assert user.password_hash != "dummy"
        assert len(user.password_hash) > 20  # Bcrypt hashes are long
        assert user.password_hash.startswith("$2b$")  # Bcrypt prefix
    
    def test_check_password_correct(self, db_session):
        """Test password verification with correct password."""
        user = User(
            username="testuser",
            password_hash="dummy",
            is_admin=False,
            is_active=True
        )
        
        password = "mypassword123"
        user.set_password(password)
        
        # Verify correct password
        assert user.check_password(password) is True
    
    def test_check_password_incorrect(self, db_session):
        """Test password verification with incorrect password."""
        user = User(
            username="testuser",
            password_hash="dummy",
            is_admin=False,
            is_active=True
        )
        
        user.set_password("mypassword123")
        
        # Verify incorrect password
        assert user.check_password("wrongpassword") is False
        assert user.check_password("") is False
        assert user.check_password("mypassword124") is False
    
    def test_update_last_login(self, db_session):
        """Test updating last login timestamp."""
        user = User(
            username="testuser",
            password_hash="dummy",
            is_admin=False,
            is_active=True
        )
        
        # Initially last_login should be None
        assert user.last_login is None
        
        # Update last login
        user.update_last_login()
        
        # Verify last_login was set
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
        
        # Verify it's recent (within last minute)
        time_diff = datetime.utcnow() - user.last_login
        assert time_diff.total_seconds() < 60
    
    def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(
            username="testuser",
            password_hash="dummy",
            is_admin=True,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        repr_str = repr(user)
        assert "testuser" in repr_str
        assert "is_admin=True" in repr_str
        assert f"id={user.id}" in repr_str


class TestPasswordSecurity:
    """Test cases for password security utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Verify hash properties
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")
    
    def test_hash_password_different_results(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Should be different due to salt
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False
        assert verify_password("", hashed) is False
        assert verify_password("testpassword124", hashed) is False
    
    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Empty password should fail
        assert verify_password("", hashed) is False
        
        # Empty hash should fail (will raise exception, so we catch it)
        try:
            result = verify_password(password, "")
            assert result is False
        except UnknownHashError:
            # This is expected behavior for empty hash
            pass
        
        # Both empty should fail (will raise exception, so we catch it)
        try:
            result = verify_password("", "")
            assert result is False
        except UnknownHashError:
            # This is expected behavior for empty hash
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])