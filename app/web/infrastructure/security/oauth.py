from fastapi.security import OAuth2PasswordBearer

# Nur das OAuth2 Schema für FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)