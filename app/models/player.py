"""
Player model for game character and progress tracking
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Player(Base):
    """Player model for game character and progress tracking."""
    
    __tablename__ = "players"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key to User
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Character information
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    family_background: Mapped[str] = mapped_column(String(100), nullable=False)
    childhood_experience: Mapped[str] = mapped_column(String(100), nullable=False)
    education_background: Mapped[str] = mapped_column(String(100), nullable=False)
    starting_city: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Game state
    money: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)
    current_turn: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_played: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="players")
    modules: Mapped[list["PlayerModule"]] = relationship("PlayerModule", back_populates="player", cascade="all, delete-orphan")
    livestock: Mapped[list["Livestock"]] = relationship("Livestock", back_populates="owner", cascade="all, delete-orphan")
    items: Mapped[list["Item"]] = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Get player's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.full_name}', money={self.money}, turn={self.current_turn})>"