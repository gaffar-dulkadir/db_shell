import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from datalayer.database import get_postgres_session
from sqlalchemy import text

async def check_schema():
    session_gen = get_postgres_session()
    session = await anext(session_gen)
    try:
        result = await session.execute(text('''
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'chats' AND table_name = 'message'
            ORDER BY ordinal_position;
        '''))
        
        print('Actual database columns in chats.message:')
        print('Column Name | Data Type | Nullable')
        print('-' * 40)
        for row in result:
            print(f'{row.column_name} | {row.data_type} | {row.is_nullable}')
    finally:
        await session.close()

asyncio.run(check_schema())