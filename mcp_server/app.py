import json
import os
from mcp.server.fastmcp import FastMCP

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "emails.json")

# ---------------------------
# MCP Server instance
# ---------------------------
mcp = FastMCP("EmailAssistant")


def _load_emails() -> list:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading emails: {e}")
        return []


@mcp.tool()
def fetch_emails(query: str = "") -> str:
    """Fetch recent emails from the inbox. Returns a JSON string of emails.
    Use this first before any other email operation.
    """
    emails = _load_emails()
    return json.dumps(emails, indent=2)


@mcp.tool()
def summarize_emails(emails_data: str = "") -> str:
    """Summarize a list of emails.
    Pass a JSON string of emails retrieved from fetch_emails,
    or leave empty to summarize all latest emails.
    """
    if emails_data:
        try:
            emails = json.loads(emails_data) if isinstance(emails_data, str) else emails_data
        except Exception:
            return "Error: Could not parse emails data. Please provide a valid JSON string of emails."
    else:
        emails = _load_emails()

    if not emails:
        return "No emails to summarize."

    lines = [
        f"- Email {e.get('id')} from {e.get('from')}: {e.get('subject')}"
        for e in emails
    ]
    return "Summary of emails:\n" + "\n".join(lines)


@mcp.tool()
def classify_email(email_data: str) -> str:
    """Classify a single email into a category.
    Pass a JSON string of a single email object from fetch_emails.
    Returns one of: Job/Career, Meeting/Calendar, Promotion/Spam, General/Other.
    """
    try:
        email = json.loads(email_data) if isinstance(email_data, str) else email_data
    except Exception:
        return "Error: Could not parse email data. Please provide a valid JSON string."

    subject = str(email.get("subject", "")).lower()
    body = str(email.get("body", "")).lower()

    if any(kw in subject for kw in ("job", "interview", "opportunity")):
        category = "Job/Career"
    elif any(kw in subject or kw in body for kw in ("meeting", "reminder", "zoom")):
        category = "Meeting/Calendar"
    elif any(kw in subject for kw in ("sale", "promo", "flash")):
        category = "Promotion/Spam"
    else:
        category = "General/Other"

    return f"Email {email.get('id')} Classification: {category}"


@mcp.tool()
def send_reply(email_id: str, reply_body: str) -> str:
    """Send a reply to a specific email."""
    emails = _load_emails()
    found = any(str(e.get("id")) == str(email_id) for e in emails)

    if not found:
        return f"Error: Email with ID {email_id} not found."

    # Save to sent_replies.json
    sent_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sent_replies.json")
    try:
        with open(sent_file, "r") as f:
            sent = json.load(f)
    except Exception:
        sent = []

    sent.append({
        "to_email_id": email_id,
        "reply": reply_body,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    })

    with open(sent_file, "w") as f:
        json.dump(sent, f, indent=2)

    return f"Success! Reply sent to email ID {email_id}.\nReply:\n{reply_body}"


if __name__ == "__main__":
    mcp.run()
