from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class Profile:
    niche: str
    target_audience: str
    content_style: str
    ai_provider: str = "gemini"
    virality_threshold: float = 2.0
    months_back: int = 4
    content_type: str = "both"  # longform | shorts | both


@dataclass
class Config:
    profile: Profile
    creators: list[str]
    youtube_api_key: str
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None


def load_config(
    profile_path: Path = Path("profile.yml"),
    creators_path: Path = Path("creators.yml"),
) -> Config:
    load_dotenv()

    if not profile_path.exists():
        raise FileNotFoundError(
            f"'{profile_path}' not found. Copy profile.example.yml → profile.yml and fill it in."
        )
    if not creators_path.exists():
        raise FileNotFoundError(
            f"'{creators_path}' not found. Copy creators.example.yml → creators.yml and fill it in."
        )

    with open(profile_path) as f:
        raw_profile = yaml.safe_load(f)

    with open(creators_path) as f:
        raw_creators = yaml.safe_load(f)

    profile = Profile(
        niche=raw_profile["niche"],
        target_audience=raw_profile["target_audience"],
        content_style=raw_profile["content_style"],
        ai_provider=raw_profile.get("ai_provider", "gemini").lower(),
        virality_threshold=float(raw_profile.get("virality_threshold", 2.0)),
        months_back=int(raw_profile.get("months_back", 4)),
        content_type=raw_profile.get("content_type", "both").lower(),
    )

    creators: list[str] = raw_creators.get("creators", [])

    youtube_api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not youtube_api_key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY is not set. Add it to your .env file (see .env.example)."
        )

    return Config(
        profile=profile,
        creators=creators,
        youtube_api_key=youtube_api_key,
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
    )
