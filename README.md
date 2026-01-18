# FilterFox

Local‑only Gmail cleanup tool that **previews** how your inbox would be organized before you **apply** changes. FilterFox classifies emails (newsletters, receipts, social, etc.), creates Gmail labels like `FilterFox/Newsletters`, and—when you choose—moves messages out of Inbox so labels behave like folders.

---

## Features

* Gmail query support (e.g., `newer_than:30d in:inbox`)
* **Preview (Dry Run)** before making any changes
* Auto‑creates labels (e.g., `FilterFox/Newsletters`)
* Optional “folder‑like” behavior (label + remove `INBOX`)
* OAuth with Google (local only)
* Rule‑based classification engine

---

## Project Structure

```
FilterFox/
├─ filterfox/
│  ├─ __init__.py
│  ├─ webapp.py          # Flask app
│  ├─ engine.py          # Core logic
│  ├─ gmail_client.py    # Gmail API wrapper
│  ├─ actions.py         # Apply label/archive actions
│  ├─ rules.py           # Classification rules
│  ├─ config.py          # Defaults & paths
│  └─ templates/
│     ├─ layout.html
│     ├─ index.html
│     └─ results.html
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## Requirements

* Python 3.9+
* Gmail account
* Google Cloud project with Gmail API enabled

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Google OAuth Setup

1. Go to **Google Cloud Console**
2. Create or select a project
3. Enable **Gmail API**
4. Configure **OAuth consent screen** (External, testing mode is fine)
5. Add yourself as a **Test User**
6. Create **OAuth Client ID** → Application type: **Desktop App**
7. Download JSON and rename to:

```
credentials.json
```

Place it in the project root:

```
FilterFox/credentials.json
```

> ⚠️ This file is ignored by Git. Never commit it.

---

## First Run

```bash
python -m filterfox.webapp
```

Open in browser:

```
http://127.0.0.1:5055
```

On first run:

* Browser opens Google sign‑in
* Approve access
* App creates `token.json` automatically

---

## Using FilterFox

### 1. Enter settings

* **Gmail query** (e.g., `newer_than:30d in:inbox`)
* **Max emails** (start small, like 25)
* **Label prefix** (default: `FilterFox`)

### 2. Preview (Dry Run)

Click **Preview (dry run)**:

* No emails are changed
* Shows how messages would be classified
* Labels may be created

### 3. Apply Changes

Click **Apply changes**:

* Labels applied
* Messages removed from Inbox (folder‑like behavior)
* Messages appear under labels like:

  * `FilterFox/Newsletters`
  * `FilterFox/Receipts`

---

## Safety Notes

* Always use **Preview** before Apply
* Start with small batches (25–50 emails)
* Check Gmail labels before large runs

---

## GitHub & Secrets

Never commit:

* `credentials.json`
* `token.json`
* `history.json`
* Any exported email data

Your `.gitignore` already protects these.

---

## Troubleshooting

### “Access blocked” during Google login

Add your email as a **Test User** in OAuth consent screen.

### Gmail API not enabled

Enable **Gmail API** in Google Cloud Console.

### Buttons don’t change color

Clear cache or hard refresh (`Ctrl + F5`).

---

## Future Ideas

* Custom user rules
* Web‑hosted version
* Auto‑unsubscribe suggestions
* Statistics dashboard
* Potential auto-deletion (far future kind of thing)

---

## Disclaimer

FilterFox runs locally and uses your own Google credentials. You are responsible for reviewing results before applying changes. This project is for educational and personal use only at this time.

---

Happy Cleaning!!
