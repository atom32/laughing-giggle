# Park Tycoon Game

A browser-based resource management and creature collection game built with FastAPI and PostgreSQL.

## Project Structure

```
park-tycoon-game/
├── app/
│   ├── api/                    # API routes and endpoints
│   ├── core/                   # Core application components
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database setup and connection
│   │   └── logging.py         # Logging configuration
│   └── models/                 # Database models
│       ├── user.py            # User authentication model
│       ├── player.py          # Player/character model
│       ├── livestock.py       # Livestock/creature model
│       ├── module.py          # Park module models
│       ├── item.py            # Items and resources model
│       └── translation.py     # I18n translation model
├── alembic/                    # Database migrations
├── scripts/                    # Utility scripts
│   ├── init_db.py             # Database initialization
│   └── start_dev.py           # Development server startup
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic configuration
└── .env.example               # Environment configuration template
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip or poetry for dependency management

### Installation

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and other settings
   ```

5. Create PostgreSQL database:
   ```sql
   CREATE DATABASE park_tycoon;
   ```

6. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

### Running the Application

#### Development Server
```bash
python scripts/start_dev.py
```

Or directly with uvicorn:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### API Documentation
Once running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Database Migrations

Generate a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT token signing key
- `ENVIRONMENT`: development/production/testing
- `LOG_LEVEL`: Logging verbosity
- `DEFAULT_LANGUAGE`: Default UI language (zh/en/es/fr)

See `.env.example` for all available options.

## Architecture

### Core Components

- **FastAPI Application**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM with declarative models
- **Alembic**: Database migration management
- **Pydantic Settings**: Configuration management
- **PostgreSQL**: Primary database with JSONB support

### Key Features

- **Async/Await**: Full async support for database operations
- **Type Safety**: Pydantic models and SQLAlchemy 2.0 typing
- **Internationalization**: Multi-language support with database-stored translations
- **Modular Design**: Extensible module system for game features
- **UUID Support**: Unique identification for game entities

## Development

### Code Organization

- Models use SQLAlchemy 2.0 declarative syntax with proper typing
- Configuration is centralized using Pydantic Settings
- Database operations are fully async
- Logging is configured for development and production environments

### Next Steps

This foundation supports the implementation of:
- Authentication system (JWT-based)
- Game logic and turn management
- Module system (Market, Farm, Restaurant, etc.)
- Livestock management and processing
- Internationalization service layer

## Health Check

Test the API is running:
```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Park Tycoon Game API is running"
}
```