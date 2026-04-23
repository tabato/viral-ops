# Setup Guide

Everything you need to go from zero to your first viral-ops run.

---

## 1. Prerequisites

**Python 3.11+** is required. Check what you have:

```bash
python3.11 --version
```

If you get `command not found`, install it via Homebrew:

```bash
brew install python@3.11
```

Don't have Homebrew? Install it at [brew.sh](https://brew.sh).

---

## 2. Clone and install

```bash
git clone https://github.com/tabato/viral-ops.git
cd viral-ops
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 3. Configure your profile

```bash
cp templates/profile.example.yml profile.yml
cp templates/creators.example.yml creators.yml
cp templates/.env.example .env
```

Open `profile.yml` and fill in your niche, target audience, and content style. The more specific, the sharper the AI copy angles.

Open `creators.yml` and replace the example channels with the YouTube creators in your space.

---

## 4. Get your Gemini API key (FREE — no card required)

Gemini is the default AI provider. Free tier is more than enough for viral-ops.

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy the key
5. Open `.env` and set:
   ```
   GEMINI_API_KEY=your_key_here
   ```

That's it. No billing, no credit card, no quota worries.

---

## 5. Get your YouTube Data API key

The YouTube API is also free — 10,000 quota units/day, and a viral-ops run uses ~60–80.

**Step 1 — Create a Google Cloud project**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project selector at the top → **New Project**
3. When prompted for Organization, select **No organization**
4. Name it anything (e.g. `viral-ops`) and click **Create**

**Step 2 — Enable the YouTube API**

1. Go to **APIs & Services → Library**
2. Search for **YouTube Data API v3**
3. Click it → click **Enable**

**Step 3 — Create an API key**

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → API key**
3. When asked what data you'll access, select **Public data**
4. Copy the key
5. Open `.env` and set:
   ```
   YOUTUBE_API_KEY=your_key_here
   ```

> **Tip:** If you see a message about org security policies blocking API keys, it's because the project is under a managed organization. Hit **New Project** and make sure **No organization** is selected before creating it.

---

## 6. Run it

```bash
source .venv/bin/activate
viral-ops
```

The gallery opens automatically when the run completes. Your swipe file is saved to `swipe_file.md`.

---

## Troubleshooting

**`python3.11: command not found`** — install Python 3.11 via `brew install python@3.11`

**`viral-ops: command not found`** — run `source .venv/bin/activate` first

**`YOUTUBE_API_KEY not set`** — make sure your `.env` file is in the project root and has the real key, not the placeholder

**`Could not find channel: @handle`** — double-check the handle matches exactly what's on YouTube (visit the channel and copy from the URL)

**`API key not valid`** — make sure you enabled YouTube Data API v3 on the same Google Cloud project you created the key in

**No outliers found** — try lowering `virality_threshold` in `profile.yml` (e.g. `1.5`) or increasing `months_back`
