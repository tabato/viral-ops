# Claude Setup (Anthropic)

Use Claude if you're already on an Anthropic plan or want the most nuanced AI copy angles. Claude tends to write in a more natural, voice-forward style than other providers — good if your content has a strong personal brand.

## Model

viral-ops uses `claude-sonnet-4-6` — Anthropic's current flagship model.

## Pricing

Claude is a paid API. Pricing at time of writing:

| | Cost |
|---|---|
| Input tokens | $3 / 1M tokens |
| Output tokens | $15 / 1M tokens |

A full viral-ops run (10 videos analyzed) uses roughly 20,000–30,000 tokens total. That's well under $0.50 per run.

Check current pricing at [anthropic.com/pricing](https://anthropic.com/pricing).

## Setup

**1. Create an Anthropic account**

[console.anthropic.com](https://console.anthropic.com)

**2. Add credits**

Go to **Billing** → add a minimum amount (usually $5) to activate API access.

**3. Generate an API key**

Go to **API Keys** → **Create Key** → copy it.

**4. Add it to your `.env`**

```bash
ANTHROPIC_API_KEY=your_key_here
```

**5. Set it in `profile.yml`**

```yaml
ai_provider: claude
```

## Troubleshooting

**`ANTHROPIC_API_KEY not set`** — check your `.env` file exists and is in the project root.

**`401 Authentication error`** — your key may have been rotated or is invalid. Generate a new one at the console.

**`529 Overloaded`** — Anthropic's API is under load. Retry in a moment; viral-ops will show the error per-video so you won't lose your whole run.
