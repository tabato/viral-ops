# OpenAI Setup

Use OpenAI if you're already paying for an API plan or want GPT-4o mini for the copy angle generation.

## Model

viral-ops uses `gpt-4o-mini` — fast, affordable, and solid at structured JSON tasks.

## Pricing

| | Cost |
|---|---|
| Input tokens | $0.15 / 1M tokens |
| Output tokens | $0.60 / 1M tokens |

A full viral-ops run (3 videos analyzed) uses roughly 5,000–8,000 tokens total — well under $0.01 per run.

Check current pricing at [openai.com/pricing](https://openai.com/pricing).

## Setup

**1. Create an OpenAI account**

[platform.openai.com](https://platform.openai.com)

**2. Add credits**

Go to **Billing → Add payment method**. A small top-up ($5) is enough for hundreds of runs.

**3. Generate an API key**

Go to **API Keys → Create new secret key** → copy it.

**4. Add it to your `.env`**

```bash
OPENAI_API_KEY=your_key_here
```

**5. Set it in `profile.yml`**

```yaml
ai_provider: openai
```

## Troubleshooting

**`OPENAI_API_KEY not set`** — check your `.env` file is in the project root.

**`401 Unauthorized`** — your key may be invalid or expired. Generate a new one at the platform dashboard.

**`429 Rate limit`** — your account tier has a low rate limit. Wait a moment and try again, or upgrade your usage tier.
