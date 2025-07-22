# Design Document: Park Tycoon Game

## Overview

Park Tycoon is a browser-based resource management and creature collection game built with a modular, extensible architecture. The system uses FastAPI for the backend with a layered architecture approach, supporting internationalization and future expansion through a flexible data-driven design.

## Architecture

### System Architecture
The application follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
│    (Initial: Web Forms, Future: Vue.js) │
├─────────────────────────────────────────┤
│              API Layer                  │
│           (FastAPI Routes)              │
├─────────────────────────────────────────┤
│            Service Layer                │
│         (Business Logic)                │
├─────────────────────────────────────────┤
│           Game Kernel                   │
│         (Core Game Logic)               │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│            (ORM/Models)                 │
├─────────────────────────────────────────┤
│            Database                     │
│          (PostgreSQL)                   │
└─────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Initial HTML/CSS/JavaScript, future Vue.js 3
- **Authentication**: FastAPI security with JWT tokens
- **Internationalization**: Custom i18n module with database-stored translations

## Components and Interfaces

### 1. Authentication System
**Purpose**: Handle user registration, login, logout, and session management

**Key Components**:
- `AuthService`: Handles password hashing, token generation, user validation
- `UserModel`: Database model for user accounts
- `AuthRoutes`: API endpoints for authentication operations

**Interfaces**:
```python
class AuthService:
    def register_user(username: str, password: str) -> User
    def authenticate_user(username: str, password: str) -> Optional[User]
    def create_access_token(user_id: int) -> str
    def verify_token(token: str) -> Optional[User]
```

### 2. Game Kernel (Core Logic)
**Purpose**: Centralized game logic abstracted from API layer

**Key Components**:
- `TurnManager`: Handles turn progression and time-based events
- `EconomicSystem`: Manages money, income, and transactions
- `LivestockManager`: Core livestock operations and calculations
- `ModuleManager`: Park module logic and upgrades

**Interfaces**:
```python
class GameKernel:
    def advance_turn(player_id: int) -> TurnResult
    def calculate_income(player_id: int) -> int
    def process_livestock(livestock_id: UUID, method: str) -> List[Item]
    def upgrade_module(player_id: int, module_type: str) -> bool
    def generate_livestock(market_level: int) -> Livestock
```

### 3. Module System
**Purpose**: Extensible park module management with upgrade mechanics

**Module Types**:
- **Market**: Livestock purchasing and stock management
- **Farm**: Main livestock storage and management
- **Slaughterhouse**: Livestock processing to meat items
- **Restaurant**: Cooking and selling dishes
- **Photo Studio**: Passive income generation
- **Dungeon**: Alternative income generation
- **Private Residence**: Livestock interaction and affection

**Module Interface**:
```python
class ModuleBase:
    def get_level_effects(level: int) -> Dict[str, Any]
    def get_upgrade_cost(current_level: int) -> int
    def process_turn_events(player_id: int) -> List[Event]
```

### 4. Livestock System
**Purpose**: Comprehensive creature management with extensible attributes

**Core Features**:
- Unique instance generation with randomized attributes
- Flexible attribute system supporting future expansion
- Location tracking across modules
- Relationship and breeding support
- Quality and value calculations

### 5. Internationalization Module
**Purpose**: Multi-language support with externalized strings

**Components**:
- `I18nService`: Translation key resolution and language management
- `TranslationModel`: Database storage for translation strings
- `LanguageMiddleware`: Request-level language detection

## Data Models

### User and Player Models
```python
class User(BaseModel):
    id: int
    username: str
    password_hash: str
    is_admin: bool
    created_at: datetime

class Player(BaseModel):
    id: int
    user_id: int  # Foreign key
    first_name: str
    last_name: str
    birth_month: int
    family_background: str
    childhood_experience: str
    education_background: str
    starting_city: str
    money: int
    current_turn: int
    created_at: datetime
```

### Livestock Model
```python
class Livestock(BaseModel):
    id: UUID
    name_i18n_key: str
    family_i18n_key: str
    nation_i18n_key: str
    city_i18n_key: str
    pic_url: str
    age: int
    father_id: Optional[UUID]
    mother_id: Optional[UUID]
    bloodtype_i18n_key: str
    zodiac_i18n_key: str
    origin_i18n_key: str
    rank_i18n_key: str
    acquire_turn: int
    quality: float
    height: float
    weight: float
    # ... additional attributes as specified
    current_location_module_id: UUID
    custom_data: dict  # JSONB field for extensibility
    owner_id: int  # Foreign key to Player
```

### Module and Item Models
```python
class PlayerModule(BaseModel):
    id: int
    player_id: int
    module_type: str
    level: int
    last_updated: datetime

class Item(BaseModel):
    id: UUID
    owner_id: int
    item_type: str
    name_i18n_key: str
    quantity: int
    quality: float
    created_from_livestock_id: Optional[UUID]
    custom_data: dict
```

### Translation Model
```python
class Translation(BaseModel):
    id: int
    key: str
    language_code: str
    value: str
    category: str  # e.g., 'livestock', 'ui', 'items'
```

## Error Handling

### Error Categories
1. **Authentication Errors**: Invalid credentials, expired tokens
2. **Validation Errors**: Invalid input data, constraint violations
3. **Business Logic Errors**: Insufficient resources, invalid operations
4. **System Errors**: Database connectivity, external service failures

### Error Response Format
```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[dict]
    timestamp: datetime
```

### Error Handling Strategy
- **API Layer**: HTTP status codes with structured error responses
- **Service Layer**: Custom exceptions with error codes
- **Database Layer**: Transaction rollback on failures
- **Frontend**: User-friendly error messages with i18n support

## Testing Strategy

### Unit Testing
- **Models**: Data validation, relationships, and constraints
- **Services**: Business logic, calculations, and state changes
- **Game Kernel**: Turn progression, income calculation, livestock generation
- **I18n Module**: Translation resolution and language switching

### Integration Testing
- **API Endpoints**: Full request/response cycles with authentication
- **Database Operations**: Complex queries and transaction handling
- **Module Interactions**: Cross-module livestock transfers and processing
- **Turn Progression**: End-to-end turn advancement with all side effects

### Test Data Management
- **Fixtures**: Predefined test users, livestock, and game states
- **Factories**: Dynamic test data generation for various scenarios
- **Database Seeding**: Consistent test environment setup
- **Cleanup**: Automated test data cleanup between test runs

### Performance Testing
- **Load Testing**: Multiple concurrent users and turn processing
- **Database Performance**: Query optimization and indexing validation
- **Memory Usage**: Livestock generation and large dataset handling
- **Response Times**: API endpoint performance under load

## Security Considerations

### Authentication Security
- Password hashing using bcrypt with salt
- JWT tokens with expiration and refresh mechanism
- Session management with secure token storage
- Rate limiting on authentication endpoints

### Data Protection
- Input validation and sanitization
- SQL injection prevention through ORM
- XSS protection in frontend rendering
- CSRF protection for state-changing operations

### Authorization
- Role-based access control (regular user vs admin)
- Resource ownership validation
- Module access permissions
- Admin function restrictions

## Scalability and Performance

### Database Optimization
- Indexing on frequently queried fields (user_id, livestock owner, turn numbers)
- Partitioning for large livestock and transaction tables
- Connection pooling for concurrent access
- Query optimization for complex livestock searches

### Caching Strategy
- Translation caching for i18n strings
- Module configuration caching
- Livestock generation template caching
- Session data caching

### Future Scalability
- Microservice architecture preparation
- Database sharding considerations
- CDN integration for static assets
- Background job processing for turn advancement