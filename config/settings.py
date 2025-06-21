import os
from dotenv import load_dotenv

load_dotenv()

# postgresql url
DATABASE_URL = os.getenv("DATABASE_URL")

# keycloak credentials
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

# redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))








'''
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
# Use localhost when FastAPI is running outside Docker
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

# Keycloak configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "user-info-realm")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "user-info-client")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")  # Must be set manually

# Optional: Token endpoint URL construction
# TOKEN_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"

'''



