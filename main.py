"""
Main agent: runs continuously, checking your inbox on a timer.

For each check:
1. Fetch recent emails
2. Skip any we've already processed before (tracked in seen_emails.txt)
3. Classify the new ones
4. Send a Telegram alert for anything important
5. Remember we've now seen all of them, so we never alert twice
"""

import time
import html
from datetime import datetime

from email_checker import connect_to_inbox, get_recent_emails
from classifier import classify_email
from notifier import send_telegram_message

CHECK_INTERVAL_SECONDS = 15 * 60  # check every 15 minutes
NUM_EMAILS_TO_CHECK = 20          # how many recent emails to look at each time
SEEN_EMAILS_FILE = "seen_emails.txt"


def load_seen_ids():
    try:
        with open(SEEN_EMAILS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def mark_as_seen(message_id):
    with open(SEEN_EMAILS_FILE, "a", encoding="utf-8") as f:
        f.write(message_id + "\n")


def format_alert(email_info, reason):
    subject = html.escape(email_info["subject"] or "")
    from_ = html.escape(email_info["from"] or "")
    date_ = html.escape(email_info["date"] or "")
    reason_ = html.escape(reason or "")

    return (
        f"📢 <b>New placement update</b>\n\n"
        f"<b>Subject:</b> {subject}\n"
        f"<b>From:</b> {from_}\n"
        f"<b>Date:</b> {date_}\n\n"
        f"<i>Flagged via: {reason_}</i>"
    )


def run_one_check():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking inbox...")

    seen_ids = load_seen_ids()

    mail = connect_to_inbox()
    emails = get_recent_emails(mail, NUM_EMAILS_TO_CHECK)
    mail.logout()

    new_important_count = 0

    for e in emails:
        if e["message_id"] in seen_ids:
            continue  # already processed this one before

        result = classify_email(e["from"], e["subject"])

        if result["important"]:
            alert_text = format_alert(e, result["reason"])
            sent = send_telegram_message(alert_text)
            if sent:
                new_important_count += 1
                print(f"  -> Alert sent: {e['subject']}")
            else:
                print(f"  -> Alert FAILED to send: {e['subject']}")

        mark_as_seen(e["message_id"])

    print(f"  Done. {new_important_count} new alert(s) sent.\n")


def run_forever():
    print("Placement agent started. Press Ctrl+C to stop.\n")
    while True:
        try:
            run_one_check()
        except Exception as e:
            # Don't let one failed check (e.g. a network hiccup) kill the whole agent
            print(f"  Error during check: {e}\n")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_forever()