from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table

from . import __version__
from .analyzer import ContentAnalyzer, AnalysisResult, save_swipe_file
from .config import load_config
from .gallery import generate_gallery
from .scanner import YouTubeScanner, VideoResult

console = Console()

app = typer.Typer(
    name="viral-ops",
    help="🔥 Viral content intelligence — scan YouTube, score virality, generate AI copy angles.",
    no_args_is_help=False,
    invoke_without_command=True,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
)

PROVIDER_LABELS = {
    "gemini": "Gemini 2.0 Flash  [dim](FREE — recommended)[/dim]",
    "claude": "Claude (Anthropic)",
    "openai": "GPT-4o mini (OpenAI)",
}

OUTLIERS_FILE = Path("outliers.json")


# ── Outlier persistence ────────────────────────────────────────────────────

def _video_to_dict(v: VideoResult, rank: int) -> dict:
    return {
        "rank": rank,
        "video_id": v.video_id,
        "title": v.title,
        "channel_id": v.channel_id,
        "channel_name": v.channel_name,
        "channel_handle": v.channel_handle,
        "published_at": v.published_at.isoformat(),
        "view_count": v.view_count,
        "like_count": v.like_count,
        "comment_count": v.comment_count,
        "thumbnail_url": v.thumbnail_url,
        "description": v.description,
        "channel_avg_views": v.channel_avg_views,
        "virality_score": v.virality_score,
    }


def _dict_to_video(d: dict) -> VideoResult:
    pub = d["published_at"]
    published_at = datetime.fromisoformat(pub)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    return VideoResult(
        video_id=d["video_id"],
        title=d["title"],
        channel_id=d["channel_id"],
        channel_name=d["channel_name"],
        channel_handle=d["channel_handle"],
        published_at=published_at,
        view_count=d["view_count"],
        like_count=d["like_count"],
        comment_count=d["comment_count"],
        thumbnail_url=d["thumbnail_url"],
        description=d["description"],
        channel_avg_views=d["channel_avg_views"],
        virality_score=d["virality_score"],
    )


def save_outliers(outliers: list[VideoResult], niche: str, path: Path = OUTLIERS_FILE) -> None:
    ranked = sorted(outliers, key=lambda v: v.virality_score, reverse=True)
    data = {
        "generated_at": datetime.now().isoformat(),
        "niche": niche,
        "count": len(ranked),
        "outliers": [_video_to_dict(v, i) for i, v in enumerate(ranked, 1)],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_outliers(path: Path = OUTLIERS_FILE) -> tuple[list[VideoResult], str]:
    if not path.exists():
        raise FileNotFoundError(
            f"No saved outliers found at '{path}'. Run 'viral-ops' first to scan channels."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    videos = [_dict_to_video(d) for d in data["outliers"]]
    return videos, data.get("niche", "")


# ── Shared UI helpers ──────────────────────────────────────────────────────

def _print_header() -> None:
    console.print()
    console.print(
        Panel.fit(
            "[bold white]🔥  VIRAL OPS[/bold white]  [dim]v{v}[/dim]\n"
            "[dim]Content intelligence for creators[/dim]".format(v=__version__),
            border_style="bright_yellow",
            padding=(1, 6),
        )
    )
    console.print()


def _print_config_summary(config) -> None:
    p = config.profile
    provider_label = PROVIDER_LABELS.get(p.ai_provider, p.ai_provider)
    console.print(f"📋  [bold]Niche[/bold]       {p.niche}")
    console.print(f"🎯  [bold]Audience[/bold]    {p.target_audience}")
    console.print(f"✍️   [bold]Style[/bold]       {p.content_style}")
    console.print(f"🤖  [bold]AI Provider[/bold] {provider_label}")
    console.print(f"📅  [bold]Window[/bold]      Last {p.months_back} months")
    console.print(f"🔥  [bold]Threshold[/bold]   ≥ {p.virality_threshold}x")
    console.print(f"📺  [bold]Channels[/bold]    {len(config.creators)}")
    console.print()


def _fmt_views(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def _print_outliers_table(outliers: list[VideoResult], top: int = 10) -> None:
    ranked = sorted(outliers, key=lambda v: v.virality_score, reverse=True)[:top]
    table = Table(
        title=f"🔥  Top {len(ranked)} Viral Outliers",
        box=box.ROUNDED,
        border_style="bright_yellow",
        show_lines=True,
        title_style="bold white",
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Channel", style="bold cyan", max_width=22)
    table.add_column("Title", max_width=48)
    table.add_column("Score", justify="right", style="bold yellow")
    table.add_column("Views", justify="right", style="green")

    for i, v in enumerate(ranked, 1):
        title_short = v.title[:46] + "…" if len(v.title) > 46 else v.title
        score_txt = f"{v.virality_score:.1f}x {v.flames}".strip()
        table.add_row(str(i), v.channel_name[:20], title_short, score_txt, _fmt_views(v.view_count))

    console.print()
    console.print(table)
    console.print()


def _run_analysis(
    videos: list[VideoResult],
    config,
    output: Path,
    no_browser: bool,
) -> None:
    console.rule("[bold]AI Analysis[/bold]")
    try:
        analyzer = ContentAnalyzer(config)
        results = analyzer.analyze_top(videos, limit=len(videos))
    except EnvironmentError as exc:
        console.print(f"[bold red]✗  AI config error:[/bold red] {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[bold red]✗  Analysis failed:[/bold red] {exc}")
        raise typer.Exit(1)

    if not results:
        console.print(
            "[yellow]⚠  No analysis results.[/yellow]\n"
            "[dim]  Try a different ai_provider in profile.yml (gemini, claude, openai)[/dim]"
        )
        raise typer.Exit(1)

    output.mkdir(parents=True, exist_ok=True)
    swipe_path = output / "swipe_file.md"
    console.print(f"\n📝  Saving [bold]{swipe_path}[/bold]…")
    save_swipe_file(results, swipe_path, config.profile.niche)

    console.rule("[bold]Gallery[/bold]")
    gallery_path = generate_gallery(
        results,
        output_dir=output,
        profile_niche=config.profile.niche,
        open_browser=not no_browser,
    )

    console.print()
    console.print(Panel.fit(
        f"[bold green]✅  Done![/bold green]\n\n"
        f"  🔥  {len(results)} videos analyzed\n"
        f"  🖼️   [link=file://{gallery_path.resolve()}]{gallery_path}[/link]\n"
        f"  📝  [link=file://{swipe_path.resolve()}]{swipe_path}[/link]",
        border_style="green",
        padding=(1, 4),
    ))
    console.print()


# ── Main command ───────────────────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    profile: Path = typer.Option(Path("profile.yml"), "--profile", "-p", show_default=True),
    creators: Path = typer.Option(Path("creators.yml"), "--creators", "-c", show_default=True),
    output: Path = typer.Option(Path("."), "--output", "-o", show_default=True),
    no_browser: bool = typer.Option(False, "--no-browser"),
    top: int = typer.Option(3, "--top", help="Top N outliers to analyze with AI", min=1, max=25),
) -> None:
    """Scan channels, score virality, analyze top outliers with AI."""
    if ctx.invoked_subcommand is not None:
        return

    _print_header()

    try:
        config = load_config(profile_path=profile, creators_path=creators)
    except (FileNotFoundError, EnvironmentError, KeyError) as exc:
        console.print(f"[bold red]✗  Config error:[/bold red] {exc}")
        raise typer.Exit(1)

    _print_config_summary(config)

    console.rule("[bold]Scanning channels[/bold]")
    console.print()

    scanner = YouTubeScanner(
        api_key=config.youtube_api_key,
        months_back=config.profile.months_back,
        virality_threshold=config.profile.virality_threshold,
    )

    try:
        all_videos = scanner.scan_all(config.creators)
    except Exception as exc:
        console.print(f"[bold red]✗  Scan failed:[/bold red] {exc}")
        raise typer.Exit(1)

    total_videos = len(all_videos)
    console.print(
        f"\n✅  Scanned [bold]{len(config.creators)}[/bold] channels — "
        f"[bold]{total_videos}[/bold] videos in last {config.profile.months_back} months\n"
    )

    if total_videos == 0:
        console.print("[yellow]⚠  No videos found. Check creators.yml and date window.[/yellow]")
        raise typer.Exit(0)

    outliers = scanner.get_outliers(all_videos, content_type=config.profile.content_type)
    type_label = {"shorts": " shorts", "longform": " longform"}.get(config.profile.content_type, "")
    console.print(f"🔥  [bold]{len(outliers)}[/bold]{type_label} outliers above {config.profile.virality_threshold}x threshold")

    if not outliers:
        console.print("[yellow]⚠  No outliers found. Try lowering virality_threshold in profile.yml.[/yellow]")
        raise typer.Exit(0)

    # Save full outlier list before AI analysis
    save_outliers(outliers, config.profile.niche)
    console.print(f"💾  [dim]All {len(outliers)} outliers saved to outliers.json — use 'viral-ops analyze' to dig into any of them[/dim]\n")

    _print_outliers_table(outliers, top=top)

    _run_analysis(
        sorted(outliers, key=lambda v: v.virality_score, reverse=True)[:top],
        config, output, no_browser,
    )


# ── Analyze command ────────────────────────────────────────────────────────

@app.command("analyze")
def analyze_cmd(
    rank: Optional[int] = typer.Option(None, "--rank", "-r", help="Rank of video from outliers.json"),
    profile: Path = typer.Option(Path("profile.yml"), "--profile", "-p"),
    output: Path = typer.Option(Path("."), "--output", "-o"),
    no_browser: bool = typer.Option(False, "--no-browser"),
    outliers_file: Path = typer.Option(OUTLIERS_FILE, "--from", help="Path to outliers.json"),
) -> None:
    """Analyze any saved outlier video on demand."""
    _print_header()

    try:
        outliers, niche = load_outliers(outliers_file)
    except FileNotFoundError as exc:
        console.print(f"[bold red]✗[/bold red]  {exc}")
        raise typer.Exit(1)

    try:
        config = load_config(profile_path=profile)
    except (FileNotFoundError, EnvironmentError) as exc:
        console.print(f"[bold red]✗  Config error:[/bold red] {exc}")
        raise typer.Exit(1)

    # Show the full saved list
    _print_outliers_table(outliers, top=len(outliers))

    # Pick which one to analyze
    if rank is None:
        rank = IntPrompt.ask(
            f"Which video do you want to analyze? (1–{len(outliers)})",
            console=console,
        )

    if not 1 <= rank <= len(outliers):
        console.print(f"[red]✗  Rank must be between 1 and {len(outliers)}[/red]")
        raise typer.Exit(1)

    video = outliers[rank - 1]
    console.print(f"\n🎯  Analyzing: [bold]{video.title}[/bold] ({video.channel_name})\n")

    _run_analysis([video], config, output, no_browser)


if __name__ == "__main__":
    app()
