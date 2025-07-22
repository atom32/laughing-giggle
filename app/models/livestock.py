"""
Livestock model for creature management
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


class Livestock(Base):
    """Livestock model for creature management."""
    
    __tablename__ = "livestock"
    
    # Primary key - using String to store UUID for SQLite compatibility
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Owner relationship
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    
    # Basic information (using i18n keys)
    name_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    family_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    nation_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    city_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Visual representation
    pic_url: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Basic attributes
    age: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bloodtype_i18n_key: Mapped[str] = mapped_column(String(50), nullable=False)
    zodiac_i18n_key: Mapped[str] = mapped_column(String(50), nullable=False)
    origin_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    rank_i18n_key: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Game mechanics
    acquire_turn: Mapped[int] = mapped_column(Integer, nullable=False)
    quality: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Physical attributes
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Breeding relationships
    father_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("livestock.id"), nullable=True)
    mother_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("livestock.id"), nullable=True)
    
    # Location tracking
    current_location_module_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("player_modules.id"), nullable=True)
    
    # Extensible custom data
    custom_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner: Mapped["Player"] = relationship("Player", back_populates="livestock")
    father: Mapped[Optional["Livestock"]] = relationship("Livestock", remote_side=[id], foreign_keys=[father_id])
    mother: Mapped[Optional["Livestock"]] = relationship("Livestock", remote_side=[id], foreign_keys=[mother_id])
    current_location: Mapped[Optional["PlayerModule"]] = relationship("PlayerModule", foreign_keys=[current_location_module_id])
    
    # Items created from this livestock
    created_items: Mapped[list["Item"]] = relationship("Item", back_populates="source_livestock", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Livestock(id={self.id}, name_key='{self.name_i18n_key}', quality={self.quality}, owner_id={self.owner_id})>"