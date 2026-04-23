# Contributing to viral-ops

Thanks for wanting to help. A few quick guidelines.

## What's welcome

- **New AI provider support** — Mistral, Cohere, local models via Ollama, etc.
- **New output formats** — Notion export, CSV, JSON swipe file
- **Platform expansion** — TikTok, Instagram Reels, X/Twitter virality scanning
- **Gallery improvements** — better design, filtering, sorting
- **Bug fixes** — especially around YouTube API edge cases (private videos, age-gated, live streams)
- **Performance** — async scanning, smarter quota usage

## Getting started

```bash
git clone https://github.com/thomasabato/viral-ops.git
cd viral-ops
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp templates/profile.example.yml profile.yml
cp templates/creators.example.yml creators.yml
cp templates/.env.example .env
```

## Guidelines

- **Keep it one command.** The whole point is `viral-ops` and done. Don't add required setup steps.
- **Match the terminal style.** Use `rich` for all output — no plain `print()` calls.
- **Don't break the free path.** Gemini free tier must always work out of the box.
- **Small PRs over big ones.** One feature or fix per PR makes review fast.

## Submitting a PR

1. Fork → branch off `main`
2. Make your change
3. Test with a real `profile.yml` and `creators.yml`
4. Open a PR with a short description of what changed and why

No formal issue required for small fixes — just open the PR.
