#!/usr/bin/env python3
"""
Database translation seeding script for Park Tycoon.

This script seeds the database with initial translation data for supported languages.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlalchemy.orm import Session
from app.core.database import sync_engine, Base
from app.models.translation import Translation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Initial translation data
INITIAL_TRANSLATIONS = {
    # UI Elements
    "ui.welcome": {
        "en": "Welcome to Park Tycoon",
        "zh": "欢迎来到公园大亨",
        "es": "Bienvenido a Park Tycoon",
        "fr": "Bienvenue à Park Tycoon"
    },
    "ui.login": {
        "en": "Login",
        "zh": "登录",
        "es": "Iniciar sesión",
        "fr": "Connexion"
    },
    "ui.register": {
        "en": "Register",
        "zh": "注册",
        "es": "Registrarse",
        "fr": "S'inscrire"
    },
    "ui.logout": {
        "en": "Logout",
        "zh": "登出",
        "es": "Cerrar sesión",
        "fr": "Déconnexion"
    },
    "ui.username": {
        "en": "Username",
        "zh": "用户名",
        "es": "Nombre de usuario",
        "fr": "Nom d'utilisateur"
    },
    "ui.password": {
        "en": "Password",
        "zh": "密码",
        "es": "Contraseña",
        "fr": "Mot de passe"
    },
    "ui.dashboard": {
        "en": "Dashboard",
        "zh": "仪表板",
        "es": "Panel de control",
        "fr": "Tableau de bord"
    },
    "ui.park": {
        "en": "Park",
        "zh": "公园",
        "es": "Parque",
        "fr": "Parc"
    },
    "ui.money": {
        "en": "Money",
        "zh": "金钱",
        "es": "Dinero",
        "fr": "Argent"
    },
    "ui.turn": {
        "en": "Turn",
        "zh": "回合",
        "es": "Turno",
        "fr": "Tour"
    },
    
    # Module Names
    "module.market": {
        "en": "Market",
        "zh": "市场",
        "es": "Mercado",
        "fr": "Marché"
    },
    "module.farm": {
        "en": "Farm",
        "zh": "农场",
        "es": "Granja",
        "fr": "Ferme"
    },
    "module.slaughterhouse": {
        "en": "Slaughterhouse",
        "zh": "屠宰场",
        "es": "Matadero",
        "fr": "Abattoir"
    },
    "module.restaurant": {
        "en": "Restaurant",
        "zh": "餐厅",
        "es": "Restaurante",
        "fr": "Restaurant"
    },
    "module.photo_studio": {
        "en": "Photo Studio",
        "zh": "摄影棚",
        "es": "Estudio fotográfico",
        "fr": "Studio photo"
    },
    "module.dungeon": {
        "en": "Dungeon",
        "zh": "地牢",
        "es": "Mazmorra",
        "fr": "Donjon"
    },
    "module.private_residence": {
        "en": "Private Residence",
        "zh": "私人住宅",
        "es": "Residencia privada",
        "fr": "Résidence privée"
    },
    
    # Livestock Categories
    "livestock.cattle": {
        "en": "Cattle",
        "zh": "牛",
        "es": "Ganado",
        "fr": "Bétail"
    },
    "livestock.pig": {
        "en": "Pig",
        "zh": "猪",
        "es": "Cerdo",
        "fr": "Porc"
    },
    "livestock.chicken": {
        "en": "Chicken",
        "zh": "鸡",
        "es": "Pollo",
        "fr": "Poulet"
    },
    "livestock.sheep": {
        "en": "Sheep",
        "zh": "羊",
        "es": "Oveja",
        "fr": "Mouton"
    },
    
    # Game Actions
    "action.buy": {
        "en": "Buy",
        "zh": "购买",
        "es": "Comprar",
        "fr": "Acheter"
    },
    "action.sell": {
        "en": "Sell",
        "zh": "出售",
        "es": "Vender",
        "fr": "Vendre"
    },
    "action.upgrade": {
        "en": "Upgrade",
        "zh": "升级",
        "es": "Mejorar",
        "fr": "Améliorer"
    },
    "action.process": {
        "en": "Process",
        "zh": "处理",
        "es": "Procesar",
        "fr": "Traiter"
    },
    "action.cook": {
        "en": "Cook",
        "zh": "烹饪",
        "es": "Cocinar",
        "fr": "Cuisiner"
    },
    
    # Character Creation
    "character.first_name": {
        "en": "First Name",
        "zh": "名字",
        "es": "Nombre",
        "fr": "Prénom"
    },
    "character.last_name": {
        "en": "Last Name",
        "zh": "姓氏",
        "es": "Apellido",
        "fr": "Nom de famille"
    },
    "character.birth_month": {
        "en": "Birth Month",
        "zh": "出生月份",
        "es": "Mes de nacimiento",
        "fr": "Mois de naissance"
    },
    
    # Error Messages
    "error.invalid_credentials": {
        "en": "Invalid username or password",
        "zh": "用户名或密码无效",
        "es": "Nombre de usuario o contraseña inválidos",
        "fr": "Nom d'utilisateur ou mot de passe invalide"
    },
    "error.insufficient_funds": {
        "en": "Insufficient funds",
        "zh": "资金不足",
        "es": "Fondos insuficientes",
        "fr": "Fonds insuffisants"
    },
    "error.not_found": {
        "en": "Not found",
        "zh": "未找到",
        "es": "No encontrado",
        "fr": "Non trouvé"
    }
}

def get_category_from_key(key: str) -> str:
    """Extract category from translation key."""
    if "." in key:
        return key.split(".")[0]
    return "general"

def seed_translations(session: Session) -> None:
    """Seed the database with initial translation data."""
    logger.info("Starting translation seeding...")
    
    # Check if translations already exist
    existing_count = session.query(Translation).count()
    if existing_count > 0:
        logger.warning(f"Found {existing_count} existing translations. Skipping seeding.")
        return
    
    translations_added = 0
    
    for key, translations in INITIAL_TRANSLATIONS.items():
        category = get_category_from_key(key)
        
        for language_code, value in translations.items():
            translation = Translation(
                key=key,
                language_code=language_code,
                value=value,
                category=category,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(translation)
            translations_added += 1
    
    try:
        session.commit()
        logger.info(f"✓ Successfully added {translations_added} translations")
        
        # Log summary by language
        for lang in ["en", "zh", "es", "fr"]:
            count = session.query(Translation).filter(Translation.language_code == lang).count()
            logger.info(f"  - {lang}: {count} translations")
            
    except Exception as e:
        session.rollback()
        logger.error(f"✗ Failed to seed translations: {e}")
        raise

def main():
    """Main function."""
    try:
        logger.info("Initializing database connection...")
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=sync_engine)
        
        # Create session and seed translations
        with Session(sync_engine) as session:
            seed_translations(session)
        
        logger.info("Translation seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"✗ Translation seeding failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()