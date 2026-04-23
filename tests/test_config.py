from pathlib import Path

import pytest

from viral_ops.config import load_config


def test_missing_profile_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="profile"):
        load_config(
            profile_path=tmp_path / "nonexistent_profile.yml",
            creators_path=tmp_path / "creators.yml",
        )


def test_missing_creators_raises(tmp_path):
    profile = tmp_path / "profile.yml"
    profile.write_text(
        "niche: test\ntarget_audience: testers\ncontent_style: direct\n"
    )
    with pytest.raises(FileNotFoundError, match="creators"):
        load_config(
            profile_path=profile,
            creators_path=tmp_path / "nonexistent_creators.yml",
        )
