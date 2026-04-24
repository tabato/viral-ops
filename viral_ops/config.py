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
            f"Can't find '{profile_path}'.\n\n"
            "  Run this to create it:\n"
            "    cp templates/profile.example.yml profile.yml\n\n"
            "  Then open profile.yml and fill in your niche, audience, and content style."
        )
    if not creators_path.exists():
        raise FileNotFoundError(
            f"Can't find '{creators_path}'.\n\n"
            "  Run this to create it:\n"
            "    cp templates/creators.example.yml creators.yml\n\n"
            "  Then open creators.yml and add the YouTube channels you want to scan.\n"
            "  Example:\n"
            "    creators:\n"
            '      - "@AlexHormozi"\n'
            '      - "@danmartell"'
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

    if not creators:
        raise ValueError(
            "Your creators.yml has no channels in it!\n\n"
            "  Open creators.yml and add at least one YouTube channel, like this:\n\n"
            "    creators:\n"
            '      - "@AlexHormozi"\n'
            '      - "@danmartell"\n\n'
            "  You can use a channel handle (starts with @) or a channel ID.\n"
            "  Not sure which channels to add? Check templates/creators.example.yml for ideas."
        )

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
