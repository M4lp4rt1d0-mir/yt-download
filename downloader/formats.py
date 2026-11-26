"""Format selection and output template utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platforms.base import PlatformBase


@dataclass
class FormatOptions:
    """Format configuration for a download."""
    audio_only: bool
    resolution: str  # e.g., "1080p", "720p"
    output_path: Path
    subdir: str  # e.g., "Videos", "Audios", "Instagram_audios"
    is_playlist: bool = False
    playlist_title: str | None = None


def build_ydl_opts(base_opts: dict, fmt: FormatOptions) -> dict:
    """Build complete yt-dlp options from base + format options."""
    opts = dict(base_opts)

    # Output template
    output_path_clean = str(fmt.output_path).replace("\\", "/")
    if fmt.is_playlist and fmt.playlist_title:
        out_template = (
            f"{output_path_clean}/{fmt.playlist_title}/"
            f"%(playlist_index)02d - %(title)s.%(ext)s"
        )
    else:
        out_template = f"{output_path_clean}/{fmt.subdir}/%(title)s.%(ext)s"
    opts["outtmpl"] = out_template

    # Format selection
    if fmt.audio_only:
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        res_limit = fmt.resolution.replace("p", "")
        opts.update({
            "format": (
                f"bestvideo[height<={res_limit}][ext=mp4]"
                f"+bestaudio[ext=m4a]/best[ext=mp4]/best"
            ),
            "merge_output_format": "mp4",
        })

    return opts


def detect_playlist(info: dict | None) -> tuple[bool, str | None]:
    """Detect if URL is a multi-item playlist."""
    if not info or info.get("_type") != "playlist":
        return False, None
    entries = info.get("entries", [])
    try:
        entry_list = list(entries)
    except TypeError:
        entry_list = []
    if len(entry_list) > 1:
        return True, info.get("title")
    return False, None


def get_platform_subdirs(platform: str, audio_only: bool) -> tuple[str, str]:
    """
    Return (video_subdir, audio_subdir) for a platform.
    """
    if platform == "ITG":
        return "Videos", "Instagram_audios"
    elif platform == "FB":
        return "Videos", "Audios"
    elif platform == "TW":
        return "Videos", "Audios"
    else:  # YT
        return "Videos", "Audios"