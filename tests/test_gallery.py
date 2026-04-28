from pathlib import Path
from unittest.mock import patch

from viral_ops.gallery import _fmt_views, _rank_badge, _download_thumbnails


def test_fmt_views_under_1k():
    assert _fmt_views(0) == "0"
    assert _fmt_views(999) == "999"


def test_fmt_views_thousands():
    assert _fmt_views(1_000) == "1K"
    assert _fmt_views(10_000) == "10K"
    assert _fmt_views(500_000) == "500K"


def test_fmt_views_millions():
    assert _fmt_views(1_000_000) == "1.0M"
    assert _fmt_views(2_500_000) == "2.5M"
    assert _fmt_views(10_000_000) == "10.0M"


# ------------------------------------------------------------------
# _rank_badge
# ------------------------------------------------------------------

def test_rank_badge_first_has_crown():
    badge = _rank_badge(1)
    assert "crown" in badge
    assert "👑" in badge
    assert "rank-1" in badge

def test_rank_badge_second_is_silver():
    badge = _rank_badge(2)
    assert "rank-2" in badge
    assert "👑" not in badge

def test_rank_badge_third_is_bronze():
    badge = _rank_badge(3)
    assert "rank-3" in badge
    assert "👑" not in badge

def test_rank_badge_other_is_plain():
    for rank in [4, 5, 10, 99]:
        badge = _rank_badge(rank)
        assert "rank-1" not in badge
        assert "rank-2" not in badge
        assert "rank-3" not in badge
        assert f"#{rank}" in badge


# ------------------------------------------------------------------
# _download_thumbnails
# ------------------------------------------------------------------

def test_download_thumbnails_success(tmp_path):
    def fake_download(url, dest):
        dest.write_bytes(b"img")
        return True

    items = [
        ("vid1", "http://example.com/1.jpg", tmp_path / "vid1.jpg", "Video One"),
        ("vid2", "http://example.com/2.jpg", tmp_path / "vid2.jpg", "Video Two"),
    ]
    with patch("viral_ops.gallery._download", side_effect=fake_download):
        result = _download_thumbnails(items, tmp_path)

    assert result == {
        "vid1": "thumbnails/vid1.jpg",
        "vid2": "thumbnails/vid2.jpg",
    }


def test_download_thumbnails_partial_failure(tmp_path):
    def fake_download(url, dest):
        if "fail" in url:
            return False
        dest.write_bytes(b"img")
        return True

    items = [
        ("ok",   "http://example.com/ok.jpg",   tmp_path / "ok.jpg",   "Good"),
        ("fail", "http://example.com/fail.jpg",  tmp_path / "fail.jpg", "Bad"),
    ]
    with patch("viral_ops.gallery._download", side_effect=fake_download):
        result = _download_thumbnails(items, tmp_path)

    assert "ok" in result
    assert "fail" not in result


def test_download_thumbnails_empty(tmp_path):
    result = _download_thumbnails([], tmp_path)
    assert result == {}


def test_download_thumbnails_all_downloaded(tmp_path):
    calls = []

    def fake_download(url, dest):
        calls.append(url)
        dest.write_bytes(b"x")
        return True

    items = [(f"v{i}", f"http://x/{i}.jpg", tmp_path / f"v{i}.jpg", f"T{i}") for i in range(5)]
    with patch("viral_ops.gallery._download", side_effect=fake_download):
        result = _download_thumbnails(items, tmp_path)

    assert len(result) == 5
    assert len(calls) == 5
