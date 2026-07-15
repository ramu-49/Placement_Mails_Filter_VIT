"""
Phase 2: Decide which emails are placement-relevant.

Two rules, checked in order:
1. TRUSTED SENDERS - emails from known placement/CDC addresses are
   always considered important, regardless of subject wording.
2. KEYWORDS - for everyone else, we scan the subject line for
   placement-related words as a backup net.

This module doesn't fetch email itself - it takes email info that
email_checker.py already retrieved and just classifies it.
"""

# Add any other official placement-related sender addresses here as you spot them
TRUSTED_SENDERS = [
    "students.cdc2027@vitap.ac.in",
    "cdc",  # matches any address containing "cdc" as a safety net
]

# Keywords checked against the subject line (case-insensitive)
PLACEMENT_KEYWORDS = [
    "placement", "internship", "intern", "recruitment", "recruiter",
    "hiring", "drive", "shortlist", "shortlisted", "selection",
    "selected", "interview", "ppo", "dream company", "dream internship",
    "super dream", "offer letter", "job opening", "campus drive",
    "walk-in", "pool campus",
]

# If any of these appear in the subject, we do NOT treat it as placement-related
# even if a keyword above also matched - these are common false-positive sources
# (exam/academic admin emails that happen to share words like "registration").
EXCLUDE_KEYWORDS = [
    "arrear", "examination", "re-examination", "fat ", "hall ticket",
    "hostel", "mess", "fee due", "attendance", "cgpa", "backlog",
]


def is_trusted_sender(from_address: str) -> bool:
    from_lower = from_address.lower()
    return any(trusted in from_lower for trusted in TRUSTED_SENDERS)


def matches_keywords(subject: str) -> bool:
    subject_lower = subject.lower()
    return any(keyword in subject_lower for keyword in PLACEMENT_KEYWORDS)


def matches_exclusions(subject: str) -> bool:
    subject_lower = subject.lower()
    return any(keyword in subject_lower for keyword in EXCLUDE_KEYWORDS)


def classify_email(from_address: str, subject: str) -> dict:
    """
    Returns a dict describing whether this email looks placement-relevant
    and why, so later steps (AI double-check, WhatsApp alert) know how
    to handle it.
    """
    if is_trusted_sender(from_address):
        return {
            "important": True,
            "reason": "trusted_sender",
            "needs_ai_check": False,  # we already trust this fully
        }

    if matches_keywords(subject) and not matches_exclusions(subject):
        return {
            "important": True,
            "reason": "keyword_match",
            "needs_ai_check": True,  # let AI confirm since sender isn't trusted
        }

    return {
        "important": False,
        "reason": "no_match",
        "needs_ai_check": False,
    }


if __name__ == "__main__":
    # Quick manual test using a few examples from your actual inbox
    test_emails = [
        ("students.cdc2027@vitap.ac.in", "Clayfin - Shortlisted list - Reg"),
        ("newsletter@economictimesnews.com", "D-St banks on TACO trade"),
        ("someuser@gmail.com", "Reminder: hostel mess fee due"),
        ("hr@somecompany.com", "You're shortlisted for the next round"),
        ("coe@vitap.ac.in", "Deadline Extended - Registration for Regular Arrear Examinations"),
    ]

    for sender, subj in test_emails:
        result = classify_email(sender, subj)
        print(f"From: {sender}")
        print(f"Subject: {subj}")
        print(f"Result: {result}\n")