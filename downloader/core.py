"""Core download logic with retry and cleanup."""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yt_dlp

from cli.output import print_info, print_warning
from downloader.network import report_network_error

if TYPE_CHECKING:
    from downloader.formats import FormatOptions


def cleanup_partial_files(output_path: str | Path) -> None:
    """Remove .part/.ytdl files to avoid resuming with expired URLs."""
    path = Path(output_path)
    if not path.is_dir():
        return
    removed = 0
    for pattern in ("*.part", "*.ytdl"):
        for file_path in path.glob(f"**/{pattern}"):
            try:
                file_path.unlink()
                removed += 1
            except OSError:
                pass
    if removed:
        print_warning(f"Removidos {removed} arquivo(s) parcial(is) para nova tentativa.")


def run_download(
    url: str,
    ydl_opts: dict[str, Any],
    output_path: str | Path,
    max_attempts: int = 3,
) -> tuple[bool, str]:
    """
    Execute download with retry on HTTP 403.
    Returns (success, error_message).
    """
    for attempt in range(1, max_attempts + 1):
        try:
            if attempt == 1:
                print_info("\nIniciando o yt-dlp...")
            else:
                print_info(f"\nNova tentativa ({attempt}/{max_attempts})...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True, ""

        except Exception as e:
            error = str(e)
            is_403 = "403" in error or "forbidden" in error.lower()
            if attempt < max_attempts and is_403:
                print_warning(
                    f"HTTP 403 na tentativa {attempt}/{max_attempts}: "
                    f"URL expirada ou bloqueada — limpando parciais e retentando..."
                )
                cleanup_partial_files(output_path)
                continue
            report_network_error(error)
            return False, error

    return False, ""


def extract_info_flat(url: str, ydl_opts: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Extract info without downloading (for playlist detection)."""
    opts: dict[str, Any] = {
        "extract_flat": True,
        "quiet": True,
        "ignoreerrors": True,
        "js_runtimes": {"node": {}},
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    if ydl_opts:
        opts.update(ydl_opts)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        report_network_error(e)
        return None