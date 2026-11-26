#!/usr/bin/env python3
"""
Global pytest configuration and fixtures.
Provides proper mocking for yt_dlp.YoutubeDL used in downloader.core.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def mock_yt_dlp(monkeypatch):
    """
    Mock yt_dlp.YoutubeDL where it's USED (downloader.core.yt_dlp),
    not where it's defined.
    """
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = {
        "id": "test123",
        "title": "Test Video",
        "duration": 120,
        "formats": [{"format_id": "22", "ext": "mp4", "height": 720, "vcodec": "avc1", "acodec": "mp4a"}],
    }
    mock_ydl_instance.download.return_value = None
    mock_ydl_instance.__enter__ = MagicMock(return_value=mock_ydl_instance)
    mock_ydl_instance.__exit__ = MagicMock(return_value=False)

    # Patch where yt_dlp is imported and used in downloader.core
    monkeypatch.setattr("downloader.core.yt_dlp.YoutubeDL", lambda *a, **k: mock_ydl_instance)

    return mock_ydl_instance


@pytest.fixture
def mock_yt_dlp_failing(monkeypatch):
    """Mock yt_dlp that raises an exception on extract_info."""
    def _make_mock(exception):
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = exception
        mock_ydl_instance.download.return_value = None
        mock_ydl_instance.__enter__ = MagicMock(return_value=mock_ydl_instance)
        mock_ydl_instance.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr("downloader.core.yt_dlp.YoutubeDL", lambda *a, **k: mock_ydl_instance)
        return mock_ydl_instance

    return _make_mock


@pytest.fixture
def mock_yt_dlp_download_failing(monkeypatch):
    """Mock yt_dlp that raises an exception on download."""
    def _make_mock(exception):
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {
            "id": "test",
            "formats": [{"format_id": "22", "ext": "mp4", "height": 720, "vcodec": "avc1", "acodec": "mp4a"}],
        }
        mock_ydl_instance.download.side_effect = exception
        mock_ydl_instance.__enter__ = MagicMock(return_value=mock_ydl_instance)
        mock_ydl_instance.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr("downloader.core.yt_dlp.YoutubeDL", lambda *a, **k: mock_ydl_instance)
        return mock_ydl_instance

    return _make_mock


@pytest.fixture
def mock_no_auto_deps(monkeypatch):
    """Mock system dependency checks to pass."""
    monkeypatch.setattr("deps.system.check_python_deps", lambda: True)
    monkeypatch.setattr("deps.system.check_ytdlp_version", lambda: None)
    monkeypatch.setattr("deps.system.check_system_deps", lambda *a, **k: True)


@pytest.fixture(autouse=True)
def reset_network_report():
    """Reset network error report before each test."""
    from downloader.network import reset_network_report
    reset_network_report()
    yield
    reset_network_report()


# Sample URLs for testing
@pytest.fixture
def yt_url() -> str:
    return "https://youtu.be/M19Hrft1iTE?si=ndbciHEySbz9O-vB"


@pytest.fixture
def itg_url() -> str:
    return "https://www.instagram.com/p/DeYnts9ALjH/?mdxt=MXF4cGlreHgxYXQwag=="


@pytest.fixture
def fb_url() -> str:
    return "https://www.facebook.com/reel/test_video/"


@pytest.fixture
def tw_url() -> str:
    return "https://x.com/user/status/1234567890123456789"