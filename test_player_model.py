"""
Unit tests for Player model and character creation functionality
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.user import User
from app.models.player import Player
from app.models.module import PlayerModule
from app.services.character_service import CharacterCreationService


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        password_hash="hashed_password",
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def character_service(db_session):
    """Create a character creation service instance."""
    return CharacterCreationService(db_session)


class TestPlayerModel:
    """Test cases for Player model."""
    
    def test_player_creation(self, db_session, test_user):
        """Test basic player creation."""
        player = Player(
            user_id=test_user.id,
            first_name="John",
            last_name="Doe",
            birth_month=6,
            family_background="middle_class",
            childhood_experience="city_life",
            education_background="university",
            starting_city="metropolis",
            money=15000,
            current_turn=1
        )
        
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        assert player.id is not None
        assert player.user_id == test_user.id
        assert player.first_name == "John"
        assert player.last_name == "Doe"
        assert player.birth_month == 6
        assert player.money == 15000
        assert player.current_turn == 1
        assert player.created_at is not None
        assert isinstance(player.created_at, datetime)
    
    def test_player_full_name_property(self, db_session, test_user):
        """Test the full_name property."""
        player = Player(
            user_id=test_user.id,
            first_name="Jane",
            last_name="Smith",
            birth_month=3,
            family_background="wealthy",
            childhood_experience="rural_life",
            education_background="trade_school",
            starting_city="village"
        )
        
        db_session.add(player)
        db_session.commit()
        
        assert player.full_name == "Jane Smith"
    
    def test_player_default_values(self, db_session, test_user):
        """Test player model default values."""
        player = Player(
            user_id=test_user.id,
            first_name="Default",
            last_name="Player",
            birth_month=1,
            family_background="middle_class",
            childhood_experience="city_life",
            education_background="university",
            starting_city="town"
        )
        
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        assert player.money == 10000  # Default money
        assert player.current_turn == 1  # Default turn
        assert player.last_played is None  # Default last_played
    
    def test_player_user_relationship(self, db_session, test_user):
        """Test relationship between Player and User."""
        player = Player(
            user_id=test_user.id,
            first_name="Related",
            last_name="Player",
            birth_month=12,
            family_background="poor",
            childhood_experience="hardship",
            education_background="none",
            starting_city="village"
        )
        
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Test forward relationship
        assert player.user is not None
        assert player.user.id == test_user.id
        assert player.user.username == test_user.username
    
    def test_player_repr(self, db_session, test_user):
        """Test player string representation."""
        player = Player(
            user_id=test_user.id,
            first_name="Repr",
            last_name="Test",
            birth_month=8,
            family_background="farming",
            childhood_experience="rural_life",
            education_background="self_taught",
            starting_city="village",
            money=8500,
            current_turn=5
        )
        
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        expected_repr = f"<Player(id={player.id}, name='Repr Test', money=8500, turn=5)>"
        assert repr(player) == expected_repr


class TestCharacterCreationService:
    """Test cases for CharacterCreationService."""
    
    def test_calculate_starting_attributes_default(self, character_service):
        """Test starting attribute calculation with default values."""
        character_data = {
            "birth_month": 1,
            "family_background": "middle_class",
            "childhood_experience": "city_life",
            "education_background": "university",
            "starting_city": "town"
        }
        
        attributes = character_service.calculate_starting_attributes(character_data)
        
        # Base: 10000, January: +0, middle_class: +0, city_life: +1000, university: +2000, town: +0
        expected_money = 10000 + 0 + 0 + 1000 + 2000 + 0
        assert attributes["starting_money"] == expected_money
        assert len(attributes["perks"]) == 5
        assert "new_beginnings" in attributes["perks"]
        assert "balanced_start" in attributes["perks"]
        assert "urban_knowledge" in attributes["perks"]
        assert "analytical_mind" in attributes["perks"]
        assert "community_ties" in attributes["perks"]
    
    def test_calculate_starting_attributes_wealthy_background(self, character_service):
        """Test starting attributes with wealthy background."""
        character_data = {
            "birth_month": 12,  # +1000
            "family_background": "wealthy",  # +5000
            "childhood_experience": "traveled_much",  # +0
            "education_background": "military",  # +1000
            "starting_city": "metropolis"  # +1500
        }
        
        attributes = character_service.calculate_starting_attributes(character_data)
        
        # Base: 10000, December: +1000, wealthy: +5000, traveled: +0, military: +1000, metropolis: +1500
        expected_money = 10000 + 1000 + 5000 + 0 + 1000 + 1500
        assert attributes["starting_money"] == expected_money
        assert attributes["money_bonus"] == 8500
        assert "year_end_fortune" in attributes["perks"]
        assert "business_acumen" in attributes["perks"]
    
    def test_calculate_starting_attributes_poor_background(self, character_service):
        """Test starting attributes with poor background."""
        character_data = {
            "birth_month": 1,  # +0
            "family_background": "poor",  # -3000
            "childhood_experience": "hardship",  # -1000
            "education_background": "none",  # -1500
            "starting_city": "village"  # -1000
        }
        
        attributes = character_service.calculate_starting_attributes(character_data)
        
        # Base: 10000, bonuses: -6500 = 3500 (above minimum of 1000)
        assert attributes["starting_money"] == 3500
        assert attributes["money_bonus"] == -6500
        assert "resilience" in attributes["perks"]
        assert "resourceful" in attributes["perks"]
    
    def test_calculate_starting_attributes_minimum_money_enforced(self, character_service):
        """Test that minimum money is enforced when calculation goes below 1000."""
        # Create a scenario that would result in very low money
        # We need to modify the service temporarily to test this
        original_base = character_service.BASE_MONEY
        character_service.BASE_MONEY = 5000  # Lower base to trigger minimum
        
        character_data = {
            "birth_month": 1,  # +0
            "family_background": "poor",  # -3000
            "childhood_experience": "hardship",  # -1000
            "education_background": "none",  # -1500
            "starting_city": "village"  # -1000
        }
        
        attributes = character_service.calculate_starting_attributes(character_data)
        
        # Base: 5000, bonuses: -6500 = -1500, but minimum is 1000
        assert attributes["starting_money"] == 1000  # Minimum enforced
        assert attributes["money_bonus"] == -6500
        
        # Restore original base
        character_service.BASE_MONEY = original_base
    
    def test_create_player_success(self, character_service, test_user):
        """Test successful player creation."""
        character_data = {
            "first_name": "Test",
            "last_name": "Character",
            "birth_month": 6,
            "family_background": "merchant",
            "childhood_experience": "sheltered",
            "education_background": "trade_school",
            "starting_city": "coastal"
        }
        
        player = character_service.create_player(test_user.id, character_data)
        
        assert player.id is not None
        assert player.user_id == test_user.id
        assert player.first_name == "Test"
        assert player.last_name == "Character"
        assert player.birth_month == 6
        assert player.family_background == "merchant"
        assert player.childhood_experience == "sheltered"
        assert player.education_background == "trade_school"
        assert player.starting_city == "coastal"
        assert player.current_turn == 1
        
        # Check calculated money (base 10000 + June:500 + merchant:2000 + sheltered:500 + trade_school:500 + coastal:500 = 14000)
        assert player.money == 14000
        
        # Check that default modules were created
        assert len(player.modules) == 7
        module_types = [module.module_type for module in player.modules]
        expected_modules = ["market", "farm", "slaughterhouse", "restaurant", "photo_studio", "dungeon", "private_residence"]
        for expected_module in expected_modules:
            assert expected_module in module_types
        
        # All modules should start at level 0
        for module in player.modules:
            assert module.level == 0
    
    def test_create_player_missing_required_field(self, character_service, test_user):
        """Test player creation with missing required field."""
        character_data = {
            "first_name": "Test",
            # Missing last_name
            "birth_month": 6,
            "family_background": "middle_class",
            "childhood_experience": "city_life",
            "education_background": "university",
            "starting_city": "town"
        }
        
        with pytest.raises(ValueError, match="Missing required field: last_name"):
            character_service.create_player(test_user.id, character_data)
    
    def test_create_player_invalid_birth_month(self, character_service, test_user):
        """Test player creation with invalid birth month."""
        character_data = {
            "first_name": "Test",
            "last_name": "Character",
            "birth_month": 13,  # Invalid month
            "family_background": "middle_class",
            "childhood_experience": "city_life",
            "education_background": "university",
            "starting_city": "town"
        }
        
        with pytest.raises(ValueError, match="Birth month must be an integer between 1 and 12"):
            character_service.create_player(test_user.id, character_data)
    
    def test_get_character_creation_options(self, character_service):
        """Test getting character creation options."""
        options = character_service.get_character_creation_options()
        
        assert "family_backgrounds" in options
        assert "childhood_experiences" in options
        assert "education_backgrounds" in options
        assert "starting_cities" in options
        assert "birth_months" in options
        
        assert "wealthy" in options["family_backgrounds"]
        assert "poor" in options["family_backgrounds"]
        assert "city_life" in options["childhood_experiences"]
        assert "university" in options["education_backgrounds"]
        assert "metropolis" in options["starting_cities"]
        assert options["birth_months"] == list(range(1, 13))
    
    def test_preview_starting_attributes(self, character_service):
        """Test previewing starting attributes without creating player."""
        character_data = {
            "birth_month": 10,
            "family_background": "wealthy",
            "childhood_experience": "traveled_much",
            "education_background": "university",
            "starting_city": "metropolis"
        }
        
        preview = character_service.preview_starting_attributes(character_data)
        
        # Should return same calculation as calculate_starting_attributes
        expected = character_service.calculate_starting_attributes(character_data)
        assert preview == expected
        assert preview["starting_money"] == expected["starting_money"]
        assert preview["perks"] == expected["perks"]
        assert preview["money_bonus"] == expected["money_bonus"]


if __name__ == "__main__":
    pytest.main([__file__])