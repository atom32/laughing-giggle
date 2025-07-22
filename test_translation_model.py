"""
Unit tests for Translation model operations.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models.translation import Translation


# Test database setup
@pytest.fixture
def test_db():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


class TestTranslationModel:
    """Test cases for Translation model."""
    
    def test_create_translation(self, test_db):
        """Test creating a new translation."""
        translation = Translation(
            key="test.key",
            language_code="en",
            value="Test Value",
            category="test"
        )
        
        test_db.add(translation)
        test_db.commit()
        
        # Verify the translation was created
        saved_translation = test_db.query(Translation).filter(
            Translation.key == "test.key",
            Translation.language_code == "en"
        ).first()
        
        assert saved_translation is not None
        assert saved_translation.key == "test.key"
        assert saved_translation.language_code == "en"
        assert saved_translation.value == "Test Value"
        assert saved_translation.category == "test"
        assert saved_translation.created_at is not None
        assert saved_translation.updated_at is not None
    
    def test_translation_unique_constraint(self, test_db):
        """Test that key-language combinations must be unique."""
        # Create first translation
        translation1 = Translation(
            key="duplicate.key",
            language_code="en",
            value="First Value",
            category="test"
        )
        test_db.add(translation1)
        test_db.commit()
        
        # Try to create duplicate key-language combination
        translation2 = Translation(
            key="duplicate.key",
            language_code="en",
            value="Second Value",
            category="test"
        )
        test_db.add(translation2)
        
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_same_key_different_languages(self, test_db):
        """Test that same key can exist for different languages."""
        # Create English translation
        translation_en = Translation(
            key="multi.lang",
            language_code="en",
            value="English Value",
            category="test"
        )
        test_db.add(translation_en)
        
        # Create Chinese translation with same key
        translation_zh = Translation(
            key="multi.lang",
            language_code="zh",
            value="中文值",
            category="test"
        )
        test_db.add(translation_zh)
        
        test_db.commit()
        
        # Verify both translations exist
        translations = test_db.query(Translation).filter(
            Translation.key == "multi.lang"
        ).all()
        
        assert len(translations) == 2
        
        # Verify language-specific retrieval
        en_translation = test_db.query(Translation).filter(
            Translation.key == "multi.lang",
            Translation.language_code == "en"
        ).first()
        assert en_translation.value == "English Value"
        
        zh_translation = test_db.query(Translation).filter(
            Translation.key == "multi.lang",
            Translation.language_code == "zh"
        ).first()
        assert zh_translation.value == "中文值"
    
    def test_translation_categories(self, test_db):
        """Test translation categorization."""
        categories = ["ui", "livestock", "module", "error"]
        
        for i, category in enumerate(categories):
            translation = Translation(
                key=f"{category}.test_{i}",
                language_code="en",
                value=f"Test {category} value",
                category=category
            )
            test_db.add(translation)
        
        test_db.commit()
        
        # Test category filtering
        ui_translations = test_db.query(Translation).filter(
            Translation.category == "ui"
        ).all()
        assert len(ui_translations) == 1
        assert ui_translations[0].key == "ui.test_0"
        
        # Test category count
        total_categories = test_db.query(Translation.category).distinct().count()
        assert total_categories == 4
    
    def test_translation_default_category(self, test_db):
        """Test default category assignment."""
        translation = Translation(
            key="no.category",
            language_code="en",
            value="No category specified"
        )
        test_db.add(translation)
        test_db.commit()
        
        saved_translation = test_db.query(Translation).filter(
            Translation.key == "no.category"
        ).first()
        
        assert saved_translation.category == "general"
    
    def test_translation_timestamps(self, test_db):
        """Test automatic timestamp handling."""
        before_create = datetime.utcnow()
        
        translation = Translation(
            key="timestamp.test",
            language_code="en",
            value="Timestamp test",
            category="test"
        )
        test_db.add(translation)
        test_db.commit()
        
        after_create = datetime.utcnow()
        
        # Verify created_at is set
        assert translation.created_at is not None
        assert before_create <= translation.created_at <= after_create
        
        # Verify updated_at is set
        assert translation.updated_at is not None
        assert translation.created_at == translation.updated_at
        
        # Test update timestamp
        original_updated_at = translation.updated_at
        translation.value = "Updated value"
        test_db.commit()
        
        # Verify updated_at changed
        assert translation.updated_at > original_updated_at
    
    def test_translation_repr(self, test_db):
        """Test string representation of Translation."""
        translation = Translation(
            key="repr.test",
            language_code="en",
            value="Representation test",
            category="test"
        )
        test_db.add(translation)
        test_db.commit()
        
        repr_str = repr(translation)
        assert "Translation(" in repr_str
        assert "key='repr.test'" in repr_str
        assert "lang='en'" in repr_str
        assert "category='test'" in repr_str
    
    def test_query_by_language(self, test_db):
        """Test querying translations by language."""
        languages = ["en", "zh", "es", "fr"]
        
        # Create translations for each language
        for lang in languages:
            for i in range(3):
                translation = Translation(
                    key=f"lang.test_{i}",
                    language_code=lang,
                    value=f"Value {i} in {lang}",
                    category="test"
                )
                test_db.add(translation)
        
        test_db.commit()
        
        # Test language-specific queries
        for lang in languages:
            lang_translations = test_db.query(Translation).filter(
                Translation.language_code == lang
            ).all()
            assert len(lang_translations) == 3
            
            for translation in lang_translations:
                assert translation.language_code == lang
                assert f"in {lang}" in translation.value
    
    def test_bulk_translation_operations(self, test_db):
        """Test bulk operations on translations."""
        # Create multiple translations
        translations = []
        for i in range(10):
            translation = Translation(
                key=f"bulk.test_{i}",
                language_code="en",
                value=f"Bulk test value {i}",
                category="bulk"
            )
            translations.append(translation)
        
        test_db.add_all(translations)
        test_db.commit()
        
        # Verify all were created
        bulk_translations = test_db.query(Translation).filter(
            Translation.category == "bulk"
        ).all()
        assert len(bulk_translations) == 10
        
        # Test bulk update
        test_db.query(Translation).filter(
            Translation.category == "bulk"
        ).update({"category": "updated_bulk"})
        test_db.commit()
        
        # Verify update
        updated_translations = test_db.query(Translation).filter(
            Translation.category == "updated_bulk"
        ).all()
        assert len(updated_translations) == 10
        
        # Test bulk delete
        test_db.query(Translation).filter(
            Translation.category == "updated_bulk"
        ).delete()
        test_db.commit()
        
        # Verify deletion
        remaining_translations = test_db.query(Translation).filter(
            Translation.category == "updated_bulk"
        ).all()
        assert len(remaining_translations) == 0