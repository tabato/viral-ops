from viral_ops.gallery import _fmt_views, _rank_badge


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
