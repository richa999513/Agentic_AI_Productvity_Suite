"""Database setup and initialization script."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.database import Base
from src.memory.memory_bank import memory_bank
from config.logging_config import logger


def init_database():
    """Initialize database schema."""
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        Base.metadata.create_all(memory_bank.engine)
        
        logger.info("Database tables created successfully!")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(memory_bank.engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Created tables: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


def seed_sample_data():
    """Seed database with sample data for testing."""
    try:
        logger.info("Seeding sample data...")

        # Create or reuse a test user (idempotent)
        existing = memory_bank.get_user_by_email("test@example.com")
        if existing:
            user = existing
            logger.info(f"Using existing test user: {user.user_id}")
        else:
            user = memory_bank.create_user(
                name="Test User",
                email="test@example.com",
                timezone="UTC",
                preferences={
                    "theme": "light",
                    "notifications": True
                }
            )
            logger.info(f"Created test user: {user.user_id}")
        
        # Create sample tasks
        from src.models.schemas import TaskPriority
        from datetime import datetime, timedelta
        
        tasks = [
            {
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "priority": TaskPriority.HIGH,
                "due_date": datetime.utcnow() + timedelta(days=3)
            },
            {
                "title": "Review code changes",
                "description": "Review pull requests from team",
                "priority": TaskPriority.MEDIUM,
                "due_date": datetime.utcnow() + timedelta(days=1)
            },
            {
                "title": "Update dependencies",
                "description": "Update all project dependencies to latest versions",
                "priority": TaskPriority.LOW,
                "due_date": datetime.utcnow() + timedelta(days=7)
            }
        ]
        
        for task_data in tasks:
            task = memory_bank.create_task(user_id=user.user_id, **task_data)
            logger.info(f"  Created task: {task.title}")
        
        logger.info(f"Created {len(tasks)} sample tasks")

        print("\n" + "="*50)
        print("Database setup complete!")
        print("="*50)
        print(f"\nTest User ID: {user.user_id}")
        print(f"Test User Email: {user.email}")
        print("\nYou can use this user ID to test the API.")
        print("="*50 + "\n")
        
        return user.user_id
        
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        return None


def main():
    """Main setup function."""
    print("\n" + "="*50)
    print("AI Productivity Suite - Database Setup")
    print("="*50 + "\n")
    
    # Initialize database
    if not init_database():
        print("\n❌ Database initialization failed!")
        sys.exit(1)
    
    # Ask if user wants sample data
    response = input("\nDo you want to seed sample data? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        user_id = seed_sample_data()
        if user_id:
            # Save user ID to a file for easy access
            with open('.user_id', 'w') as f:
                f.write(user_id)
            print(f"\nUser ID saved to .user_id file")
    
    print("\nSetup complete! You can now start the application.\n")


if __name__ == "__main__":
    main()