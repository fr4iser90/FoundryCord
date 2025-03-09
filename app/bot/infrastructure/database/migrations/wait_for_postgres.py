#!/usr/bin/env python3
import asyncio
import os
import sys
import time
from sqlalchemy.ext.asyncio import create_async_engine

async def wait_for_postgres():
    db_host = os.environ.get('POSTGRES_HOST', 'postgres')
    db_port = os.environ.get('POSTGRES_PORT', '5432')
    db_user = os.environ.get('APP_DB_USER', 'app_user')
    db_pass = os.environ.get('APP_DB_PASSWORD', 'app_password')
    db_name = os.environ.get('POSTGRES_DB', 'homelab')
    
    db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_async_engine(db_url)
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with engine.begin() as conn:
                await conn.execute('SELECT 1')
                print('PostgreSQL is ready!')
                return True
        except Exception as e:
            retry_count += 1
            print(f'Waiting for PostgreSQL... ({retry_count}/{max_retries})')
            if retry_count >= max_retries:
                print(f'Could not connect to PostgreSQL: {e}')
                return False
            await asyncio.sleep(2)

if __name__ == "__main__":
    if asyncio.run(wait_for_postgres()) == False:
        sys.exit(1)