import os 
from dotenv import load_dotenv

load_dotenv()

class Settings :
    APP_NAME : str = os.getenv("APP_NAME", "Chores Tracking App")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    SECRET_KEY : str = os.getenv("SECRET_KEY")
    ALGORITHM : str = os.getenv("ALGORITHM","HS256")
    ACCESS_TOKEN_EXPIRE_HOURS : int =int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 2))
    DATABASE_URL : str = os.getenv("DATABASE_URL", "sqlite:///.choresTracker.db")
         

settings = Settings()