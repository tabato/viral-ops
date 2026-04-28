from datetime import datetime, timezone

import pytest

from viral_ops.scanner import VideoResult, _parse_duration, _compute_virality_scores, YouTubeScanner


def _make_video(view_count: int, channel_avg: float, duration_seconds: int = 300) -> VideoResult:
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
        duration_seconds=duration_seconds,
    )


# ------------------------------------------------------------------
# _parse_duration
# ------------------------------------------------------------------

def test_parse_duration_full():
    assert _parse_duration("PT1H2M3S") == 3723

def test_parse_duration_minutes_seconds():
    assert _parse_duration("PT5M30S") == 330

def test_parse_duration_seconds_only():
    assert _parse_duration("PT45S") == 45

def test_parse_duration_minutes_only():
    assert _parse_duration("PT10M") == 600

def test_parse_duration_empty():
    assert _parse_duration("") == 0

def test_parse_duration_none_like():
    assert _parse_duration("PT") == 0


# ------------------------------------------------------------------
# is_short
# ------------------------------------------------------------------

def test_is_short_true():
    v = _make_video(1000, 500, duration_seconds=59)
    assert v.is_short is True

def test_is_short_exactly_60():
    v = _make_video(1000, 500, duration_seconds=60)
    assert v.is_short is True

def test_is_short_false_longform():
    v = _make_video(1000, 500, duration_seconds=61)
    assert v.is_short is False

def test_is_short_zero_duration():
    # duration unknown (0) → not treated as short
    v = _make_video(1000, 500, duration_seconds=0)
    assert v.is_short is False


# ------------------------------------------------------------------
# get_outliers content_type filtering
# ------------------------------------------------------------------

def _make_outlier_set():
    short = _make_video(10000, 1000, duration_seconds=45)   # 10x, short
    long1 = _make_video(5000, 1000, duration_seconds=600)   # 5x, longform
    long2 = _make_video(3000, 1000, duration_seconds=360)   # 3x, longform (>5min)
    below = _make_video(1500, 1000, duration_seconds=300)   # 1.5x, below threshold
    return [short, long1, long2, below]


def test_get_outliers_both():
    scanner = YouTubeScanner.__new__(YouTubeScanner)
    scanner.virality_threshold = 2.0
    results = scanner.get_outliers(_make_outlier_set(), content_type="both")
    assert len(results) == 3  # short + long1 + long2, not below

def test_get_outliers_shorts_only():
    scanner = YouTubeScanner.__new__(YouTubeScanner)
    scanner.virality_threshold = 2.0
    results = scanner.get_outliers(_make_outlier_set(), content_type="shorts")
    assert len(results) == 1
    assert results[0].duration_seconds == 45

def test_get_outliers_longform_only():
    scanner = YouTubeScanner.__new__(YouTubeScanner)
    scanner.virality_threshold = 2.0
    results = scanner.get_outliers(_make_outlier_set(), content_type="longform")
    assert len(results) == 2
    assert all(v.duration_seconds > 60 for v in results)


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


# ------------------------------------------------------------------
# _compute_virality_scores
# ------------------------------------------------------------------

def _make_raw_video(view_count: int, duration_seconds: int) -> VideoResult:
    """Build a VideoResult with zeroed scores (as fetch_channel_videos would before scoring)."""
    return VideoResult(
        video_id="x",
        title="T",
        channel_id="UC0",
        channel_name="C",
        channel_handle="@c",
        published_at=datetime.now(timezone.utc),
        view_count=view_count,
        like_count=0,
        comment_count=0,
        thumbnail_url="",
        description="",
        channel_avg_views=0.0,
        virality_score=0.0,
        duration_seconds=duration_seconds,
    )


def test_compute_scores_separates_shorts_and_longform():
    # 2 longform: 1000 and 3000 views → avg 2000
    # 2 shorts:    500 and 1500 views → avg 1000
    long1 = _make_raw_video(1000, 600)
    long2 = _make_raw_video(3000, 600)
    short1 = _make_raw_video(500, 30)
    short2 = _make_raw_video(1500, 30)

    _compute_virality_scores([long1, long2, short1, short2])

    assert long1.channel_avg_views == pytest.approx(2000)
    assert long2.channel_avg_views == pytest.approx(2000)
    assert short1.channel_avg_views == pytest.approx(1000)
    assert short2.channel_avg_views == pytest.approx(1000)

    assert long1.virality_score == pytest.approx(0.5)
    assert long2.virality_score == pytest.approx(1.5)
    assert short1.virality_score == pytest.approx(0.5)
    assert short2.virality_score == pytest.approx(1.5)


def test_compute_scores_longform_only_uses_overall():
    # No shorts → longform videos get the overall average
    v1 = _make_raw_video(1000, 600)
    v2 = _make_raw_video(3000, 600)

    _compute_virality_scores([v1, v2])

    assert v1.channel_avg_views == pytest.approx(2000)
    assert v1.virality_score == pytest.approx(0.5)
    assert v2.virality_score == pytest.approx(1.5)


def test_compute_scores_shorts_only_uses_overall():
    s1 = _make_raw_video(200, 30)
    s2 = _make_raw_video(600, 30)

    _compute_virality_scores([s1, s2])

    assert s1.channel_avg_views == pytest.approx(400)
    assert s1.virality_score == pytest.approx(0.5)


def test_compute_scores_unknown_duration_uses_overall():
    long = _make_raw_video(1000, 600)
    unknown = _make_raw_video(3000, 0)   # duration not available

    _compute_virality_scores([long, unknown])

    overall_avg = (1000 + 3000) / 2
    assert unknown.channel_avg_views == pytest.approx(overall_avg)
