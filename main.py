import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

app = FastAPI()
security = HTTPBearer()

# Pulls secrets safely from the cloud environment
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
REQUIRED_DOMAIN = "docplanner.com"

@app.get("/")
def home():
    return {"status": "Docplanner KPI Backend is Live!"}

@app.post("/api/verify")
def verify_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifies that the user logged in with an @docplanner.com email."""
    try:
        token = credentials.credentials
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        if id_info.get("hd") != REQUIRED_DOMAIN:
            raise HTTPException(status_code=403, detail="Access restricted to @docplanner.com")
        
        return {"status": "authorized", "email": id_info.get("email")}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")