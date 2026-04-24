# Gemini Setup — FREE ✨ (Recommended)

Gemini is the default AI provider for viral-ops and it's **completely free**.

No billing required. No credit card. Just a Google account.

## Free tier limits

| Limit | Amount |
|---|---|
| Requests per minute | 15 |
| Tokens per day | 1,000,000 |
| Cost | $0 |

A full viral-ops run (3 videos analyzed) uses roughly 5,000–8,000 tokens. You have plenty of room.

## Setup

**1. Go to Google AI Studio**

[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

Sign in with your Google account.

**2. Create an API key**

Click **Create API key** → select any Google Cloud project (or let it create one for you) → copy the key.

**3. Add it to your `.env`**

```bash
GEMINI_API_KEY=your_key_here
```

**4. Set it in `profile.yml`**

```yaml
ai_provider: gemini
```

That's it. No billing setup, no credit card.

## Model

viral-ops uses `gemini-2.5-flash` — Google's latest fast model. It's accurate, cheap, and handles the analysis prompts reliably.

## Troubleshooting

**`GEMINI_API_KEY not set`** — your `.env` file is either missing or not in the project root folder. Make sure you ran `cp templates/.env.example .env` and filled in your key.

**Rate limit hit** — Gemini's free tier allows 15 requests per minute. If you see a rate limit error, wait a minute and try again. viral-ops adds a small delay between calls automatically to reduce this.

**High demand / 503 error** — Google's servers are busy. This is temporary. Wait 60 seconds and run again.

**`Invalid API key`** — go back to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey), create a new key, and update your `.env`.
