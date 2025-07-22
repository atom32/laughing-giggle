"""
User model for authentication and account management
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.security import hash_password, verify_password


class User(Base):
    """User model for authentication and account management."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # User status
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    players: Mapped[list["Player"]] = relationship("Player", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """
        Set the user's password by hashing it.
        
        Args:
            password: Plain text password to hash and store
        """
        self.password_hash = hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return verify_password(password, self.password_hash)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp to current time."""
        self.last_login = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', is_admin={self.is_admin})>"