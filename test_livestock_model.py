"""
Unit tests for Livestock model
"""
import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.user import User
from app.models.player import Player
from app.models.livestock import Livestock
from app.models.module import PlayerModule


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
def test_player(db_session, test_user):
    """Create a test player."""
    player = Player(
        user_id=test_user.id,
        first_name="Test",
        last_name="Player",
        birth_month=6,
        family_background="middle_class",
        childhood_experience="city_life",
        education_background="university",
        starting_city="town",
        money=15000,
        current_turn=5
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player


@pytest.fixture
def test_module(db_session, test_player):
    """Create a test player module."""
    module = PlayerModule(
        player_id=test_player.id,
        module_type="farm",
        level=2
    )
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)
    return module


class TestLivestockModel:
    """Test cases for Livestock model."""
    
    def test_livestock_creation(self, db_session, test_player):
        """Test basic livestock creation."""
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.cow.bessie",
            family_i18n_key="livestock.family.bovine",
            nation_i18n_key="livestock.nation.holstein",
            city_i18n_key="livestock.city.farmville",
            pic_url="/images/livestock/cow_001.jpg",
            age=24,
            bloodtype_i18n_key="livestock.bloodtype.a",
            zodiac_i18n_key="livestock.zodiac.taurus",
            origin_i18n_key="livestock.origin.domestic",
            rank_i18n_key="livestock.rank.common",
            acquire_turn=3,
            quality=1.5,
            height=150.5,
            weight=450.0
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        assert livestock.id is not None
        assert len(livestock.id) == 36  # UUID length
        assert livestock.owner_id == test_player.id
        assert livestock.name_i18n_key == "livestock.cow.bessie"
        assert livestock.family_i18n_key == "livestock.family.bovine"
        assert livestock.age == 24
        assert livestock.quality == 1.5
        assert livestock.height == 150.5
        assert livestock.weight == 450.0
        assert livestock.created_at is not None
        assert livestock.updated_at is not None
        assert isinstance(livestock.created_at, datetime)
    
    def test_livestock_default_values(self, db_session, test_player):
        """Test livestock model default values."""
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.pig.wilbur",
            family_i18n_key="livestock.family.swine",
            nation_i18n_key="livestock.nation.yorkshire",
            city_i18n_key="livestock.city.barnyard",
            pic_url="/images/livestock/pig_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.o",
            zodiac_i18n_key="livestock.zodiac.pig",
            origin_i18n_key="livestock.origin.wild",
            rank_i18n_key="livestock.rank.rare",
            acquire_turn=1,
            height=80.0,
            weight=120.0
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        assert livestock.age == 0  # Default age
        assert livestock.quality == 1.0  # Default quality
        assert livestock.father_id is None  # Default parent
        assert livestock.mother_id is None  # Default parent
        assert livestock.current_location_module_id is None  # Default location
        assert livestock.custom_data == {}  # Default custom data
    
    def test_livestock_uuid_generation(self, db_session, test_player):
        """Test that each livestock gets a unique UUID."""
        livestock1 = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.sheep.dolly",
            family_i18n_key="livestock.family.ovine",
            nation_i18n_key="livestock.nation.merino",
            city_i18n_key="livestock.city.pasture",
            pic_url="/images/livestock/sheep_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.b",
            zodiac_i18n_key="livestock.zodiac.sheep",
            origin_i18n_key="livestock.origin.domestic",
            rank_i18n_key="livestock.rank.uncommon",
            acquire_turn=2,
            height=90.0,
            weight=65.0
        )
        
        livestock2 = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.goat.billy",
            family_i18n_key="livestock.family.caprine",
            nation_i18n_key="livestock.nation.nubian",
            city_i18n_key="livestock.city.hillside",
            pic_url="/images/livestock/goat_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.ab",
            zodiac_i18n_key="livestock.zodiac.goat",
            origin_i18n_key="livestock.origin.mountain",
            rank_i18n_key="livestock.rank.epic",
            acquire_turn=4,
            height=75.0,
            weight=55.0
        )
        
        db_session.add_all([livestock1, livestock2])
        db_session.commit()
        
        assert livestock1.id != livestock2.id
        assert len(livestock1.id) == 36
        assert len(livestock2.id) == 36
        
        # Verify they are valid UUIDs
        uuid.UUID(livestock1.id)
        uuid.UUID(livestock2.id)
    
    def test_livestock_owner_relationship(self, db_session, test_player):
        """Test relationship between Livestock and Player."""
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.horse.thunder",
            family_i18n_key="livestock.family.equine",
            nation_i18n_key="livestock.nation.arabian",
            city_i18n_key="livestock.city.stable",
            pic_url="/images/livestock/horse_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.a",
            zodiac_i18n_key="livestock.zodiac.horse",
            origin_i18n_key="livestock.origin.desert",
            rank_i18n_key="livestock.rank.legendary",
            acquire_turn=1,
            height=160.0,
            weight=500.0
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        # Test forward relationship
        assert livestock.owner is not None
        assert livestock.owner.id == test_player.id
        assert livestock.owner.first_name == test_player.first_name
        
        # Test backward relationship
        assert len(test_player.livestock) == 1
        assert test_player.livestock[0].id == livestock.id
    
    def test_livestock_breeding_relationships(self, db_session, test_player):
        """Test breeding relationships between livestock."""
        # Create parent livestock
        father = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.bull.ferdinand",
            family_i18n_key="livestock.family.bovine",
            nation_i18n_key="livestock.nation.angus",
            city_i18n_key="livestock.city.ranch",
            pic_url="/images/livestock/bull_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.o",
            zodiac_i18n_key="livestock.zodiac.ox",
            origin_i18n_key="livestock.origin.highland",
            rank_i18n_key="livestock.rank.rare",
            acquire_turn=1,
            height=170.0,
            weight=800.0
        )
        
        mother = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.cow.moobert",
            family_i18n_key="livestock.family.bovine",
            nation_i18n_key="livestock.nation.jersey",
            city_i18n_key="livestock.city.dairy",
            pic_url="/images/livestock/cow_002.jpg",
            bloodtype_i18n_key="livestock.bloodtype.a",
            zodiac_i18n_key="livestock.zodiac.ox",
            origin_i18n_key="livestock.origin.island",
            rank_i18n_key="livestock.rank.uncommon",
            acquire_turn=1,
            height=140.0,
            weight=400.0
        )
        
        db_session.add_all([father, mother])
        db_session.commit()
        db_session.refresh(father)
        db_session.refresh(mother)
        
        # Create offspring
        offspring = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.calf.junior",
            family_i18n_key="livestock.family.bovine",
            nation_i18n_key="livestock.nation.crossbreed",
            city_i18n_key="livestock.city.nursery",
            pic_url="/images/livestock/calf_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.a",
            zodiac_i18n_key="livestock.zodiac.ox",
            origin_i18n_key="livestock.origin.bred",
            rank_i18n_key="livestock.rank.common",
            acquire_turn=5,
            height=60.0,
            weight=80.0,
            father_id=father.id,
            mother_id=mother.id
        )
        
        db_session.add(offspring)
        db_session.commit()
        db_session.refresh(offspring)
        
        # Test parent relationships
        assert offspring.father is not None
        assert offspring.father.id == father.id
        assert offspring.father.name_i18n_key == "livestock.bull.ferdinand"
        
        assert offspring.mother is not None
        assert offspring.mother.id == mother.id
        assert offspring.mother.name_i18n_key == "livestock.cow.moobert"
    
    def test_livestock_location_relationship(self, db_session, test_player, test_module):
        """Test relationship between Livestock and PlayerModule."""
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.chicken.henrietta",
            family_i18n_key="livestock.family.poultry",
            nation_i18n_key="livestock.nation.rhode_island_red",
            city_i18n_key="livestock.city.coop",
            pic_url="/images/livestock/chicken_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.b",
            zodiac_i18n_key="livestock.zodiac.rooster",
            origin_i18n_key="livestock.origin.domestic",
            rank_i18n_key="livestock.rank.common",
            acquire_turn=2,
            height=30.0,
            weight=2.5,
            current_location_module_id=test_module.id
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        # Test location relationship
        assert livestock.current_location is not None
        assert livestock.current_location.id == test_module.id
        assert livestock.current_location.module_type == "farm"
        assert livestock.current_location.level == 2
    
    def test_livestock_custom_data(self, db_session, test_player):
        """Test custom data storage in livestock."""
        custom_data = {
            "special_abilities": ["milk_production", "cheese_making"],
            "personality_traits": {"friendliness": 8, "stubbornness": 3},
            "breeding_history": {
                "offspring_count": 5,
                "last_breeding_turn": 10
            },
            "awards": ["Best in Show 2023", "Milk Production Champion"]
        }
        
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.cow.champion",
            family_i18n_key="livestock.family.bovine",
            nation_i18n_key="livestock.nation.holstein",
            city_i18n_key="livestock.city.showground",
            pic_url="/images/livestock/cow_champion.jpg",
            bloodtype_i18n_key="livestock.bloodtype.a",
            zodiac_i18n_key="livestock.zodiac.ox",
            origin_i18n_key="livestock.origin.premium",
            rank_i18n_key="livestock.rank.legendary",
            acquire_turn=1,
            height=155.0,
            weight=480.0,
            custom_data=custom_data
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        assert livestock.custom_data == custom_data
        assert livestock.custom_data["special_abilities"] == ["milk_production", "cheese_making"]
        assert livestock.custom_data["personality_traits"]["friendliness"] == 8
        assert livestock.custom_data["breeding_history"]["offspring_count"] == 5
        assert "Best in Show 2023" in livestock.custom_data["awards"]
    
    def test_livestock_repr(self, db_session, test_player):
        """Test livestock string representation."""
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.duck.quackers",
            family_i18n_key="livestock.family.waterfowl",
            nation_i18n_key="livestock.nation.mallard",
            city_i18n_key="livestock.city.pond",
            pic_url="/images/livestock/duck_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.o",
            zodiac_i18n_key="livestock.zodiac.duck",
            origin_i18n_key="livestock.origin.wetland",
            rank_i18n_key="livestock.rank.common",
            acquire_turn=3,
            quality=1.2,
            height=25.0,
            weight=1.8
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        expected_repr = f"<Livestock(id={livestock.id}, name_key='livestock.duck.quackers', quality=1.2, owner_id={test_player.id})>"
        assert repr(livestock) == expected_repr
    
    def test_livestock_timestamps(self, db_session, test_player):
        """Test that timestamps are properly set and updated."""
        livestock = Livestock(
            owner_id=test_player.id,
            name_i18n_key="livestock.rabbit.bugs",
            family_i18n_key="livestock.family.lagomorph",
            nation_i18n_key="livestock.nation.cottontail",
            city_i18n_key="livestock.city.burrow",
            pic_url="/images/livestock/rabbit_001.jpg",
            bloodtype_i18n_key="livestock.bloodtype.ab",
            zodiac_i18n_key="livestock.zodiac.rabbit",
            origin_i18n_key="livestock.origin.forest",
            rank_i18n_key="livestock.rank.uncommon",
            acquire_turn=4,
            height=20.0,
            weight=1.5
        )
        
        db_session.add(livestock)
        db_session.commit()
        db_session.refresh(livestock)
        
        created_time = livestock.created_at
        updated_time = livestock.updated_at
        
        assert created_time is not None
        assert updated_time is not None
        assert created_time == updated_time  # Should be same on creation
        
        # Update the livestock
        livestock.quality = 2.0
        db_session.commit()
        db_session.refresh(livestock)
        
        assert livestock.created_at == created_time  # Should not change
        assert livestock.updated_at > updated_time  # Should be updated


if __name__ == "__main__":
    pytest.main([__file__])