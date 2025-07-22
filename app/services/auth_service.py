"""
Authentication service for user registration, login, and token management
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.core.config import get_settings


class AuthService:
    """Service class for handling authentication operations."""
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the authentication service.
        
        Args:
            db_session: Database session for operations
        """
        self.db = db_session
        self.settings = get_settings()
    
    async def register_user(self, username: str, password: str, is_admin: bool = False) -> Optional[User]:
        """
        Register a new user account.
        
        Args:
            username: Unique username for the account
            password: Plain text password to hash and store
            is_admin: Whether the user should have admin privileges
            
        Returns:
            User: Created user object if successful, None if username already exists
            
        Raises:
            ValueError: If username or password is invalid
        """
        # Validate input
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        username = username.strip().lower()
        
        try:
            # Check if username already exists
            existing_user = await self.get_user_by_username(username)
            if existing_user:
                return None
            
            # Create new user
            user = User(
                username=username,
                is_admin=is_admin,
                is_active=True,
                created_at=datetime.utcnow()
            )
            user.set_password(password)
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            return user
            
        except IntegrityError:
            await self.db.rollback()
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password to verify
            
        Returns:
            User: User object if authentication successful, None if failed
        """
        if not username or not password:
            return None
        
        username = username.strip().lower()
        user = await self.get_user_by_username(username)
        
        if not user or not user.is_active:
            return None
        
        if not user.check_password(password):
            return None
        
        # Update last login timestamp
        user.update_last_login()
        await self.db.commit()
        
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User: User object if found, None if not found
        """
        username = username.strip().lower()
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User: User object if found, None if not found
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create an access token for a user.
        
        Args:
            user: User to create token for
            expires_delta: Optional custom expiration time
            
        Returns:
            str: JWT access token
        """
        data = {
            "sub": str(user.id),
            "username": user.username,
            "is_admin": user.is_admin,
            "iat": datetime.utcnow()
        }
        return create_access_token(data, expires_delta)
    
    async def verify_token(self, token: str) -> Optional[User]:
        """
        Verify a JWT token and return the associated user.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User: User object if token is valid, None if invalid
        """
        payload = verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return None
        
        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            return None
        
        return user
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh an access token if it's valid.
        
        Args:
            token: Current JWT token
            
        Returns:
            str: New JWT token if refresh successful, None if failed
        """
        user = await self.verify_token(token)
        if user is None:
            return None
        
        return self.create_access_token(user)
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (placeholder for future token blacklisting).
        
        Args:
            token: JWT token to revoke
            
        Returns:
            bool: True if revocation successful, False otherwise
        """
        # For now, we don't implement token blacklisting
        # In a production system, you would store revoked tokens in a cache/database
        # and check against them in verify_token
        return True
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: ID of the user changing password
            old_password: Current password for verification
            new_password: New password to set
            
        Returns:
            bool: True if password changed successfully, False otherwise
            
        Raises:
            ValueError: If new password is invalid
        """
        if not new_password or len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long")
        
        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            return False
        
        if not user.check_password(old_password):
            return False
        
        user.set_password(new_password)
        await self.db.commit()
        
        return True
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: ID of the user to deactivate
            
        Returns:
            bool: True if deactivation successful, False otherwise
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return False
        
        user.is_active = False
        await self.db.commit()
        
        return True
    
    async def activate_user(self, user_id: int) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: ID of the user to activate
            
        Returns:
            bool: True if activation successful, False otherwise
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return False
        
        user.is_active = True
        await self.db.commit()
        
        return True