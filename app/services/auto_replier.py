import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.services.email_reader import get_gmail_service


def generate_reply(to_email, subject, body, confidence,
                   original_message_id=None, thread_id=None):

    print("\n----- DEBUG: generate_reply() STARTED -----")

    if confidence <= 0.50:
        print(f"DEBUG: Confidence {confidence} too low, skipping reply.")
        return None

    print("To:", to_email)
    print("Subject:", subject)
    print("Body:", body)

    service = get_gmail_service()

    msg = MIMEText(body)
    msg["to"] = to_email
    msg["subject"] = subject

    if original_message_id:
        msg["In-Reply-To"] = original_message_id
        msg["References"] = original_message_id

    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    send_body = {"raw": raw_msg}

    if thread_id:
        send_body["threadId"] = thread_id

    sent = service.users().messages().send(
        userId="me",
        body=send_body
    ).execute()

    print("DEBUG: Gmail SEND RESULT:", sent)

    if original_message_id:
        try:
            service.users().messages().modify(
                userId="me",
                id=original_message_id,
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print(f"DEBUG: Marked original email {original_message_id} as read.")
        except Exception as e:
            print("DEBUG: Failed to mark email as read:", e)

    return sent


# <<< ADDED NEW FUNCTION
def forward_email(original_message_id, forward_to):
    print("\n----- DEBUG: forward_email() STARTED -----")

    service = get_gmail_service()

    # ---- Fetch original message from Gmail ----
    original_msg = service.users().messages().get(
        userId="me",
        id=original_message_id,
        format="full"
    ).execute()

    print("DEBUG: Original message fetched for forwarding")

    # ---- Extract original email body ----
    try:
        raw_body = original_msg["payload"]["parts"][0]["body"].get("data")
    except:
        raw_body = original_msg["payload"]["body"].get("data")

    original_body = ""

    if raw_body:
        original_body = base64.urlsafe_b64decode(raw_body).decode(errors="ignore")

    # ---- Extract useful headers ----
    headers = original_msg.get("payload", {}).get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    from_email = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

    # =======================================================
    #  CREATE A **NEW EMAIL MESSAGE** TO SEND TO STAFF
    # =======================================================
    forward_msg = MIMEMultipart()
    forward_msg["to"] = forward_to                      # <<< FIXED
    forward_msg["subject"] = f"FWD: {subject}"          # <<< FIXED

    # ---- Construct forwarded content ----
    body_text = f"""
A new customer complaint has been received.

From: {from_email}
Original Subject: {subject}

-------- Customer Complaint --------
{original_body}
------------------------------------

This email was automatically forwarded by the support system.
"""

    forward_msg.attach(MIMEText(body_text, "plain"))

    # ---- Encode and send ----
    raw_forward = base64.urlsafe_b64encode(
        forward_msg.as_bytes()
    ).decode()

    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw_forward}
    ).execute()

    print("DEBUG: Forwarding sent:", sent)

    # ---- Mark original message as READ ----
    try:
        service.users().messages().modify(
            userId="me",
            id=original_message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        print("DEBUG: Marked original complaint email as READ.")
    except Exception as e:
        print("DEBUG: Failed to mark as read:", e)

    return sent