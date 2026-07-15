# Placement Agent 🎓📬

An automated agent that watches your Gmail inbox for placement/internship-related
emails and sends you an instant alert on Telegram — so you never miss a
shortlist, drive announcement, or interview call buried in a busy inbox.

## How it works

1. Logs into your Gmail via IMAP and checks for new emails on a timer.
2. Classifies each new email as "important" or not, using:
   - A trusted senders list (e.g. your college's placement cell address)
   - A keyword scan (e.g. "shortlisted", "interview", "drive") with
     exclusions for common false positives (e.g. exam/hostel notices)
3. Sends a Telegram message for anything flagged important.
4. Remembers what it's already checked, so you're never alerted twice.

It runs automatically in the cloud via GitHub Actions every 10 minutes —
you don't need to keep your laptop or any script running.

## ⚠️ A note if you're not from VIT-AP

The trusted sender list and keyword list in this project were built by
reading through the original author's own VIT-AP inbox, so they're tuned
to how VIT-AP's CDC (Career Development Centre) and recruiters phrase things.

If you go to a different college or company, don't just use these as-is —
your placement cell's email address will be different, and the wording
your recruiters use might differ too.

**What to do instead:**
1. Pull a sample of your own placement/internship emails (subjects + sender
   addresses are enough).
2. Feed them to any AI model (ChatGPT, Claude, etc.) and ask it to suggest
   a list of trusted sender addresses and keywords based on your samples.
3. Open `classifier.py` and update these two lists near the top of the file:
   - `TRUSTED_SENDERS` — add your placement cell's real email address(es)
   - `PLACEMENT_KEYWORDS` — add/remove keywords to match your emails
   - (optional) `EXCLUDE_KEYWORDS` — add any false-positive terms you notice

## Prerequisites

Before you start, make sure you have:

- Python 3.9 or newer installed
- A Gmail account (the one that receives placement emails)
- A Telegram account (free, just the app or web)
- A GitHub account (free)
- 10–15 minutes for one-time setup

---

## Step 1: Get a Gmail App Password

Gmail won't let this script log in with your normal password — you need
a special 16-character "App Password" instead. Here's how to get one:

1. Go to your Google Account: https://myaccount.google.com/
2. In the left sidebar, click **Security**.
3. Under "How you sign in to Google," make sure **2-Step Verification**
   is turned ON. (App Passwords only work if this is enabled — turn it
   on first if it isn't already.)
4. Once 2-Step Verification is on, search for **"App passwords"** in the
   search bar at the top of the Google Account page (or go directly to
   https://myaccount.google.com/apppasswords).
5. Under "App name," type something like `Placement Agent` and click
   **Create**.
6. Google will show you a 16-character password (e.g. `abcd efgh ijkl mnop`).
   **Copy it now** — you won't be able to see it again later.
7. You'll paste this into your `.env` file (local testing) and/or GitHub
   Secrets (for the automated version) in a later step.

> 🔒 This app password only works for this one app and can be revoked
> anytime from the same App Passwords page — it never exposes your
> actual Google account password.

---

## Step 2: Create a Telegram bot

1. Open Telegram (app or web: https://web.telegram.org/) and search for
   **@BotFather** — it's the official bot that creates other bots.
2. Start a chat with BotFather and send the command:
   ```
   /newbot
   ```
3. It will ask you to choose a **name** for your bot (this can be
   anything, e.g. `My Placement Agent`).
4. Then it will ask for a **username** for your bot — this must be
   unique and end in `bot` (e.g. `myplacementagent_bot`).
5. BotFather will reply with a message containing your **bot token** —
   a long string like:
   ```
   123456789:ABCdefGhIJKlmNoPQRstuVwxYZ
   ```
   Copy this — you'll need it later.

## Step 3: Get your Telegram Chat ID

Your bot needs to know *where* to send messages — that's your Chat ID.

1. In Telegram, search for the bot you just created (by the username
   you gave it) and click **Start** (or send it any message, e.g. "hi").
   This step is required — Telegram won't let a bot message you until
   you've messaged it first.
2. Open this URL in your browser, replacing `<YOUR_BOT_TOKEN>` with the
   token from BotFather:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. You'll see a chunk of JSON text. Look for a section like:
   ```json
   "chat":{"id":123456789,"first_name":"Your Name", ...}
   ```
4. That number next to `"id"` is your **Chat ID**. Copy it.

> If you see an empty result (`"result":[]`), it means Step 1 wasn't
> done — go back and message your bot first, then reload the URL.

---

## Step 4: Set up the project locally (recommended, to test before automating)

1. **Fork this repository**, then clone your fork:
   ```bash
   git clone <your-fork-url>
   cd Placement_Agent
   ```

2. **Create a virtual environment** (keeps this project's packages separate
   from other Python projects on your machine):
   ```bash
   python -m venv venv
   ```

3. **Activate it:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create your `.env` file:**
   - Copy the template:
     ```bash
     cp .env.example .env
     ```
     (On Windows, use `copy .env.example .env` instead.)
   - Open `.env` in any text editor and fill in the four values you
     collected in Steps 1–3:
     ```
     EMAIL_ADDRESS=youremail@gmail.com
     EMAIL_APP_PASSWORD=your16charapppassword
     TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVwxYZ
     TELEGRAM_CHAT_ID=123456789
     ```
   - Save the file. **Never share this file or commit it to git** —
     it's already excluded via `.gitignore`.

6. **Test the email connection:**
   ```bash
   python email_checker.py
   ```
   You should see your 10 most recent emails printed to the console.

7. **Test the Telegram connection:**
   ```bash
   python notifier.py
   ```
   You should get a message on Telegram from your bot.

8. **Run the classifier test** (see which of your real emails would
   get flagged, without sending any alerts):
   ```bash
   python run_filter.py
   ```

9. **Run the full agent locally (optional):**
   ```bash
   python main.py
   ```
   It will check your inbox every 15 minutes and alert you on Telegram
   for anything important, for as long as this script keeps running.

---

## Step 5: Running this automatically with GitHub Actions (recommended, free)

This repo includes a GitHub Actions workflow that checks your inbox every
10 minutes automatically, forever, for free — no need to keep your laptop
or any script running.

1. Make sure you've **forked this repository** to your own GitHub account
   (click "Fork" at the top of the repo page, if you haven't already).

2. In **your fork**, go to **Settings → Secrets and variables → Actions**.

3. Click **New repository secret** and add each of these one at a time
   (using the same values from Steps 1–3 above):

   | Secret name           | Value                                  |
   |-----------------------|------------------------------------------|
   | `EMAIL_ADDRESS`       | your Gmail address                       |
   | `EMAIL_APP_PASSWORD`  | your 16-character Gmail App Password     |
   | `TELEGRAM_BOT_TOKEN`  | your bot token from BotFather             |
   | `TELEGRAM_CHAT_ID`    | your Telegram chat ID                    |

4. Go to the **Actions** tab of your fork, and enable workflows if
   prompted (forks have Actions disabled by default for safety).

5. That's it — the workflow will now run automatically every 10 minutes.
   You can also trigger it manually anytime: go to **Actions → Check
   Placement Emails → Run workflow**.

> 🔒 These secrets are encrypted by GitHub and never visible in your code,
> logs, or commit history — not even to you after you save them (you can
> only overwrite them, not view them again).

---

## Project structure

| File                        | Purpose                                                        |
|-----------------------------|------------------------------------------------------------------|
| `main.py`                   | Runs continuously, checks inbox on a timer (for local/manual use) |
| `run_once.py`                | Runs a single check and exits (used by GitHub Actions)           |
| `email_checker.py`          | Connects to Gmail via IMAP, fetches recent emails                |
| `classifier.py`             | Decides which emails are placement-relevant                     |
| `notifier.py`               | Sends alerts to Telegram                                         |
| `run_filter.py`             | Test script — shows which recent emails would be flagged, without sending alerts |
| `requirements.txt`          | Python package dependencies                                      |
| `.env.example`              | Template showing which environment variables you need           |
| `.env`                      | Your real credentials (never committed — see `.gitignore`)      |
| `seen_emails.txt`           | Auto-updated log of already-processed emails, kept in sync by GitHub Actions |
| `.github/workflows/check_inbox.yml` | The GitHub Actions workflow that runs everything automatically |

## Troubleshooting

- **No emails printed by `email_checker.py`:** double-check your Gmail
  address and App Password in `.env` — a regular Gmail password will
  not work.
- **Telegram test message not arriving:** make sure you sent your bot a
  message (e.g. "hi") before running `notifier.py` — bots can't message
  you first.
- **GitHub Actions workflow not running:** confirm Actions are enabled
  for your fork (Step 5.4) and that all four secrets are spelled exactly
  as shown in the table above.
- **Nothing gets flagged as important:** run `python classifier.py`
  directly — it includes sample test cases to sanity-check your keyword
  list is working as expected.