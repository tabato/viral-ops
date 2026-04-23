from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)

console = Console()


@dataclass
class VideoResult:
    video_id: str
    title: str
    channel_id: str
    channel_name: str
    channel_handle: str
    published_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    thumbnail_url: str
    description: str
    channel_avg_views: float
    virality_score: float
    duration_seconds: int = 0

    @property
    def is_short(self) -> bool:
        return 0 < self.duration_seconds <= 60

    @property
    def video_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    @property
    def flames(self) -> str:
        count = min(5, max(0, int(self.virality_score - 2.0)))
        return "🔥" * count

    @property
    def score_display(self) -> str:
        f = self.flames
        return f"{self.virality_score:.1f}x {f}".strip()


def _parse_duration(duration: str) -> int:
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)


class YouTubeScanner:
    def __init__(
        self,
        api_key: str,
        months_back: int = 4,
        virality_threshold: float = 2.0,
    ):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.months_back = months_back
        self.virality_threshold = virality_threshold
        self.cutoff = datetime.now(timezone.utc) - timedelta(days=months_back * 30)

    # ------------------------------------------------------------------
    # Channel resolution
    # ------------------------------------------------------------------

    def _resolve_by_handle(self, handle: str) -> Optional[tuple[str, str]]:
        try:
            resp = self.youtube.channels().list(
                part="snippet",
                forHandle=handle,
            ).execute()
            items = resp.get("items", [])
            if items:
                return items[0]["id"], items[0]["snippet"]["title"]
        except HttpError:
            pass
        return None

    def _resolve_by_username(self, username: str) -> Optional[tuple[str, str]]:
        try:
            resp = self.youtube.channels().list(
                part="snippet",
                forUsername=username,
            ).execute()
            items = resp.get("items", [])
            if items:
                return items[0]["id"], items[0]["snippet"]["title"]
        except HttpError:
            pass
        return None

    def _resolve_by_id(self, channel_id: str) -> Optional[tuple[str, str]]:
        try:
            resp = self.youtube.channels().list(
                part="snippet",
                id=channel_id,
            ).execute()
            items = resp.get("items", [])
            if items:
                return items[0]["id"], items[0]["snippet"]["title"]
        except HttpError:
            pass
        return None

    def resolve_channel(self, handle_or_id: str) -> Optional[tuple[str, str]]:
        """Return (channel_id, channel_name) or None."""
        raw = handle_or_id.strip()

        if raw.startswith("UC"):
            result = self._resolve_by_id(raw)
            if result:
                return result

        handle = raw.lstrip("@")
        result = self._resolve_by_handle(handle)
        if result:
            return result

        result = self._resolve_by_username(handle)
        if result:
            return result

        return None

    # ------------------------------------------------------------------
    # Video fetching
    # ------------------------------------------------------------------

    def _get_uploads_playlist(self, channel_id: str) -> Optional[str]:
        resp = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id,
        ).execute()
        items = resp.get("items", [])
        if items:
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return None

    def _fetch_video_ids_since(self, playlist_id: str) -> list[tuple[str, datetime]]:
        results: list[tuple[str, datetime]] = []
        next_page_token: Optional[str] = None
        stop = False

        while not stop:
            params: dict = dict(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
            )
            if next_page_token:
                params["pageToken"] = next_page_token

            resp = self.youtube.playlistItems().list(**params).execute()

            for item in resp.get("items", []):
                pub_str = item["snippet"]["publishedAt"]
                published_at = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))

                if published_at < self.cutoff:
                    stop = True
                    break

                video_id = item["contentDetails"]["videoId"]
                results.append((video_id, published_at))

            next_page_token = resp.get("nextPageToken")
            if not next_page_token:
                break

        return results

    def _fetch_video_stats(self, video_ids: list[str]) -> list[dict]:
        items = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i : i + 50]
            resp = self.youtube.videos().list(
                part="statistics,snippet,contentDetails",
                id=",".join(batch),
            ).execute()
            items.extend(resp.get("items", []))
        return items

    def fetch_channel_videos(
        self,
        channel_id: str,
        channel_name: str,
        channel_handle: str,
    ) -> list[VideoResult]:
        playlist_id = self._get_uploads_playlist(channel_id)
        if not playlist_id:
            return []

        id_date_pairs = self._fetch_video_ids_since(playlist_id)
        if not id_date_pairs:
            return []

        video_ids = [pair[0] for pair in id_date_pairs]
        pub_map = {pair[0]: pair[1] for pair in id_date_pairs}

        raw_items = self._fetch_video_stats(video_ids)

        videos: list[VideoResult] = []
        for item in raw_items:
            stats = item.get("statistics", {})
            snippet = item["snippet"]

            thumbs = snippet.get("thumbnails", {})
            thumbnail_url = (
                thumbs.get("maxres", {}).get("url")
                or thumbs.get("standard", {}).get("url")
                or thumbs.get("high", {}).get("url")
                or thumbs.get("medium", {}).get("url")
                or thumbs.get("default", {}).get("url")
                or ""
            )

            duration_seconds = _parse_duration(
                item.get("contentDetails", {}).get("duration", "")
            )

            videos.append(
                VideoResult(
                    video_id=item["id"],
                    title=snippet.get("title", ""),
                    channel_id=channel_id,
                    channel_name=channel_name,
                    channel_handle=channel_handle,
                    published_at=pub_map.get(item["id"], datetime.now(timezone.utc)),
                    view_count=int(stats.get("viewCount", 0)),
                    like_count=int(stats.get("likeCount", 0)),
                    comment_count=int(stats.get("commentCount", 0)),
                    thumbnail_url=thumbnail_url,
                    description=snippet.get("description", "")[:500],
                    channel_avg_views=0.0,
                    virality_score=0.0,
                    duration_seconds=duration_seconds,
                )
            )

        if videos:
            avg = sum(v.view_count for v in videos) / len(videos)
            for v in videos:
                v.channel_avg_views = avg
                v.virality_score = (v.view_count / avg) if avg > 0 else 0.0

        return videos

    # ------------------------------------------------------------------
    # Full scan
    # ------------------------------------------------------------------

    def scan_all(self, creators: list[str]) -> list[VideoResult]:
        all_videos: list[VideoResult] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=28),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task("Scanning…", total=len(creators))

            for creator in creators:
                short = creator[:30]
                progress.update(task, description=f"📡  {short:<30}")

                resolved = self.resolve_channel(creator)
                if not resolved:
                    console.print(f"  [yellow]⚠[/yellow]  Could not find channel: [bold]{creator}[/bold]")
                    progress.advance(task)
                    continue

                channel_id, channel_name = resolved

                try:
                    videos = self.fetch_channel_videos(channel_id, channel_name, creator)
                    all_videos.extend(videos)
                    console.print(
                        f"  [green]✓[/green]  [bold]{channel_name}[/bold] "
                        f"[dim]— {len(videos)} videos[/dim]"
                    )
                except HttpError as exc:
                    console.print(f"  [red]✗[/red]  {creator}: API error — {exc}")

                progress.advance(task)

        return all_videos

    # ------------------------------------------------------------------
    # Outlier detection
    # ------------------------------------------------------------------

    def get_outliers(self, videos: list[VideoResult], content_type: str = "both") -> list[VideoResult]:
        if content_type == "shorts":
            videos = [v for v in videos if v.is_short]
        elif content_type == "longform":
            videos = [v for v in videos if not v.is_short]
        return [v for v in videos if v.virality_score >= self.virality_threshold]
