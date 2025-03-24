import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
DEFAULT_LINK_EXPIRY_DAYS = os.getenv('DEFAULT_LINK_EXPIRY_DAYS')

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#DATABASE_URL = "postgresql://url_admin:245hw8A@62.217.177.132:5432/url_project"
# DATABASE_URL = URL.create(
#     "postgresql",
#     username=DB_USER,
#     password=DB_PASS,
#     host=DB_HOST,
#     port=DB_PORT,
#     database=DB_NAME
# )

