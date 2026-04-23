from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config, Profile
from .scanner import VideoResult

console = Console()


@dataclass
class AnalysisResult:
    video: VideoResult
    hook_analysis: str
    viral_reasons: str
    copy_angles: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# Prompt
# ------------------------------------------------------------------

def _build_prompt(video: VideoResult, profile: Profile) -> str:
    return f"""You are an expert content strategist and viral growth consultant.

VIRAL VIDEO:
- Title: {video.title}
- Channel: {video.channel_name}
- Views: {video.view_count:,}
- Virality Score: {video.virality_score:.2f}x above this channel's average
- Description excerpt: {video.description[:400]}

CREATOR PROFILE:
- Niche: {profile.niche}
- Target Audience: {profile.target_audience}
- Content Style: {profile.content_style}

Analyze why this video went viral and generate tailored copy angles.

Return ONLY a valid JSON object with exactly these keys:
{{
  "hook_analysis": "2–3 sentences on why the title/hook is psychologically compelling — specificity, curiosity gap, emotional trigger, etc.",
  "viral_reasons": "2–3 sentences on the core mechanics that drove virality — format, timing, topic momentum, emotional response, shareability.",
  "copy_angles": [
    "Angle 1: specific, actionable title idea adapted for the creator's niche and audience",
    "Angle 2: different angle — different emotion or format from angle 1",
    "Angle 3: contrarian or pattern-interrupt version for the same niche"
  ]
}}

Be specific. Reference the exact niche and audience. Do not use placeholders. Return ONLY the JSON."""


def _parse_json(text: str) -> Optional[dict]:
    text = text.strip()
    for fence in ("```json", "```"):
        if text.startswith(fence):
            text = text[len(fence):]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # last-ditch: try to find first { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return None


def _build_result(video: VideoResult, data: dict) -> AnalysisResult:
    return AnalysisResult(
        video=video,
        hook_analysis=data.get("hook_analysis", ""),
        viral_reasons=data.get("viral_reasons", ""),
        copy_angles=data.get("copy_angles", [])[:3],
    )


# ------------------------------------------------------------------
# Provider implementations
# ------------------------------------------------------------------

def _analyze_gemini(video: VideoResult, profile: Profile, api_key: str) -> Optional[AnalysisResult]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(_build_prompt(video, profile))
    data = _parse_json(response.text)
    return _build_result(video, data) if data else None


def _analyze_claude(video: VideoResult, profile: Profile, api_key: str) -> Optional[AnalysisResult]:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": _build_prompt(video, profile)}],
    )
    data = _parse_json(message.content[0].text)
    return _build_result(video, data) if data else None


def _analyze_openai(video: VideoResult, profile: Profile, api_key: str) -> Optional[AnalysisResult]:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": _build_prompt(video, profile)}],
        response_format={"type": "json_object"},
    )
    data = _parse_json(resp.choices[0].message.content or "")
    return _build_result(video, data) if data else None


# ------------------------------------------------------------------
# Analyzer
# ------------------------------------------------------------------

class ContentAnalyzer:
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.profile.ai_provider

    def _analyze_one(self, video: VideoResult) -> Optional[AnalysisResult]:
        p = self.config.profile
        if self.provider == "gemini":
            if not self.config.gemini_api_key:
                raise EnvironmentError("GEMINI_API_KEY not set in .env")
            return _analyze_gemini(video, p, self.config.gemini_api_key)
        elif self.provider == "claude":
            if not self.config.anthropic_api_key:
                raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")
            return _analyze_claude(video, p, self.config.anthropic_api_key)
        elif self.provider == "openai":
            if not self.config.openai_api_key:
                raise EnvironmentError("OPENAI_API_KEY not set in .env")
            return _analyze_openai(video, p, self.config.openai_api_key)
        else:
            raise ValueError(f"Unknown ai_provider: '{self.provider}'. Use gemini, claude, or openai.")

    def analyze_top(self, outliers: list[VideoResult], limit: int = 10) -> list[AnalysisResult]:
        top = sorted(outliers, key=lambda v: v.virality_score, reverse=True)[:limit]
        results: list[AnalysisResult] = []

        provider_label = {
            "gemini": "Gemini 1.5 Flash (free)",
            "claude": "Claude (Anthropic)",
            "openai": "GPT-4o mini (OpenAI)",
        }.get(self.provider, self.provider)

        console.print(f"\n🧠  Analyzing with [bold]{provider_label}[/bold]…\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task("", total=len(top))

            for i, video in enumerate(top, 1):
                short = video.title[:55] + "…" if len(video.title) > 55 else video.title
                progress.update(task, description=f"[{i}/{len(top)}] {short}")

                try:
                    result = self._analyze_one(video)
                    if result:
                        results.append(result)
                        console.print(f"  [green]✓[/green]  {short}")
                    else:
                        console.print(f"  [yellow]⚠[/yellow]  Couldn't parse response: {short}")
                except Exception as exc:
                    console.print(f"  [red]✗[/red]  {short}: {exc}")

                progress.advance(task)

        return results


# ------------------------------------------------------------------
# Swipe file
# ------------------------------------------------------------------

def save_swipe_file(results: list[AnalysisResult], path: Path, profile_niche: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = [
        "# 🔥 Viral Content Swipe File",
        f"> Generated: {now}  |  Niche: {profile_niche}",
        "",
        "---",
        "",
    ]

    for i, r in enumerate(results, 1):
        v = r.video
        flames = v.flames
        lines += [
            f"## {i}. {v.title}",
            "",
            f"| | |",
            f"|---|---|",
            f"| **Channel** | {v.channel_name} ({v.channel_handle}) |",
            f"| **Views** | {v.view_count:,} |",
            f"| **Virality Score** | {v.virality_score:.2f}x {flames} |",
            f"| **URL** | [{v.video_url}]({v.video_url}) |",
            "",
            "### Hook Analysis",
            "",
            r.hook_analysis,
            "",
            "### Why It Went Viral",
            "",
            r.viral_reasons,
            "",
            f"### Copy Angles for *{profile_niche}*",
            "",
        ]
        for j, angle in enumerate(r.copy_angles, 1):
            lines.append(f"{j}. {angle}")

        lines += ["", "---", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
