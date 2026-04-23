from datetime import datetime, timezone

import pytest

from viral_ops.scanner import VideoResult


def _make_video(view_count: int, channel_avg: float) -> VideoResult:
    return VideoResult(
        video_id="abc123",
        title="Test Video Title",
        channel_id="UC000",
        channel_name="Test Channel",
        channel_handle="@test",
        published_at=datetime.now(timezone.utc),
        view_count=view_count,
        like_count=0,
        comment_count=0,
        thumbnail_url="https://example.com/thumb.jpg",
        description="",
        channel_avg_views=channel_avg,
        virality_score=view_count / channel_avg if channel_avg > 0 else 0.0,
    )


def test_virality_score_basic():
    v = _make_video(1000, 500)
    assert v.virality_score == 2.0


def test_virality_score_below_threshold():
    v = _make_video(400, 500)
    assert v.virality_score == pytest.approx(0.8)


def test_flames_at_exactly_2x():
    v = _make_video(1000, 500)  # 2.0x — int(2.0 - 2.0) = 0
    assert v.flames == ""


def test_flames_at_3x():
    v = _make_video(1500, 500)  # 3.0x — 1 flame
    assert v.flames == "🔥"


def test_flames_at_5x():
    v = _make_video(2500, 500)  # 5.0x — 3 flames
    assert v.flames == "🔥🔥🔥"


def test_flames_capped_at_5():
    v = _make_video(50000, 500)  # 100x — capped at 5
    assert v.flames == "🔥🔥🔥🔥🔥"


def test_video_url():
    v = _make_video(1000, 500)
    assert v.video_url == "https://www.youtube.com/watch?v=abc123"


def test_score_display_includes_score():
    v = _make_video(1500, 500)  # 3.0x
    assert "3.0x" in v.score_display
