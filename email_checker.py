"""
Phase 1: Connect to Gmail via IMAP and fetch recent emails.

This is just a connection test. It logs in, grabs the most recent
emails from your inbox, and prints their sender/subject/date so you
can confirm everything is wired up correctly before we add filtering
and WhatsApp alerts on top.
"""

import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from your .env file

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

NUM_EMAILS_TO_FETCH = 10  # how many recent emails to pull for this test


def decode_mime_words(s):
    """Gmail sometimes encodes subject lines (e.g. for non-ASCII text).
    This decodes them into normal readable strings."""
    if not s:
        return ""
    decoded_parts = decode_header(s)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result


def connect_to_inbox():
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise ValueError(
            "Missing EMAIL_ADDRESS or EMAIL_APP_PASSWORD. "
            "Make sure you created a .env file (copy .env.example -> .env "
            "and fill in your real values)."
        )

    print(f"Connecting to {IMAP_HOST} as {EMAIL_ADDRESS} ...")
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
    print("Connected successfully.\n")
    return mail


def get_recent_emails(mail, num_emails=NUM_EMAILS_TO_FETCH):
    """Returns a list of dicts: [{"from": ..., "subject": ..., "date": ...}, ...]
    Newest email first. This is the reusable version other scripts import."""
    mail.select("inbox")

    status, message_ids = mail.search(None, "ALL")
    if status != "OK":
        return []

    id_list = message_ids[0].split()
    recent_ids = id_list[-num_emails:]

    results = []
    for eid in reversed(recent_ids):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        results.append({
            "message_id": msg.get("Message-ID", f"no-id-{eid.decode()}"),
            "from": decode_mime_words(msg.get("From")),
            "subject": decode_mime_words(msg.get("Subject")),
            "date": msg.get("Date"),
        })

    return results


def fetch_recent_emails(mail, num_emails=NUM_EMAILS_TO_FETCH):
    """Prints recent emails to the console (used when running this file directly)."""
    emails = get_recent_emails(mail, num_emails)
    print(f"Fetching the {len(emails)} most recent emails:\n")
    print("-" * 70)
    for e in emails:
        print(f"From:    {e['from']}")
        print(f"Subject: {e['subject']}")
        print(f"Date:    {e['date']}")
        print("-" * 70)


if __name__ == "__main__":
    mailbox = connect_to_inbox()
    fetch_recent_emails(mailbox)
    mailbox.logout()
    print("\nDone. Connection test complete.")