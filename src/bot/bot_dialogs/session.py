from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

database_url = 'sqlite+aiosqlite:///src/database/example.sqlite'
engine = create_async_engine(database_url)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
