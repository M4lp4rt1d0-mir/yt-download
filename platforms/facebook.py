"""Facebook platform implementation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from platforms.base import PlatformInfo, PlatformProtocol, PlatformBase, register_platform
from downloader.core import run_download, extract_info_flat
from downloader.formats import FormatOptions, build_ydl_opts, detect_playlist

if TYPE_CHECKING:
    from cli.args import Args


@register_platform
class FacebookPlatform(PlatformBase):
    """Facebook downloader (reels, posts, watch)."""

    info = PlatformInfo(
        name="FB",
        display_name="Facebook",
        url_patterns=[
            "facebook.com",
            "fb.watch",
            "fb.com",
        ],
        default_output_dir="facebook_downloads",
        video_subdir="Videos",
        audio_subdir="Audios",
    )

    def detect_url(self, url: str) -> bool:
        """Check if URL belongs to Facebook."""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.info.url_patterns)

    def prepare_opts(self, args: Args, url: str) -> dict[str, Any]:
        """Prepare base yt-dlp options for Facebook."""
        # Check for playlist
        info = extract_info_flat(url)
        is_playlist, playlist_title = detect_playlist(info)

        opts: dict[str, Any] = {
            "ignoreerrors": False,
            "quiet": False,
            "noplaylist": False,
            "windowsfilenames": True,
            "js_runtimes": {"node": {}},
        }

        # Handle cookies if provided
        if args.cookies:
            opts["cookiesfrombrowser"] = (args.cookies,)
        if args.cookie_file:
            opts["cookiefile"] = args.cookie_file

        opts["_playlist_info"] = {"is_playlist": is_playlist, "title": playlist_title}
        return opts

    def download(
        self,
        url: str,
        opts: dict[str, Any],
        output_path: Path,
        fmt_opts: FormatOptions,
    ) -> tuple[bool, str]:
        """Execute Facebook download."""
        # Extract playlist info
        playlist_info = opts.pop("_playlist_info", {})
        fmt_opts.is_playlist = playlist_info.get("is_playlist", False)
        fmt_opts.playlist_title = playlist_info.get("title")

        # Build final options
        ydl_opts = build_ydl_opts(opts, fmt_opts)

        return run_download(url, ydl_opts, output_path)