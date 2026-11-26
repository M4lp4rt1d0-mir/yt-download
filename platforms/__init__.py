"""Platform package - auto-registers all platform implementations."""

from __future__ import annotations

# Import all platforms to trigger @register_platform decorator
from platforms import youtube, instagram, facebook, twitter  # noqa: F401
from platforms.base import (
    PlatformInfo,
    PlatformProtocol,
    get_platform,
    list_platforms,
    detect_platform_from_url,
    register_platform,
)

__all__ = [
    "PlatformInfo",
    "PlatformProtocol",
    "get_platform",
    "list_platforms",
    "detect_platform_from_url",
    "register_platform",
]