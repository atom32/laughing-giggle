"""
Module models for park management system
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


class PlayerModule(Base):
    """Player module model for tracking module levels and states."""
    
    __tablename__ = "player_modules"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key to Player
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    
    # Module information
    module_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # market, farm, slaughterhouse, etc.
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-5
    
    # Module-specific configuration and state
    config_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="modules")
    livestock_in_module: Mapped[list["Livestock"]] = relationship("Livestock", foreign_keys="Livestock.current_location_module_id")
    
    def __repr__(self) -> str:
        return f"<PlayerModule(id={self.id}, player_id={self.player_id}, type='{self.module_type}', level={self.level})>"


class ModuleConfig(Base):
    """Configuration template for different module types and levels."""
    
    __tablename__ = "module_configs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Module identification
    module_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Configuration data
    name_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    description_i18n_key: Mapped[str] = mapped_column(String(100), nullable=False)
    upgrade_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Level effects and bonuses
    effects: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<ModuleConfig(id={self.id}, type='{self.module_type}', level={self.level}, cost={self.upgrade_cost})>"