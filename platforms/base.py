"""Base protocol for platform downloaders."""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from cli.args import Args
    from downloader.formats import FormatOptions


@dataclass
class PlatformInfo:
    """Metadata about a platform."""
    name: str
    display_name: str
    url_patterns: list[str]
    default_output_dir: str
    video_subdir: str
    audio_subdir: str


@runtime_checkable
class PlatformBase(Protocol):
    """Base protocol with common platform functionality."""

    info: PlatformInfo

    def get_default_output_dir(self) -> str:
        """Return default output directory name."""
        return self.info.default_output_dir

    def get_subdirs(self, audio_only: bool) -> tuple[str, str]:
        """Return (video_subdir, audio_subdir)."""
        return (self.info.video_subdir, self.info.audio_subdir)


@runtime_checkable
class PlatformProtocol(PlatformBase, Protocol):
    """Protocol that all platform implementations must follow."""

    info: PlatformInfo

    @abstractmethod
    def detect_url(self, url: str) -> bool:
        """Check if this platform handles the given URL."""
        ...

    @abstractmethod
    def prepare_opts(self, args: Args, url: str) -> dict:
        """Prepare yt-dlp options for this platform/URL."""
        ...

    @abstractmethod
    def download(
        self,
        url: str,
        opts: dict,
        output_path: Path,
        fmt_opts: FormatOptions,
    ) -> tuple[bool, str]:
        """Execute the download. Returns (success, error)."""
        ...


# Registry for auto-discovery
_PLATFORM_REGISTRY: dict[str, type[PlatformProtocol]] = {}


def register_platform(cls: type[PlatformProtocol]) -> type[PlatformProtocol]:
    """Decorator to register a platform implementation."""
    _PLATFORM_REGISTRY[cls.info.name] = cls
    return cls


def get_platform(name: str) -> type[PlatformProtocol] | None:
    """Get platform class by name (e.g., 'YT', 'ITG', 'FB', 'TW')."""
    return _PLATFORM_REGISTRY.get(name.upper())


def list_platforms() -> list[str]:
    """List all registered platform names."""
    return list(_PLATFORM_REGISTRY.keys())


def detect_platform_from_url(url: str) -> str | None:
    """Auto-detect platform from URL."""
    for name, cls in _PLATFORM_REGISTRY.items():
        # Create temporary instance to check
        instance = cls()
        if instance.detect_url(url):
            return name
    return None


__all__ = [
    "PlatformInfo",
    "PlatformBase",
    "PlatformProtocol",
    "get_platform",
    "list_platforms",
    "detect_platform_from_url",
    "register_platform",
]