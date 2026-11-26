"""YouTube platform implementation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from platforms.base import PlatformInfo, PlatformProtocol, PlatformBase, register_platform
from downloader.core import run_download, extract_info_flat
from downloader.formats import FormatOptions, build_ydl_opts, detect_playlist

if TYPE_CHECKING:
    from cli.args import Args


@register_platform
class YouTubePlatform(PlatformBase):
    """YouTube downloader using yt-dlp with Android client."""

    info = PlatformInfo(
        name="YT",
        display_name="YouTube",
        url_patterns=[
            "youtube.com",
            "youtu.be",
            "youtube-nocookie.com",
        ],
        default_output_dir="Youtube_Downloads",
        video_subdir="Videos",
        audio_subdir="Audios",
    )

    def detect_url(self, url: str) -> bool:
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.info.url_patterns)

    def prepare_opts(self, args: Args, url: str) -> dict:
        """Prepare base yt-dlp options for YouTube."""
        # Check for playlist
        info = extract_info_flat(url)
        is_playlist, playlist_title = detect_playlist(info)

        opts = {
            "ignoreerrors": False,
            "quiet": False,
            "noplaylist": False,
            "windowsfilenames": True,
            "js_runtimes": {"node": {}},
            "extractor_args": {"youtube": {"player_client": ["android"]}},
            "remote_components": ["ejs:github"],
        }

        # Handle cookies
        if args.cookies:
            opts["cookiesfrombrowser"] = (args.cookies,)
        if args.cookie_file:
            opts["cookiefile"] = args.cookie_file

        # Store playlist info for format building
        opts["_playlist_info"] = {"is_playlist": is_playlist, "title": playlist_title}
        return opts

    def download(
        self,
        url: str,
        opts: dict,
        output_path: Path,
        fmt_opts: FormatOptions,
    ) -> tuple[bool, str]:
        """Execute YouTube download."""
        # Extract playlist info from opts
        playlist_info = opts.pop("_playlist_info", {})
        fmt_opts.is_playlist = playlist_info.get("is_playlist", False)
        fmt_opts.playlist_title = playlist_info.get("title")

        # Build final options
        ydl_opts = build_ydl_opts(opts, fmt_opts)

        return run_download(url, ydl_opts, output_path)