from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .analyzer import ContentAnalyzer, save_swipe_file
from .config import load_config
from .gallery import generate_gallery
from .scanner import YouTubeScanner, VideoResult

console = Console()

app = typer.Typer(
    name="viral-ops",
    help="🔥 Viral content intelligence — scan YouTube, score virality, generate AI copy angles.",
    no_args_is_help=False,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
)

PROVIDER_LABELS = {
    "gemini": "Gemini 1.5 Flash  [dim](FREE — recommended)[/dim]",
    "claude": "Claude (Anthropic)",
    "openai": "GPT-4o mini (OpenAI)",
}


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

    def fmt_views(n: int) -> str:
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.0f}K"
        return str(n)

    for i, v in enumerate(ranked, 1):
        title_short = v.title[:46] + "…" if len(v.title) > 46 else v.title
        score_txt = f"{v.virality_score:.1f}x {v.flames}".strip()
        table.add_row(
            str(i),
            v.channel_name[:20],
            title_short,
            score_txt,
            fmt_views(v.view_count),
        )

    console.print()
    console.print(table)
    console.print()


def _print_final_summary(
    total_videos: int,
    channels_scanned: int,
    outlier_count: int,
    analyzed_count: int,
    gallery_path: Path,
    swipe_path: Path,
) -> None:
    console.print()
    console.print(Panel.fit(
        f"[bold green]✅  Done![/bold green]\n\n"
        f"  📺  {channels_scanned} channels  →  {total_videos} videos scanned\n"
        f"  🔥  {outlier_count} outliers found  →  {analyzed_count} analyzed\n"
        f"  🖼️   [link=file://{gallery_path.resolve()}]{gallery_path}[/link]\n"
        f"  📝  [link=file://{swipe_path.resolve()}]{swipe_path}[/link]",
        border_style="green",
        padding=(1, 4),
    ))
    console.print()


# ── CLI command ────────────────────────────────────────────────────────────

@app.command()
def main(
    profile: Path = typer.Option(
        Path("profile.yml"),
        "--profile",
        "-p",
        help="Path to profile.yml",
        show_default=True,
    ),
    creators: Path = typer.Option(
        Path("creators.yml"),
        "--creators",
        "-c",
        help="Path to creators.yml",
        show_default=True,
    ),
    output: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory for gallery.html and swipe_file.md",
        show_default=True,
    ),
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Don't auto-open gallery.html in the browser",
    ),
    top: int = typer.Option(
        10,
        "--top",
        help="Number of top outliers to analyze",
        min=1,
        max=25,
    ),
) -> None:
    """
    Scan YouTube channels, score virality, analyze outliers with AI,
    and generate a gallery + swipe file.
    """
    _print_header()

    # Load config
    try:
        config = load_config(profile_path=profile, creators_path=creators)
    except (FileNotFoundError, EnvironmentError, KeyError) as exc:
        console.print(f"[bold red]✗  Config error:[/bold red] {exc}")
        raise typer.Exit(1)

    _print_config_summary(config)

    # Scan channels
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

    channels_scanned = len(config.creators)
    total_videos = len(all_videos)

    console.print(
        f"\n✅  Scanned [bold]{channels_scanned}[/bold] channels — "
        f"[bold]{total_videos}[/bold] videos in last "
        f"{config.profile.months_back} months\n"
    )

    if total_videos == 0:
        console.print("[yellow]⚠  No videos found. Check your creators.yml and date window.[/yellow]")
        raise typer.Exit(0)

    # Outliers
    outliers = scanner.get_outliers(all_videos)
    console.print(
        f"🔥  [bold]{len(outliers)}[/bold] outliers above "
        f"{config.profile.virality_threshold}x threshold"
    )

    if not outliers:
        console.print(
            "[yellow]⚠  No viral outliers found. Try lowering virality_threshold in profile.yml.[/yellow]"
        )
        raise typer.Exit(0)

    _print_outliers_table(outliers, top=top)

    # AI analysis
    console.rule("[bold]AI Analysis[/bold]")

    try:
        analyzer = ContentAnalyzer(config)
        results = analyzer.analyze_top(outliers, limit=top)
    except EnvironmentError as exc:
        console.print(f"[bold red]✗  AI config error:[/bold red] {exc}")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[bold red]✗  Analysis failed:[/bold red] {exc}")
        raise typer.Exit(1)

    if not results:
        console.print("[yellow]⚠  No analysis results. Check your AI API key and try again.[/yellow]")
        raise typer.Exit(1)

    # Swipe file
    output.mkdir(parents=True, exist_ok=True)
    swipe_path = output / "swipe_file.md"
    console.print(f"\n📝  Saving [bold]{swipe_path}[/bold]…")
    save_swipe_file(results, swipe_path, config.profile.niche)

    # Gallery
    console.rule("[bold]Gallery[/bold]")
    gallery_path = generate_gallery(
        results,
        output_dir=output,
        profile_niche=config.profile.niche,
        open_browser=not no_browser,
    )

    _print_final_summary(
        total_videos=total_videos,
        channels_scanned=channels_scanned,
        outlier_count=len(outliers),
        analyzed_count=len(results),
        gallery_path=gallery_path,
        swipe_path=swipe_path,
    )


if __name__ == "__main__":
    app()
