from viral_ops.gallery import _fmt_views


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
