# viral-ops

<div align="center">

<br>

<a href="https://www.instagram.com/thomasabatojr/" target="_blank">
  <img src="assets/viral-ops-logo.png" alt="viral-ops — You went viral. And you knew exactly why." width="100%">
</a>

<br>

[![CI](https://github.com/tabato/viral-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/tabato/viral-ops/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![YouTube API](https://img.shields.io/badge/YouTube-Data%20API%20v3-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://developers.google.com/youtube/v3)
[![Gemini](https://img.shields.io/badge/Gemini-FREE%20tier-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com/)
[![Claude](https://img.shields.io/badge/Claude-Anthropic-C68642?style=flat-square)](https://anthropic.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20mini-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com)

<br>

### *Your competitors already blew up. Now you can too.*

<br>

`2,500+ videos scanned` &nbsp;·&nbsp; `130+ outliers found` &nbsp;·&nbsp; `30 AI copy angles` &nbsp;·&nbsp; `~30 seconds to scan`

</div>

<br>

**viral-ops** scans YouTube channels you admire, scores every video by how far it outperformed that channel's average, surfaces the top outliers, and uses AI to explain *exactly* why each one went viral — then generates three copy angles tailored to your niche.

Outputs: a swipe file in Markdown and a beautiful dark-mode gallery that opens in your browser automatically.

---

## Core Capabilities

- **Channel scanning** — point it at any YouTube handle or channel ID, scores every video in seconds
- **Virality scoring** — every video gets a score: `views ÷ channel average`. No guessing, no vibes
- **Outlier detection** — anything above your threshold (default 2×) is flagged automatically
- **AI analysis** — top outliers analyzed for hook mechanics, viral drivers, and 3 copy angles tailored to your exact niche
- **Dark-mode gallery** — YouTube-style grid with thumbnails, virality badges, copy angle previews on hover, full analysis on expand — auto-opens in your browser
- **Swipe file** — every hook, title, and copy angle saved to a clean Markdown file
- **On-demand analysis** — dig into any of the 128 saved outliers later with `viral-ops analyze`
- **Content type filter** — scan longform only, Shorts only, or both
- **Multi-provider AI** — Gemini free tier by default, Claude or OpenAI as alternatives

---

## Demo

![viral-ops demo](assets/demo-placeholder.svg)

> *Demo coming soon. Star the repo to get notified.*

---

## viral-ops vs. doing it manually

| | viral-ops | Manual Research |
|---|---|---|
| Videos scanned | 2,500+ in ~30 seconds | Scroll for hours |
| Channels at once | Unlimited | One at a time |
| Virality scoring | Automatic (math) | Eyeballed |
| AI copy angles | ✅ Instant, niche-specific | ❌ ChatGPT separately |
| Gallery export | ✅ Auto-opens in browser | ❌ Screenshot folder chaos |
| Swipe file | ✅ Clean Markdown | ❌ Notes app |
| Repeatable | ✅ One command | ❌ Start over every time |

---

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/tabato/viral-ops.git && cd viral-ops
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e .

# 2. Configure
cp templates/profile.example.yml profile.yml
cp templates/creators.example.yml creators.yml
cp templates/.env.example .env   # add your API keys

# 3. Run
viral-ops
```

> **Python 3.11+ required.** Run `python3.11 --version` to confirm. On Mac: `brew install python@3.11`

That's it. Gallery opens automatically when the run finishes.

→ Having trouble? See [SETUP.md](SETUP.md) for step-by-step API key setup and troubleshooting.

---

## API setup

### ✨ Gemini — FREE, no billing required (recommended)

Get a free key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — no credit card, instant.
Free tier: **15 req/min · 1M tokens/day · $0**.

→ Full setup guide: [GEMINI.md](GEMINI.md)

### Claude (Anthropic)

Paid API. Best if you want more voice-forward copy angles or are already on an Anthropic plan.
Uses `claude-sonnet-4-6` · ~$0.50 per full run.

→ Full setup guide: [CLAUDE.md](CLAUDE.md)

---

## YouTube API key

1. Go to [console.cloud.google.com](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
2. Enable **YouTube Data API v3**
3. Go to **Credentials → Create API key → Public data**
4. Add to `.env`:
   ```
   YOUTUBE_API_KEY=your_key_here
   ```

Free tier: 10,000 quota units/day. A typical viral-ops run uses ~60–80 units.

---

## Usage philosophy

viral-ops is a **research tool**, not a content copy machine.

It tells you *why* things work — the psychological hooks, the format patterns, the timing signals. The copy angles it generates are starting points for your own voice, not scripts to paste verbatim.

The best creators don't copy what went viral. They understand it well enough to make their own version better.

---

## profile.yml reference

```yaml
niche: "AI sales coaching for business owners and entrepreneurs"
target_audience: "Founders and sales professionals who want to use AI to close more deals"
content_style: "Mix of talking head, tutorials, and short-form clips — direct and high-energy"

# FREE ✨ | gemini   claude   openai
ai_provider: gemini

virality_threshold: 2.0   # flag videos that outperform channel avg by this multiple
months_back: 4            # how far back to scan

# longform | shorts | both
content_type: both
```

The more specific your `niche` and `target_audience`, the sharper the AI copy angles.

---

## creators.yml reference

```yaml
creators:
  - "@AlexHormozi"
  - "@danmartell"
  - "UCX6OQ3DkcsbYNE6H8uQQuVA"   # channel ID also works
```

Mix handles (`@handle`) and channel IDs freely.

---

## Output files

| File | What's in it |
|---|---|
| `gallery.html` | Dark-mode grid — thumbnails, virality badges, copy angle preview on hover, full analysis on expand. Auto-opens in browser. |
| `swipe_file.md` | Full analysis per outlier: hook breakdown, why it went viral, 3 copy angles for your niche. |
| `outliers.json` | All ranked outliers from the scan — used by `viral-ops analyze`. |
| `thumbnails/` | Downloaded thumbnail images. |

---

## CLI reference

### `viral-ops` — full scan

Scans all channels, scores every video, analyzes the top 3 outliers with AI, and opens the gallery.

```
viral-ops [OPTIONS]

  -p, --profile PATH     Path to profile.yml        [default: profile.yml]
  -c, --creators PATH    Path to creators.yml        [default: creators.yml]
  -o, --output PATH      Output directory            [default: .]
      --top INTEGER      How many outliers to analyze [default: 3]
      --no-browser       Don't auto-open gallery
```

### `viral-ops analyze` — dig into any saved outlier

After a scan, all outliers are saved to `outliers.json`. Use this command to analyze any of them on demand — no re-scanning needed.

```bash
# Show the full ranked list and pick interactively
viral-ops analyze

# Go straight to a specific video by rank
viral-ops analyze --rank 7
```

**Example workflow:**
```
$ viral-ops
# → Scans 1,200+ videos, finds 128 outliers, analyzes top 3, opens gallery
# → All 128 outliers saved to outliers.json

$ viral-ops analyze --rank 12
# → Pulls video #12 from the saved list, runs AI analysis, appends to swipe_file.md
```

---

## How virality score works

```
virality_score = video_views / channel_average_views
```

A score of `3.5x` means that video got 3.5× more views than that channel's typical video in the same time window. This controls for channel size — a 100K-view video on a small channel can outperform a 1M-view video on a massive one.

Videos above `virality_threshold` (default `2.0`) are flagged as outliers.

---

## Disclaimers

- viral-ops uses the YouTube Data API v3 in compliance with [YouTube's Terms of Service](https://www.youtube.com/t/terms)
- No video content is downloaded — only metadata and publicly available thumbnails
- AI-generated copy angles are starting points, not finished scripts
- Respect the creators whose content you're studying — understand the pattern, don't lift the execution

---

## Inspiration

Inspired by **[career-ops](https://github.com/santifer/career-ops)**.

---

## 🔥 Went viral using viral-ops? [Share it.](https://github.com/tabato/viral-ops/issues/new?labels=went-viral&title=I+went+viral+using+viral-ops)

---

## Let's connect

If you're building something, making content, or just want to talk — find me here:

[![Instagram](https://img.shields.io/badge/@thomasabatojr-E4405F?style=flat-square&logo=instagram&logoColor=white)](https://www.instagram.com/thomasabatojr/)
[![YouTube](https://img.shields.io/badge/@ThomasAbato-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://www.youtube.com/@ThomasAbato)
[![TikTok](https://img.shields.io/badge/@thomasabato-000000?style=flat-square&logo=tiktok&logoColor=white)](https://www.tiktok.com/@thomasabato)
[![X](https://img.shields.io/badge/@thomasabato-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/thomasabato)
[![LinkedIn](https://img.shields.io/badge/Thomas%20Abato-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/thomasabato/)

---

## License

MIT © 2026
