from __future__ import annotations

import html
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

from .analyzer import AnalysisResult
from .scanner import VideoResult

console = Console()


def _fmt_views(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "viral-ops/0.1"})
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception:
        return False


def _card_html(result: AnalysisResult, thumb_src: str, rank: int) -> str:
    v = result.video
    safe_title = html.escape(v.title)
    safe_channel = html.escape(v.channel_name)
    badge_text = html.escape(f"{v.virality_score:.1f}x {v.flames}".strip())
    views_str = _fmt_views(v.view_count)
    safe_url = html.escape(v.video_url)

    img_tag = (
        f'<img src="{html.escape(thumb_src)}" alt="{safe_title}" loading="lazy">'
        if thumb_src
        else '<div class="thumb-placeholder">🎬</div>'
    )

    # Hover overlay: first angle only + hint to expand
    first_angle = result.copy_angles[0] if result.copy_angles else ""
    remaining = max(0, len(result.copy_angles) - 1)
    hint = f'<div class="copy-hint">+{remaining} more &mdash; click Analysis below &darr;</div>' if remaining else ""

    # Full analysis: hook + viral reasons + all angles
    full_angles = "".join(
        f'<div class="copy-angle-full">{html.escape(a)}</div>'
        for a in result.copy_angles
    )

    return f"""
<article class="card">
  <a href="{safe_url}" target="_blank" rel="noopener" class="thumb-link">
    <div class="thumb-wrap">
      {img_tag}
      <span class="rank-badge">#{rank}</span>
      <span class="virality-badge">{badge_text}</span>
      <div class="copy-overlay">
        <div class="copy-inner">
          <div class="copy-heading">✦ Copy Angle</div>
          <div class="copy-angle">{html.escape(first_angle)}</div>
          {hint}
        </div>
      </div>
    </div>
  </a>
  <div class="card-body">
    <div class="card-title">{safe_title}</div>
    <div class="card-meta">
      <span class="channel-name">{safe_channel}</span>
      <span class="view-count">{views_str} views</span>
    </div>
  </div>
  <details class="analysis-details">
    <summary><span class="summary-icon">▶</span> Full Analysis</summary>
    <div class="analysis-body">
      <h5>Hook</h5>
      <p>{html.escape(result.hook_analysis)}</p>
      <h5>Why it went viral</h5>
      <p>{html.escape(result.viral_reasons)}</p>
      <h5>Copy Angles</h5>
      {full_angles}
    </div>
  </details>
</article>"""


_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:      #0f0f0f;
  --bg2:     #161616;
  --card-bg: #1a1a1a;
  --text:    #f1f1f1;
  --text2:   #aaaaaa;
  --text3:   #717171;
  --yellow:  #ffd700;
  --border:  rgba(255,255,255,0.07);
  --overlay: rgba(0,0,0,0.91);
  --radius:  10px;
}

html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

/* ── Header ─────────────────────────────── */
header {
  position: sticky; top: 0; z-index: 200;
  background: rgba(15,15,15,0.92);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--border);
  padding: 18px 28px;
}

.header-inner {
  max-width: 1560px; margin: 0 auto;
  display: flex; align-items: center;
  justify-content: space-between;
  gap: 16px; flex-wrap: wrap;
}

.brand h1 { font-size: 1.1em; font-weight: 700; letter-spacing: -.02em; }
.brand p  { font-size: .75em; color: var(--text3); margin-top: 2px; font-style: italic; }

.stats { display: flex; gap: 28px; }
.stat  { text-align: right; }
.stat-val { display: block; font-size: 1.15em; font-weight: 800; color: var(--yellow); }
.stat-lbl { display: block; font-size: .68em; color: var(--text3); text-transform: uppercase; letter-spacing: .08em; margin-top: 1px; }

/* ── Grid ────────────────────────────────── */
.grid-wrapper { max-width: 1560px; margin: 0 auto; padding: 32px 24px 56px; }

.section-label {
  font-size: .72em; font-weight: 700;
  letter-spacing: .12em; text-transform: uppercase;
  color: var(--text3); margin-bottom: 22px;
  display: flex; align-items: center; gap: 10px;
}
.section-label::after { content: ""; flex: 1; height: 1px; background: var(--border); }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(288px, 1fr));
  gap: 20px;
}

/* ── Card ────────────────────────────────── */
.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border);
  transition: transform .2s ease, border-color .22s ease, box-shadow .22s ease;
  display: flex; flex-direction: column;
}

.card:hover {
  transform: translateY(-4px);
  border-color: rgba(255,215,0,.32);
  box-shadow: 0 12px 40px rgba(0,0,0,.55), 0 0 0 1px rgba(255,215,0,.07);
}

/* Thumbnail — this is the only clickable link */
.thumb-link { display: block; text-decoration: none; color: inherit; }

.thumb-wrap {
  position: relative; aspect-ratio: 16/9;
  background: #0a0a0a; overflow: hidden;
}

.thumb-wrap img {
  width: 100%; height: 100%;
  object-fit: cover; display: block;
  transition: transform .35s ease;
}

.thumb-link:hover .thumb-wrap img { transform: scale(1.05); }

.thumb-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 2em; background: var(--bg2); color: var(--text3);
}

/* Badges */
.rank-badge {
  position: absolute; top: 8px; left: 10px;
  background: rgba(0,0,0,.72); color: var(--text2);
  font-size: .68em; font-weight: 700;
  padding: 3px 7px; border-radius: 4px; z-index: 2;
}

.virality-badge {
  position: absolute; top: 8px; right: 10px;
  background: var(--yellow); color: #0a0a0a;
  font-size: .73em; font-weight: 900;
  padding: 4px 9px; border-radius: 5px; z-index: 2;
  box-shadow: 0 2px 10px rgba(0,0,0,.6);
  white-space: nowrap; letter-spacing: .01em;
}

/* Hover overlay — triggers on thumbnail only */
.copy-overlay {
  position: absolute; inset: 0;
  background: var(--overlay);
  opacity: 0; transition: opacity .2s ease;
  z-index: 3; padding: 16px;
  display: flex; flex-direction: column; justify-content: flex-end;
}

.thumb-link:hover .copy-overlay { opacity: 1; }

.copy-inner {
  transform: translateY(8px);
  transition: transform .22s ease;
}
.thumb-link:hover .copy-inner { transform: translateY(0); }

.copy-heading {
  font-size: .68em; font-weight: 800;
  letter-spacing: .1em; text-transform: uppercase;
  color: var(--yellow); margin-bottom: 9px;
}

.copy-angle {
  border-left: 2px solid var(--yellow);
  background: rgba(255,215,0,.07);
  padding: 7px 11px;
  border-radius: 0 5px 5px 0;
  font-size: .79em; line-height: 1.48; color: #e8e8e8;
}

.copy-hint {
  margin-top: 8px;
  font-size: .72em; color: var(--text3);
  font-style: italic; letter-spacing: .01em;
}

/* Card body — NOT a link, just info */
.card-body { padding: 12px 14px 13px; flex: 1; cursor: default; }

.card-title {
  font-size: .88em; font-weight: 600;
  line-height: 1.42; color: var(--text);
  display: -webkit-box;
  -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; margin-bottom: 7px;
}

.card-meta { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.channel-name { font-size: .76em; color: var(--text2); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.view-count { font-size: .74em; color: var(--text3); white-space: nowrap; flex-shrink: 0; }

/* Analysis — clearly separate from the thumbnail */
.analysis-details { border-top: 1px solid var(--border); }

.analysis-details summary {
  padding: 10px 14px;
  cursor: pointer; list-style: none; user-select: none;
  font-size: .8em; font-weight: 600; color: var(--text3);
  display: flex; align-items: center; gap: 6px;
  transition: color .15s, background .15s;
}
.analysis-details summary::-webkit-details-marker { display: none; }
.analysis-details summary:hover { color: var(--text2); background: rgba(255,255,255,.03); }
.analysis-details[open] summary { color: var(--yellow); }

.summary-icon {
  display: inline-block; font-size: .7em;
  transition: transform .2s ease; color: var(--text3);
}
.analysis-details[open] .summary-icon { transform: rotate(90deg); color: var(--yellow); }

.analysis-body { padding: 0 14px 14px; }

.analysis-body h5 {
  font-size: .72em; font-weight: 700;
  text-transform: uppercase; letter-spacing: .08em;
  color: var(--yellow); margin: 12px 0 5px;
}
.analysis-body p {
  font-size: .82em; color: var(--text2); line-height: 1.6;
}

.copy-angle-full {
  border-left: 2px solid var(--yellow);
  background: rgba(255,215,0,.05);
  padding: 7px 11px;
  border-radius: 0 5px 5px 0;
  margin-bottom: 6px;
  font-size: .81em; line-height: 1.5; color: var(--text2);
}
.copy-angle-full:last-child { margin-bottom: 0; }

/* ── Footer ──────────────────────────────── */
footer {
  border-top: 1px solid var(--border);
  padding: 24px 28px; text-align: center;
  color: var(--text3); font-size: .78em;
}
footer a { color: var(--yellow); text-decoration: none; }
footer a:hover { text-decoration: underline; }

/* ── Responsive ──────────────────────────── */
@media (max-width: 600px) {
  .grid { grid-template-columns: 1fr; }
  .grid-wrapper { padding: 16px 12px 40px; }
  .stats { gap: 16px; }
}
"""


def generate_gallery(
    results: list[AnalysisResult],
    output_dir: Path,
    profile_niche: str,
    open_browser: bool = True,
) -> Path:
    thumbs_dir = output_dir / "thumbnails"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    console.print("\n🖼️   [bold]Downloading thumbnails…[/bold]")
    thumb_map: dict[str, str] = {}
    for r in results:
        v = r.video
        if not v.thumbnail_url:
            continue
        dest = thumbs_dir / f"{v.video_id}.jpg"
        if _download(v.thumbnail_url, dest):
            thumb_map[v.video_id] = f"thumbnails/{v.video_id}.jpg"
            console.print(f"  [dim]↓  {v.title[:60]}[/dim]")
        else:
            console.print(f"  [yellow]⚠[/yellow]  Failed: {v.title[:40]}")

    console.print("🌐  [bold]Generating gallery.html…[/bold]")

    cards = "".join(
        _card_html(r, thumb_map.get(r.video.video_id, ""), i)
        for i, r in enumerate(results, 1)
    )

    total_views = sum(r.video.view_count for r in results)
    avg_score = sum(r.video.virality_score for r in results) / len(results) if results else 0
    generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>viral-ops — Your competitors already blew up. Now you can too.</title>
  <style>{_CSS}</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">
      <div>
        <h1>viral-ops</h1>
        <p>Your competitors already blew up. Now you can too.</p>
      </div>
    </div>
    <div class="stats">
      <div class="stat">
        <span class="stat-val">{len(results)}</span>
        <span class="stat-lbl">Analyzed</span>
      </div>
      <div class="stat">
        <span class="stat-val">{avg_score:.1f}x</span>
        <span class="stat-lbl">Avg Score</span>
      </div>
      <div class="stat">
        <span class="stat-val">{_fmt_views(total_views)}</span>
        <span class="stat-lbl">Total Views</span>
      </div>
    </div>
  </div>
</header>

<div class="grid-wrapper">
  <div class="section-label">Hover thumbnail for a copy angle preview &nbsp;&middot;&nbsp; Click thumbnail to watch &nbsp;&middot;&nbsp; Expand Analysis for the full breakdown</div>
  <div class="grid">
    {cards}
  </div>
</div>

<footer>
  Generated by <a href="https://github.com/tabato/viral-ops">viral-ops</a> &nbsp;&middot;&nbsp; {generated_at}
</footer>

</body>
</html>"""

    gallery_path = output_dir / "gallery.html"
    gallery_path.write_text(html_doc, encoding="utf-8")

    if open_browser:
        console.print("🎉  [bold green]Opening gallery in browser…[/bold green]")
        webbrowser.open(gallery_path.resolve().as_uri())

    return gallery_path
