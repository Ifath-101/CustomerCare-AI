from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import email
from email import policy
from bs4 import BeautifulSoup
import re


def get_gmail_service():
    creds = Credentials.from_authorized_user_file("gmail_credentials.json")
    return build("gmail", "v1", credentials=creds)


def extract_clean_text(parsed_email):
    """Extract usable text from multipart or HTML emails."""
    if parsed_email.is_multipart():
        for part in parsed_email.walk():
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)

            if payload is None:
                continue

            decoded = payload.decode("utf-8", errors="ignore")

            if content_type == "text/plain":
                return decoded.strip()

            if content_type == "text/html":
                return BeautifulSoup(decoded, "html.parser").get_text(separator="\n").strip()

    else:
        payload = parsed_email.get_payload(decode=True)
        if payload:
            decoded = payload.decode("utf-8", errors="ignore")

            if parsed_email.get_content_type() == "text/html":
                return BeautifulSoup(decoded, "html.parser").get_text(separator="\n").strip()

            return decoded.strip()
    return ""


def clean_email_body(text: str):
    """Removes quoted replies + signatures + forwarded blocks."""
    print("DEBUG: Cleaning email body...")

    # Remove "On Mon, XXX wrote:"
    text = re.split(r"On\s.*wrote:", text)[0]

    # Remove multiple empty lines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # Remove typical signatures
    text = re.sub(r"(?i)(thanks|regards|best regards|sent from my).*", "", text).strip()

    print("DEBUG: Cleaned customer message:", text[:200], "...")
    return text


def read_latest_unread_email():
    print("----- DEBUG: Checking unread emails -----")

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=1
    ).execute()

    messages = results.get("messages", [])
    print("DEBUG: Unread messages list:", messages)

    if not messages:
        print("DEBUG: No unread messages found.")
        return None

    latest_id = messages[0]["id"]
    print("DEBUG: Latest unread email ID:", latest_id)

    msg = service.users().messages().get(
        userId="me",
        id=latest_id,
        format="raw"
    ).execute()

    raw = base64.urlsafe_b64decode(msg["raw"])
    parsed = email.message_from_bytes(raw, policy=policy.default)

    extracted = extract_clean_text(parsed)
    print("DEBUG: Extracted clean body (raw):", extracted[:200], "...")

    cleaned_body = clean_email_body(extracted)

    result = {
        "id": latest_id,
        "from": parsed["From"],
        "subject": parsed["Subject"],
        "body": cleaned_body   # 👈 Use cleaned message now
    }

    print("DEBUG: Final parsed + cleaned email:", result)
    return result
