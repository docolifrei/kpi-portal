import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

app = FastAPI(title="Docplanner KPI Backend")

# Enable CORS so your HTML frontend can communicate with this Render server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from local HTML files or web hosts
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Read the Google Client ID from Render Environment Variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
REQUIRED_DOMAIN = "docplanner.com"

@app.get("/")
def home():
    """Health check endpoint to verify server status."""
    return {"status": "Docplanner KPI Backend is Live!"}

@app.post("/api/verify")
def verify_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifies that the user logged in with a valid @docplanner.com email."""
    try:
        token = credentials.credentials
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        # Enforce @docplanner.com hosted domain requirement
        if id_info.get("hd") != REQUIRED_DOMAIN:
            raise HTTPException(
                status_code=403, 
                detail="Access denied: Must use a valid @docplanner.com email."
            )
        
        return {
            "status": "authorized",
            "email": id_info.get("email"),
            "name": id_info.get("name")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
