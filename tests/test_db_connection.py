from sqlalchemy import create_engine, text

def test_connection():
    database_url = "postgresql://jonas:password123@localhost:5432/fastapi_db"
    
    print("Testing connection with jonas user...")
    print(f"URL: {database_url}")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL version: {version[0]}")
            
            # Get current user and database
            result = conn.execute(text("SELECT current_user, current_database();"))
            user_info = result.fetchone()
            print(f"👤 User: {user_info[0]}, Database: {user_info[1]}")
            return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
