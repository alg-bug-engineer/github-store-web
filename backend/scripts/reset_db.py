import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the project root to the sys.path to allow imports from app
# Assumes script is in backend/scripts/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.db.base import Base # Base from where all models are inherited
from app.db.session import engine

def reset_database():
    """
    Drops all tables from the database, including the Alembic version table.
    """
    print("This script will drop all tables from the database.")
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    print("Dropping all tables...")
    try:
        with engine.connect() as connection:
            with connection.begin():
                print("Dropping alembic_version table...")
                connection.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        
        print("Dropping all other tables...")
        Base.metadata.drop_all(bind=engine)
        
        print("All tables dropped successfully.")
        print("To recreate the database schema, run the following command in the 'backend' directory:")
        print("alembic upgrade head")
    except Exception as e:
        print(f"An error occurred while dropping tables: {e}")

if __name__ == "__main__":
    reset_database()
