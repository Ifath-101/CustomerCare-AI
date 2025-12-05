from fastapi import APIRouter
from app.utils.oauth_utils import get_auth_flow

router = APIRouter(prefix="/auth", tags=["Auth"])

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
