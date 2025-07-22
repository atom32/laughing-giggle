"""
Item model for processed goods and resources
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


class Item(Base):
    """Item model for processed goods and resources."""
    
    __tablename__ = "items"
    
    # Primary key - using String to store UUID for SQLite compatibility
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Owner relationship
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    
    # Item information
    item_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # meat, dish, etc.
    name_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    description_i18n_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Quantity and quality
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quality: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Value and pricing
    base_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Source tracking
    created_from_livestock_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("livestock.id"), 
        nullable=True
    )
    
    # Extensible custom data
    custom_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner: Mapped["Player"] = relationship("Player", back_populates="items")
    source_livestock: Mapped[Optional["Livestock"]] = relationship("Livestock", back_populates="created_items")
    
    def __repr__(self) -> str:
        return f"<Item(id={self.id}, type='{self.item_type}', name_key='{self.name_i18n_key}', quantity={self.quantity}, owner_id={self.owner_id})>"