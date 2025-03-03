import asyncio
from core.database.config import initialize_engine

async def test_connection():
    try:
        engine = await initialize_engine()
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if not success:
        exit(1)
