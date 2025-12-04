from fastapi import APIRouter
import os
from fastapi import HTTPException
from app.utils.oauth_utils import get_auth_flow

router = APIRouter(prefix="/auth", tags=["Auth"])

# Path to credentials file relative to this file
CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "gmail_credentials.json"
)

@router.get("/login")
def login():
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return {"auth_url": auth_url}

@router.get("/callback")
def callback(code: str):
    flow = get_auth_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Temporarily save creds to local file
    with open("gmail_credentials.json", "w") as f:
        f.write(credentials.to_json())

    return {"message": "Gmail connected successfully!"}

# ---------------------------
# Check if Gmail is connected
# ---------------------------
@router.get("/status")
def status():
    """
    Returns whether the user is logged in (gmail_credentials.json exists in backend folder)
    """
    logged_in = os.path.exists(CREDENTIALS_PATH)
    return {"logged_in": logged_in}


@router.get("/logout")
def logout():
    """
    Deletes gmail_credentials.json to log the user out
    """
    if os.path.exists(CREDENTIALS_PATH):
        os.remove(CREDENTIALS_PATH)
        return {"message": "Logged out successfully"}
    else:
        raise HTTPException(status_code=400, detail="No user logged in")