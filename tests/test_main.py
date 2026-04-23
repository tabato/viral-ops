from datetime import datetime, timezone
from pathlib import Path

import pytest

from viral_ops.__main__ import save_outliers, load_outliers
from viral_ops.scanner import VideoResult


def _make_video(video_id: str = "abc123", virality_score: float = 3.0) -> VideoResult:
    return VideoResult(
        video_id=video_id,
        title="Test Video",
        channel_id="UC000",
        channel_name="Test Channel",
        channel_handle="@test",
        published_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        view_count=300_000,
        like_count=5000,
        comment_count=200,
        thumbnail_url="https://example.com/thumb.jpg",
        description="A test video.",
        channel_avg_views=100_000.0,
        virality_score=virality_score,
        duration_seconds=480,
    )


def test_save_and_load_round_trip(tmp_path):
    videos = [_make_video("vid1", 5.0), _make_video("vid2", 3.0)]
    path = tmp_path / "outliers.json"

    save_outliers(videos, niche="test niche", path=path)
    loaded, niche = load_outliers(path)

    assert niche == "test niche"
    assert len(loaded) == 2


def test_save_sorts_by_virality(tmp_path):
    videos = [_make_video("low", 2.0), _make_video("high", 8.0), _make_video("mid", 5.0)]
    path = tmp_path / "outliers.json"

    save_outliers(videos, niche="niche", path=path)
    loaded, _ = load_outliers(path)

    assert loaded[0].video_id == "high"
    assert loaded[1].video_id == "mid"
    assert loaded[2].video_id == "low"


def test_load_preserves_fields(tmp_path):
    v = _make_video("xyz", virality_score=4.2)
    path = tmp_path / "outliers.json"

    save_outliers([v], niche="niche", path=path)
    loaded, _ = load_outliers(path)
    result = loaded[0]

    assert result.video_id == "xyz"
    assert result.virality_score == pytest.approx(4.2)
    assert result.view_count == 300_000
    assert result.duration_seconds == 480
    assert result.published_at.tzinfo is not None


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_outliers(tmp_path / "nonexistent.json")
