# Placement Agent

An automated system that watches a Gmail inbox for placement/internship-related emails and sends an instant alert via Telegram — so you never miss a shortlist, drive announcement, or interview call buried in a busy inbox.

This project has **two alert paths**, which can be used together or independently:

| Path | Delay | Cost | Complexity |
|---|---|---|---|
| **A. GitHub Actions polling** | Up to 10 minutes | Free | Simple |
| **B. Google Cloud real-time push** | Near-instant (seconds) | Free (low usage) | Moderate |

Path A is the original, simpler system. Path B was added later for true real-time alerts. Path A also acts as Path B's backup — if the Cloud system ever breaks, you're still covered within 10 minutes.

---

## How It Works

1. **Detection** — new email arrives in Gmail.
2. **Classification** (`classifier.py`) — checked against:
   - A trusted senders list (e.g. your college's placement cell address)
   - A keyword scan (e.g. "shortlisted", "interview", "drive") with exclusions for common false positives (e.g. exam/hostel notices)
3. **Alert** (`notifier.py` / Cloud Function) — a Telegram message is sent if the email is flagged important.

---

## Path A: GitHub Actions (Polling)

Runs automatically in the cloud every 10 minutes, checking your inbox via IMAP. No laptop or server needs to stay on.

### Why this is free
GitHub Actions gives every account **2,000 free minutes/month** on private repos (unlimited on public repos). A single inbox check takes a few seconds, so checking every 10 minutes uses only a small fraction of this — this workflow will never come close to the free limit under normal use.

### Setup

1. Fork this repository, then clone your fork:
   ```
   git clone <your-fork-url>
   cd Placement_Agent
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Get a **Gmail App Password**: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2-Step Verification enabled).
5. Create a **Telegram bot** via [@BotFather](https://t.me/BotFather) → `/newbot` → copy the bot token.
6. Get your **Telegram Chat ID**: message your new bot once, then visit:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   and copy the `chat.id` value.
7. In your GitHub fork: **Settings → Secrets and variables → Actions**, add:

   | Secret name | Value |
   |---|---|
   | `EMAIL_ADDRESS` | your Gmail address |
   | `EMAIL_APP_PASSWORD` | your 16-character Gmail App Password |
   | `TELEGRAM_BOT_TOKEN` | your bot token |
   | `TELEGRAM_CHAT_ID` | your chat ID |

8. Go to the **Actions** tab and enable workflows if prompted (disabled by default on forks).

That's it — `.github/workflows/check_inbox.yml` now runs every 10 minutes automatically. Trigger it manually anytime via **Actions → Check Placement Emails → Run workflow**.

> ⚠️ **Note:** GitHub does not guarantee exact cron timing — scheduled runs can be delayed during high platform load. Also, if a repo has zero activity for 60 days, GitHub auto-disables its scheduled workflows until manually re-enabled.

---

## Path B: Google Cloud Real-Time Push

Instead of checking the inbox every 10 minutes, this path uses Gmail's **push notifications** — Gmail tells Google Cloud the *instant* a new email arrives, which triggers an alert within seconds.

### Architecture

```
Gmail inbox (new email)
      │
      ▼
Gmail API "watch" → Pub/Sub Topic (gmail-notifications)
      │
      ▼
Pub/Sub Push Subscription
      │
      ▼
Cloud Run Function (gmail-notification-handler)
      │
      ├─ Fetches new message(s) via History API
      ├─ Runs classify_email() logic
      └─ Sends Telegram alert if important
```

### Why this stays free (mostly)
Cloud Run's free tier includes **2 million requests/month** and generous compute time. This project realistically triggers a handful of times a day — nowhere close to the limit. Google **does** require a billing account and a one-time minimum prepayment (varies by region, e.g. ₹1,000) to activate certain APIs, even for free-tier usage — this acts as identity verification, not a recurring charge. Actual monthly cost for this project's usage is effectively ₹0.

**Cost safety nets set up:**
- Billing budget alert (e.g. ₹100 threshold) — emails you if costs ever approach even a tiny amount
- Post-pay billing threshold (e.g. ₹2,000) — caps how much could ever be charged before you're notified

### One-time setup summary

1. **Google Cloud project** created (`placement-email-alerts`), Gmail API enabled.
2. **OAuth consent screen** configured (External, Testing mode) + Gmail `readonly` scope added.
3. **OAuth credentials** (Desktop app type) downloaded as `credentials.json`; authorized once locally via a Python script to produce `token.json` (contains a long-lived refresh token).
4. **Pub/Sub topic** `gmail-notifications` created; Gmail's system account (`gmail-api-push@system.gserviceaccount.com`) granted **Pub/Sub Publisher** on it.
5. **Cloud Run Function** (`gmail-notification-handler`, Python 3.13, `asia-south1`) deployed with:
   - Entry point: `gmail_push_handler`
   - Environment variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GMAIL_TOKEN_JSON`
   - Authentication required (IAM)
6. **Pub/Sub push subscription** (`gmail-notifications-sub`) created, pointing at the function's URL, authenticated via the project's default service account.
7. Pub/Sub's service account granted **Cloud Run Invoker** on the function (via IAM).
8. Gmail's `watch()` API called once to start publishing inbox changes to the topic.

### The 7-day renewal requirement

Gmail's `watch()` subscription **expires after 7 days** — this is a hard Google limitation, not a bug. If not renewed, notifications silently stop (no error is thrown; alerts just stop arriving).

**This is handled automatically** via a second GitHub Actions workflow (`.github/workflows/renew_watch.yml`) that re-runs `start_watch.py` every Monday, refreshing the subscription indefinitely. Requires a `GMAIL_TOKEN_JSON` secret set in the same GitHub repo (Settings → Secrets and variables → Actions).

You can also trigger this manually anytime via **Actions → Renew Gmail Watch → Run workflow**.

---

## Project Structure

| File | Purpose |
|---|---|
| `main.py` | Runs continuously, checks inbox on a timer (local/manual use, Path A) |
| `run_once.py` | Runs a single check and exits (used by GitHub Actions, Path A) |
| `email_checker.py` | Connects to Gmail via IMAP, fetches recent emails (Path A) |
| `classifier.py` | Decides which emails are placement-relevant (shared logic) |
| `notifier.py` | Sends alerts to Telegram (Path A) |
| `run_filter.py` | Test script — shows which recent emails would be flagged, without alerting |
| `start_watch.py` | Starts/renews the Gmail push notification subscription (Path B) |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for local environment variables |
| `.env` | Real local credentials (never committed) |
| `seen_emails.txt` | Auto-updated log of processed emails (Path A dedup) |
| `.github/workflows/check_inbox.yml` | GitHub Actions — polls inbox every 10 minutes (Path A) |
| `.github/workflows/renew_watch.yml` | GitHub Actions — renews Gmail watch weekly (Path B) |

The Cloud Function's source code (deployed directly via Google Cloud Console) mirrors the logic in `classifier.py` and `notifier.py`, adapted to read credentials from environment variables instead of local files.

---

## Customizing the Filter

The trusted sender list and keyword list are tuned to one college's placement cell (VIT-AP CDC). If you're using this elsewhere:

1. Pull a sample of your own placement/internship emails (subjects + sender addresses).
2. Feed them to an AI model and ask for suggested trusted senders and keywords based on your samples.
3. Open `classifier.py` and update:
   - `TRUSTED_SENDERS` — your placement cell's real email address(es)
   - `PLACEMENT_KEYWORDS` — keywords matching your emails
   - `EXCLUDE_KEYWORDS` — false-positive terms to exclude
4. If using Path B, also update the same three lists inside the Cloud Function's source (Cloud Run → your service → Source tab).

---

## Security Notes

- **Gmail access is read-only** (`gmail.readonly` scope) — this project can never send, delete, or modify anything in your inbox.
- Credentials (`token.json`, App Password, bot token) should never be committed to Git or shared — they're excluded via `.gitignore` locally, and stored as encrypted Secrets on GitHub / environment variables on Cloud Run.
- If any credential is ever accidentally exposed (e.g. pasted somewhere, shared in a screenshot):
  - **Gmail token**: revoke at [myaccount.google.com/permissions](https://myaccount.google.com/permissions), then re-run `authorize.py` for a fresh one.
  - **Telegram bot token**: revoke and regenerate via [@BotFather](https://t.me/BotFather) → `/mybots` → your bot → **API Token** → **Revoke current token**.

---

## Troubleshooting

**Path A (GitHub Actions polling)**
- No emails printed by `email_checker.py`: double-check Gmail address and App Password in `.env`.
- Telegram test message not arriving: make sure you've messaged your bot at least once.
- Workflow not running: confirm Actions are enabled on your fork, and all four secrets are spelled exactly right.

**Path B (Cloud push)**
- No alerts arriving, but no errors either: check Cloud Run → **Observability/Logs** for the timestamp of the email — confirm the function ran, what it classified the email as, and whether Telegram accepted the message.
- Alerts stopped after ~7 days: the Gmail watch likely expired — check the **Actions** tab for `renew_watch.yml`'s run history, or manually run `python start_watch.py` locally.
- `500 Internal Server Error` when testing manually: check Logs for a Python traceback — most often caused by a missing/malformed environment variable.
- Telegram `400 Bad Request: can't parse entities`: sender names/subjects containing `<`, `>`, or `&` must be HTML-escaped before sending (already handled in the current Cloud Function code via `html.escape()`).

---

## Costs Summary

| Component | Typical Monthly Cost |
|---|---|
| GitHub Actions (both workflows) | ₹0 (well within free tier) |
| Gmail API | ₹0 (free) |
| Cloud Pub/Sub | ₹0 (free tier covers this volume) |
| Cloud Run Function | ₹0 (free tier covers this volume) |
| Google Cloud billing account | One-time ₹1,000 prepayment (verification only, not a fee) |

Total ongoing cost for typical personal use: **effectively free**, once the one-time Google Cloud prepayment is made.