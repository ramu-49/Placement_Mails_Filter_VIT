"""
Step 6 test script: fetches your real recent emails and runs them
through the classifier to see which ones get flagged as important.

This is a checkpoint script - once we add the AI double-check (Phase 3)
and WhatsApp alerts (Phase 4), this logic will move into main.py.
"""

from email_checker import connect_to_inbox, get_recent_emails
from classifier import classify_email

NUM_EMAILS_TO_CHECK = 15


def run():
    mail = connect_to_inbox()
    emails = get_recent_emails(mail, NUM_EMAILS_TO_CHECK)
    mail.logout()

    print(f"\nChecked {len(emails)} recent emails.\n")
    print("=" * 70)

    important_count = 0
    for e in emails:
        result = classify_email(e["from"], e["subject"])
        status = "IMPORTANT" if result["important"] else "skip"

        print(f"[{status}] {e['subject']}")
        print(f"    From: {e['from']}")
        if result["important"]:
            print(f"    Reason: {result['reason']}")
            important_count += 1
        print("-" * 70)

    print(f"\n{important_count} out of {len(emails)} emails flagged as important.")


if __name__ == "__main__":
    run()