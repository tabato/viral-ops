# Gemini Setup — FREE ✨ (Recommended)

Gemini 1.5 Flash is the default AI provider for viral-ops and it's **completely free**.

No billing required. No credit card. Just a Google account.

## Free tier limits

| Limit | Amount |
|---|---|
| Requests per minute | 15 |
| Tokens per day | 1,000,000 |
| Cost | $0 |

A full viral-ops run (10 videos analyzed) uses roughly 15,000–20,000 tokens. You could run it 50+ times a day on the free tier.

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

That's it. No billing setup, no quotas to worry about.

## Model

viral-ops uses `gemini-2.0-flash` — Google's latest fast model, optimized for high-volume tasks. It's accurate, quick, and handles the JSON-structured analysis prompts reliably.

## Troubleshooting

**`GEMINI_API_KEY not set`** — check your `.env` file is in the project root and you've run `source .venv/bin/activate` before running `viral-ops`.

**`429 Resource exhausted`** — you've hit the 15 RPM limit. This shouldn't happen with viral-ops (10 sequential calls), but if it does, wait 60 seconds and retry.

**`Invalid API key`** — regenerate the key at AI Studio and update `.env`.
