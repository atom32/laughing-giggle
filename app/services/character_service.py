"""
Character creation service for calculating starting attributes and initializing player data
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.user import User
from app.models.module import PlayerModule


class CharacterCreationService:
    """Service for handling character creation logic and calculations."""
    
    # Character creation options and their effects
    FAMILY_BACKGROUND_EFFECTS = {
        "wealthy": {"money_bonus": 5000, "perk": "business_acumen"},
        "middle_class": {"money_bonus": 0, "perk": "balanced_start"},
        "poor": {"money_bonus": -3000, "perk": "resourceful"},
        "farming": {"money_bonus": -1000, "perk": "animal_affinity"},
        "merchant": {"money_bonus": 2000, "perk": "negotiation"}
    }
    
    CHILDHOOD_EXPERIENCE_EFFECTS = {
        "city_life": {"money_bonus": 1000, "perk": "urban_knowledge"},
        "rural_life": {"money_bonus": -500, "perk": "nature_connection"},
        "traveled_much": {"money_bonus": 0, "perk": "worldly_wisdom"},
        "sheltered": {"money_bonus": 500, "perk": "focused_learning"},
        "hardship": {"money_bonus": -1000, "perk": "resilience"}
    }
    
    EDUCATION_BACKGROUND_EFFECTS = {
        "university": {"money_bonus": 2000, "perk": "analytical_mind"},
        "trade_school": {"money_bonus": 500, "perk": "practical_skills"},
        "self_taught": {"money_bonus": -500, "perk": "autodidact"},
        "military": {"money_bonus": 1000, "perk": "discipline"},
        "none": {"money_bonus": -1500, "perk": "street_smart"}
    }
    
    STARTING_CITY_EFFECTS = {
        "metropolis": {"money_bonus": 1500, "perk": "market_access"},
        "town": {"money_bonus": 0, "perk": "community_ties"},
        "village": {"money_bonus": -1000, "perk": "simple_living"},
        "coastal": {"money_bonus": 500, "perk": "trade_routes"},
        "mountain": {"money_bonus": -500, "perk": "hardy_constitution"}
    }
    
    BIRTH_MONTH_EFFECTS = {
        1: {"money_bonus": 0, "perk": "new_beginnings"},    # January
        2: {"money_bonus": 200, "perk": "love_affinity"},   # February
        3: {"money_bonus": 300, "perk": "spring_energy"},   # March
        4: {"money_bonus": 400, "perk": "growth_mindset"},  # April
        5: {"money_bonus": 500, "perk": "blooming_luck"},   # May
        6: {"money_bonus": 500, "perk": "summer_warmth"},   # June  # Fixed: was 300
        7: {"money_bonus": 100, "perk": "independence"},    # July
        8: {"money_bonus": 600, "perk": "harvest_wisdom"},  # August
        9: {"money_bonus": 400, "perk": "autumn_balance"},  # September
        10: {"money_bonus": 800, "perk": "halloween_mystery"}, # October
        11: {"money_bonus": 200, "perk": "gratitude"},      # November
        12: {"money_bonus": 1000, "perk": "year_end_fortune"} # December
    }
    
    BASE_MONEY = 10000
    DEFAULT_MODULES = [
        "market", "farm", "slaughterhouse", "restaurant", 
        "photo_studio", "dungeon", "private_residence"
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_starting_attributes(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate starting money and perks based on character creation choices.
        
        Args:
            character_data: Dictionary containing character creation choices
            
        Returns:
            Dictionary with calculated starting money and perks
        """
        total_money_bonus = 0
        perks = []
        
        # Calculate bonuses from each choice
        family_bg = character_data.get("family_background", "middle_class")
        if family_bg in self.FAMILY_BACKGROUND_EFFECTS:
            effect = self.FAMILY_BACKGROUND_EFFECTS[family_bg]
            total_money_bonus += effect["money_bonus"]
            perks.append(effect["perk"])
        
        childhood_exp = character_data.get("childhood_experience", "city_life")
        if childhood_exp in self.CHILDHOOD_EXPERIENCE_EFFECTS:
            effect = self.CHILDHOOD_EXPERIENCE_EFFECTS[childhood_exp]
            total_money_bonus += effect["money_bonus"]
            perks.append(effect["perk"])
        
        education_bg = character_data.get("education_background", "university")
        if education_bg in self.EDUCATION_BACKGROUND_EFFECTS:
            effect = self.EDUCATION_BACKGROUND_EFFECTS[education_bg]
            total_money_bonus += effect["money_bonus"]
            perks.append(effect["perk"])
        
        starting_city = character_data.get("starting_city", "town")
        if starting_city in self.STARTING_CITY_EFFECTS:
            effect = self.STARTING_CITY_EFFECTS[starting_city]
            total_money_bonus += effect["money_bonus"]
            perks.append(effect["perk"])
        
        birth_month = character_data.get("birth_month", 1)
        if birth_month in self.BIRTH_MONTH_EFFECTS:
            effect = self.BIRTH_MONTH_EFFECTS[birth_month]
            total_money_bonus += effect["money_bonus"]
            perks.append(effect["perk"])
        
        # Calculate final starting money (minimum 1000)
        starting_money = max(1000, self.BASE_MONEY + total_money_bonus)
        
        return {
            "starting_money": starting_money,
            "perks": perks,
            "money_bonus": total_money_bonus
        }
    
    def create_player(self, user_id: int, character_data: Dict[str, Any]) -> Player:
        """
        Create a new player with calculated starting attributes.
        
        Args:
            user_id: ID of the user creating the character
            character_data: Character creation form data
            
        Returns:
            Created Player instance
        """
        # Validate required fields
        required_fields = [
            "first_name", "last_name", "birth_month", "family_background",
            "childhood_experience", "education_background", "starting_city"
        ]
        
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate birth month
        birth_month = character_data["birth_month"]
        if not isinstance(birth_month, int) or birth_month < 1 or birth_month > 12:
            raise ValueError("Birth month must be an integer between 1 and 12")
        
        # Calculate starting attributes
        attributes = self.calculate_starting_attributes(character_data)
        
        # Create player
        player = Player(
            user_id=user_id,
            first_name=character_data["first_name"].strip(),
            last_name=character_data["last_name"].strip(),
            birth_month=birth_month,
            family_background=character_data["family_background"],
            childhood_experience=character_data["childhood_experience"],
            education_background=character_data["education_background"],
            starting_city=character_data["starting_city"],
            money=attributes["starting_money"],
            current_turn=1
        )
        
        self.db.add(player)
        self.db.flush()  # Get the player ID
        
        # Initialize default modules at level 0
        self._initialize_default_modules(player.id)
        
        self.db.commit()
        return player
    
    def _initialize_default_modules(self, player_id: int) -> None:
        """Initialize default park modules at level 0 for new player."""
        for module_type in self.DEFAULT_MODULES:
            module = PlayerModule(
                player_id=player_id,
                module_type=module_type,
                level=0
            )
            self.db.add(module)
    
    def get_character_creation_options(self) -> Dict[str, Any]:
        """
        Get available character creation options and their descriptions.
        
        Returns:
            Dictionary with all available options for character creation
        """
        return {
            "family_backgrounds": list(self.FAMILY_BACKGROUND_EFFECTS.keys()),
            "childhood_experiences": list(self.CHILDHOOD_EXPERIENCE_EFFECTS.keys()),
            "education_backgrounds": list(self.EDUCATION_BACKGROUND_EFFECTS.keys()),
            "starting_cities": list(self.STARTING_CITY_EFFECTS.keys()),
            "birth_months": list(range(1, 13))
        }
    
    def preview_starting_attributes(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview what the starting attributes would be for given character data.
        
        Args:
            character_data: Character creation choices
            
        Returns:
            Preview of calculated attributes without creating a player
        """
        return self.calculate_starting_attributes(character_data)