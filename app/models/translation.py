"""
Translation model for internationalization support
"""
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Translation(Base):
    """Translation model for internationalization support."""
    
    __tablename__ = "translations"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Translation key and language
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Translation value
    value: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Category for organization
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general", index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Ensure unique key-language combinations
    __table_args__ = (
        UniqueConstraint('key', 'language_code', name='uq_translation_key_language'),
    )
    
    def __repr__(self) -> str:
        return f"<Translation(id={self.id}, key='{self.key}', lang='{self.language_code}', category='{self.category}')>"