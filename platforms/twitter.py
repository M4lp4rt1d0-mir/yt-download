"""Twitter/X platform implementation with rate limit handling."""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from platforms.base import PlatformInfo, PlatformProtocol, PlatformBase, register_platform
from downloader.core import run_download, extract_info_flat
from downloader.formats import FormatOptions, build_ydl_opts, detect_playlist
from cli.output import print_warning, print_info

if TYPE_CHECKING:
    from cli.args import Args


@register_platform
class TwitterPlatform(PlatformBase):
    """Twitter/X downloader (tweets, spaces) with rate limit handling."""

    info = PlatformInfo(
        name="TW",
        display_name="Twitter/X",
        url_patterns=[
            "twitter.com",
            "x.com",
            "t.co",
        ],
        default_output_dir="twitter_downloads",
        video_subdir="Videos",
        audio_subdir="Audios",
    )

    def detect_url(self, url: str) -> bool:
        """Check if URL belongs to Twitter/X."""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.info.url_patterns)

    def prepare_opts(self, args: Args, url: str) -> dict[str, Any]:
        """Prepare base yt-dlp options for Twitter/X."""
        # Check for playlist
        info = extract_info_flat(url)
        is_playlist, playlist_title = detect_playlist(info)

        opts: dict[str, Any] = {
            "ignoreerrors": False,
            "quiet": False,
            "noplaylist": False,
            "windowsfilenames": True,
            "js_runtimes": {"node": {}},
            # Twitter-specific: add delay to avoid rate limits
            "sleep_interval": 1,
            "max_sleep_interval": 5,
        }

        # Handle cookies if provided (optional for Twitter)
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
        """Execute Twitter/X download with rate limit handling."""
        # Extract playlist info
        playlist_info = opts.pop("_playlist_info", {})
        fmt_opts.is_playlist = playlist_info.get("is_playlist", False)
        fmt_opts.playlist_title = playlist_info.get("title")

        # Build final options
        ydl_opts = build_ydl_opts(opts, fmt_opts)

        # Twitter/X often has rate limits - retry with exponential backoff
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            success, error = run_download(url, ydl_opts, output_path, max_attempts=1)
            if success:
                return True, ""

            error_lower = error.lower()
            # Check for rate limit errors
            if any(term in error_lower for term in ["rate limit", "too many requests", "429"]):
                if attempt < max_attempts:
                    wait_time = 2 ** attempt  # 2, 4, 8 seconds
                    print_warning(f"Rate limit detectado. Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
                    continue
                print_warning("Limite de taxa do Twitter/X atingido. Tente novamente mais tarde.")
            return False, error

        return False, ""