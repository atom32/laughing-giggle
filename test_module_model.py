"""
Unit tests for PlayerModule and ModuleConfig models
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.module import PlayerModule, ModuleConfig
from app.models.player import Player
from app.models.user import User


class TestPlayerModule:
    """Test cases for PlayerModule model."""
    
    def test_create_player_module(self, db_session, test_player):
        """Test creating a basic player module."""
        module = PlayerModule(
            player_id=test_player.id,
            module_type="market",
            level=1,
            config_data={"stock_refresh_cost": 100}
        )
        
        db_session.add(module)
        db_session.commit()
        
        assert module.id is not None
        assert module.player_id == test_player.id
        assert module.module_type == "market"
        assert module.level == 1
        assert module.config_data == {"stock_refresh_cost": 100}
        assert isinstance(module.created_at, datetime)
        assert isinstance(module.last_updated, datetime)
    
    def test_player_module_defaults(self, db_session, test_player):
        """Test default values for PlayerModule."""
        module = PlayerModule(
            player_id=test_player.id,
            module_type="farm"
        )
        
        db_session.add(module)
        db_session.commit()
        
        assert module.level == 0
        assert module.config_data == {}
    
    def test_player_module_relationship(self, db_session, test_player):
        """Test relationship between PlayerModule and Player."""
        module = PlayerModule(
            player_id=test_player.id,
            module_type="slaughterhouse",
            level=2
        )
        
        db_session.add(module)
        db_session.commit()
        
        # Test forward relationship
        assert module.player is not None
        assert module.player.id == test_player.id
        assert module.player.full_name == test_player.full_name
        
        # Test reverse relationship
        assert len(test_player.modules) >= 1
        assert module in test_player.modules
    
    def test_player_module_constraints(self, db_session, test_player):
        """Test database constraints for PlayerModule."""
        # Test that player_id is required
        with pytest.raises(IntegrityError):
            module = PlayerModule(
                module_type="restaurant",
                level=1
            )
            db_session.add(module)
            db_session.commit()
        
        db_session.rollback()
        
        # Test that module_type is required
        with pytest.raises(IntegrityError):
            module = PlayerModule(
                player_id=test_player.id,
                level=1
            )
            db_session.add(module)
            db_session.commit()
    
    def test_player_module_config_data_json(self, db_session, test_player):
        """Test JSON storage in config_data field."""
        complex_config = {
            "capacity": 50,
            "upgrade_costs": [100, 250, 500, 1000, 2000],
            "effects": {
                "income_multiplier": 1.5,
                "processing_speed": 2.0
            },
            "unlocked_features": ["auto_process", "bulk_transfer"]
        }
        
        module = PlayerModule(
            player_id=test_player.id,
            module_type="photo_studio",
            level=3,
            config_data=complex_config
        )
        
        db_session.add(module)
        db_session.commit()
        
        # Retrieve and verify JSON data
        retrieved_module = db_session.query(PlayerModule).filter_by(id=module.id).first()
        assert retrieved_module.config_data == complex_config
        assert retrieved_module.config_data["capacity"] == 50
        assert retrieved_module.config_data["effects"]["income_multiplier"] == 1.5
    
    def test_player_module_update_timestamp(self, db_session, test_player):
        """Test that last_updated timestamp is updated on modification."""
        module = PlayerModule(
            player_id=test_player.id,
            module_type="dungeon",
            level=0
        )
        
        db_session.add(module)
        db_session.commit()
        
        original_updated = module.last_updated
        
        # Update the module
        module.level = 1
        module.config_data = {"new_feature": True}
        db_session.commit()
        
        assert module.last_updated > original_updated
    
    def test_player_module_repr(self, db_session, test_player):
        """Test string representation of PlayerModule."""
        module = PlayerModule(
            player_id=test_player.id,
            module_type="private_residence",
            level=4
        )
        
        db_session.add(module)
        db_session.commit()
        
        repr_str = repr(module)
        assert f"PlayerModule(id={module.id}" in repr_str
        assert f"player_id={test_player.id}" in repr_str
        assert "type='private_residence'" in repr_str
        assert "level=4" in repr_str


class TestModuleConfig:
    """Test cases for ModuleConfig model."""
    
    def test_create_module_config(self, db_session):
        """Test creating a basic module configuration."""
        config = ModuleConfig(
            module_type="market",
            level=1,
            name_i18n_key="module.market.level1.name",
            description_i18n_key="module.market.level1.description",
            upgrade_cost=500,
            effects={
                "stock_size": 5,
                "refresh_cost": 100,
                "quality_bonus": 0.1
            }
        )
        
        db_session.add(config)
        db_session.commit()
        
        assert config.id is not None
        assert config.module_type == "market"
        assert config.level == 1
        assert config.upgrade_cost == 500
        assert config.effects["stock_size"] == 5
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.updated_at, datetime)
    
    def test_module_config_defaults(self, db_session):
        """Test default values for ModuleConfig."""
        config = ModuleConfig(
            module_type="farm",
            level=0,
            name_i18n_key="module.farm.level0.name",
            description_i18n_key="module.farm.level0.description"
        )
        
        db_session.add(config)
        db_session.commit()
        
        assert config.upgrade_cost == 0
        assert config.effects == {}
    
    def test_module_config_constraints(self, db_session):
        """Test database constraints for ModuleConfig."""
        # Test that module_type is required
        with pytest.raises(IntegrityError):
            config = ModuleConfig(
                level=1,
                name_i18n_key="test.name",
                description_i18n_key="test.description"
            )
            db_session.add(config)
            db_session.commit()
        
        db_session.rollback()
        
        # Test that level is required
        with pytest.raises(IntegrityError):
            config = ModuleConfig(
                module_type="test",
                name_i18n_key="test.name",
                description_i18n_key="test.description"
            )
            db_session.add(config)
            db_session.commit()
    
    def test_module_config_effects_json(self, db_session):
        """Test JSON storage in effects field."""
        complex_effects = {
            "capacity": 100,
            "processing_rates": {
                "meat": 2.0,
                "leather": 1.5,
                "bone": 1.0
            },
            "bonuses": [
                {"type": "quality", "value": 0.2},
                {"type": "speed", "value": 1.5}
            ],
            "unlocks": ["bulk_processing", "quality_enhancement"]
        }
        
        config = ModuleConfig(
            module_type="slaughterhouse",
            level=5,
            name_i18n_key="module.slaughterhouse.level5.name",
            description_i18n_key="module.slaughterhouse.level5.description",
            upgrade_cost=5000,
            effects=complex_effects
        )
        
        db_session.add(config)
        db_session.commit()
        
        # Retrieve and verify JSON data
        retrieved_config = db_session.query(ModuleConfig).filter_by(id=config.id).first()
        assert retrieved_config.effects == complex_effects
        assert retrieved_config.effects["capacity"] == 100
        assert retrieved_config.effects["processing_rates"]["meat"] == 2.0
    
    def test_module_config_update_timestamp(self, db_session):
        """Test that updated_at timestamp is updated on modification."""
        config = ModuleConfig(
            module_type="restaurant",
            level=2,
            name_i18n_key="module.restaurant.level2.name",
            description_i18n_key="module.restaurant.level2.description",
            upgrade_cost=1000
        )
        
        db_session.add(config)
        db_session.commit()
        
        original_updated = config.updated_at
        
        # Update the config
        config.upgrade_cost = 1200
        config.effects = {"cooking_speed": 1.5}
        db_session.commit()
        
        assert config.updated_at > original_updated
    
    def test_module_config_repr(self, db_session):
        """Test string representation of ModuleConfig."""
        config = ModuleConfig(
            module_type="photo_studio",
            level=3,
            name_i18n_key="module.photo_studio.level3.name",
            description_i18n_key="module.photo_studio.level3.description",
            upgrade_cost=2500
        )
        
        db_session.add(config)
        db_session.commit()
        
        repr_str = repr(config)
        assert f"ModuleConfig(id={config.id}" in repr_str
        assert "type='photo_studio'" in repr_str
        assert "level=3" in repr_str
        assert "cost=2500" in repr_str


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(username="testuser", is_admin=False)
    user.set_password("testpassword")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_player(db_session, test_user):
    """Create a test player."""
    player = Player(
        user_id=test_user.id,
        first_name="Test",
        last_name="Player",
        birth_month=6,
        family_background="middle_class",
        childhood_experience="rural",
        education_background="university",
        starting_city="tokyo",
        money=15000,
        current_turn=1
    )
    db_session.add(player)
    db_session.commit()
    return player