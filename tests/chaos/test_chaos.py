#!/usr/bin/env python3
"""
Chaos Tests - Testes de quebra intencional.
Devem falhar graciosamente com mensagens claras (não crash com traceback).
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch, MagicMock

import pytest

# Adiciona raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import main
from downloader.network import report_network_error, reset_network_report
import yt_dlp


def _make_mock_ydl(monkeypatch, extract_info_result=None, extract_info_exception=None, download_exception=None):
    """Create a mock yt_dlp.YoutubeDL instance with specified behavior."""
    mock_ydl_instance = MagicMock()
    
    if extract_info_exception:
        mock_ydl_instance.extract_info.side_effect = extract_info_exception
    else:
        mock_ydl_instance.extract_info.return_value = extract_info_result or {
            "id": "test",
            "formats": [{"format_id": "22", "ext": "mp4", "height": 720, "vcodec": "avc1", "acodec": "mp4a"}],
        }
    
    if download_exception:
        mock_ydl_instance.download.side_effect = download_exception
    else:
        mock_ydl_instance.download.return_value = None
    
    mock_ydl_instance.__enter__ = MagicMock(return_value=mock_ydl_instance)
    mock_ydl_instance.__exit__ = MagicMock(return_value=False)
    
    monkeypatch.setattr("downloader.core.yt_dlp.YoutubeDL", lambda *a, **k: mock_ydl_instance)
    return mock_ydl_instance


def _make_mock_ydl_both_fail(monkeypatch, exception):
    """Create a mock that fails on both extract_info and download."""
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.side_effect = exception
    mock_ydl_instance.download.side_effect = exception
    mock_ydl_instance.__enter__ = MagicMock(return_value=mock_ydl_instance)
    mock_ydl_instance.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("downloader.core.yt_dlp.YoutubeDL", lambda *a, **k: mock_ydl_instance)
    return mock_ydl_instance


# =============================================================================
# CHAOS TEST 1: REDE OFFLINE (socket.gaierror)
# =============================================================================

class TestChaosNetworkOffline:
    """Simula falha de DNS/conexão (socket.gaierror)."""

    def test_socket_gaierror_on_extract_info(self, mock_no_auto_deps, monkeypatch):
        """gaierror ao extrair info deve dar mensagem amigável e falhar no download."""
        _make_mock_ydl_both_fail(monkeypatch, socket.gaierror(-3, "Temporary failure in name resolution"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_socket_gaierror_on_download(self, mock_no_auto_deps, monkeypatch):
        """gaierror durante download deve dar mensagem amigável."""
        _make_mock_ydl(monkeypatch, download_exception=socket.gaierror(-3, "Temporary failure"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_network_error_reporting(self):
        """report_network_error detecta erros de rede."""
        reset_network_report()

        # gaierror
        assert report_network_error("socket.gaierror: [Errno -3] Temporary failure") is True
        assert report_network_error("gaierror: Name or service not known") is True
        assert report_network_error("Connection refused") is True
        assert report_network_error("Connection timed out") is True
        assert report_network_error("Network is unreachable") is True
        assert report_network_error("No route to host") is True

        # Erro não-rede
        assert report_network_error("HTTP Error 404: Not Found") is False
        assert report_network_error("Video unavailable") is False


# =============================================================================
# CHAOS TEST 2: URL INVÁLIDA
# =============================================================================

class TestChaosInvalidURL:
    """Testes com URLs malformadas ou não suportadas."""

    def test_completely_invalid_url(self, mock_no_auto_deps, capsys):
        """URL completamente inválida."""
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'not-a-url-at-all']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_url_wrong_platform(self, mock_no_auto_deps, capsys):
        """URL de plataforma não suportada."""
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://vimeo.com/123456']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_empty_url(self, mock_no_auto_deps):
        """URL vazia."""
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_malformed_youtube_url(self, mock_no_auto_deps, capsys, monkeypatch):
        """URL YouTube malformada - deve falhar na extração de info e no download."""
        _make_mock_ydl_both_fail(monkeypatch, yt_dlp.utils.ExtractorError("Unable to extract video ID"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtube.com/watch?v=']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output


# =============================================================================
# CHAOS TEST 3: COOKIE EXPIRADO/INVÁLIDO
# =============================================================================

class TestChaosExpiredCookie:
    """Testes com cookies expirados ou inválidos."""

    def test_invalid_browser_cookie(self, mock_no_auto_deps, capsys, monkeypatch):
        """Cookie de navegador inválido."""
        _make_mock_ydl_both_fail(monkeypatch, yt_dlp.utils.ExtractorError("Sign in to confirm your age"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '--cookies', 'chrome', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_expired_cookie_file(self, mock_no_auto_deps, capsys, monkeypatch, tmp_path):
        """Arquivo de cookie expirado."""
        cookie_file = tmp_path / "expired_cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n.expired.com\tTRUE\t/\tFALSE\t0\tname\tvalue\n")

        _make_mock_ydl_both_fail(monkeypatch, yt_dlp.utils.ExtractorError("Cookies expired"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '--cookie-file', str(cookie_file), 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_private_video_without_auth(self, mock_no_auto_deps, capsys, monkeypatch):
        """Vídeo privado sem autenticação."""
        _make_mock_ydl_both_fail(monkeypatch, yt_dlp.utils.ExtractorError("This video is private"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/private']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output


# =============================================================================
# CHAOS TEST 4: RATE LIMIT SIMULADO (HTTP 429)
# =============================================================================

class TestChaosRateLimit:
    """Testes de rate limiting (HTTP 429)."""

    def test_http_429_on_extract_info(self, mock_no_auto_deps, capsys, monkeypatch):
        """HTTP 429 ao extrair metadados."""
        _make_mock_ydl_both_fail(monkeypatch, yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_http_429_on_download(self, mock_no_auto_deps, capsys, monkeypatch):
        """HTTP 429 durante download."""
        _make_mock_ydl(monkeypatch, download_exception=yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_rate_limit_retry_exhausted(self, mock_no_auto_deps, capsys, monkeypatch):
        """Rate limit após retries esgotados."""
        call_count = {"count": 0}

        def fail_then_succeed(*args, **kwargs):
            call_count["count"] += 1
            if call_count["count"] <= 3:
                raise yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests")
            return None

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"id": "test", "formats": [{"format_id": "22", "ext": "mp4"}]}
        mock_ydl_instance.download.side_effect = fail_then_succeed
        mock_ydl_instance.__enter__ = MagicMock(return_value=mock_ydl_instance)
        mock_ydl_instance.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr("downloader.core.yt_dlp.YoutubeDL", lambda *a, **k: mock_ydl_instance)

        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code in (0, 1)

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output


# =============================================================================
# CHAOS TEST 5: ARQUIVO .PART CORROMPIDO
# =============================================================================

class TestChaosCorruptedPartFile:
    """Testes com arquivos .part corrompidos."""

    def test_corrupted_part_file_cleanup(self, mock_no_auto_deps, capsys, monkeypatch, tmp_path):
        """Arquivo .part corrompido deve ser limpo ou reportado."""
        part_file = tmp_path / "test_video.f22.part"
        part_file.write_bytes(b"corrupted partial data")

        _make_mock_ydl(monkeypatch, download_exception=yt_dlp.utils.DownloadError("Unable to resume: corrupted .part file"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '-o', str(tmp_path), 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_orphan_part_file_handling(self, mock_no_auto_deps, capsys, monkeypatch, tmp_path):
        """Arquivo .part órfão (sem download em andamento)."""
        for i in range(3):
            (tmp_path / f"video_{i}.f22.part").write_bytes(b"orphan")

        _make_mock_ydl(monkeypatch)
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '-o', str(tmp_path), 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_partial_download_interruption(self, mock_no_auto_deps, capsys, monkeypatch, tmp_path):
        """Interrupção durante download deixa .part."""
        part_file = tmp_path / "video.f22.part"
        part_file.write_bytes(b"partial" * 1000)

        def simulate_interrupt(*args, **kwargs):
            raise yt_dlp.utils.DownloadError("Connection reset by peer")

        _make_mock_ydl(monkeypatch, download_exception=simulate_interrupt)
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '-o', str(tmp_path), 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output


# =============================================================================
# CHAOS TESTS ADICIONAIS: EDGE CASES
# =============================================================================

class TestChaosEdgeCases:
    """Casos extremos adicionais."""

    def test_ffmpeg_missing(self, mock_no_auto_deps, capsys):
        """FFmpeg não instalado."""
        with patch("deps.system.check_system_deps", return_value=False):
            with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output
        assert "ffmpeg" in output.lower() or "dependência" in output.lower()

    def test_yt_dlp_outdated_warning(self, mock_no_auto_deps, capsys):
        """yt-dlp desatualizado (>90 dias)."""
        with patch("deps.system.check_ytdlp_version") as mock_check:
            mock_check.side_effect = None
            with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '--changelog']):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_permission_denied_output_dir(self, mock_no_auto_deps, capsys, monkeypatch, tmp_path):
        """Sem permissão no diretório de saída."""
        import os
        if os.name == 'nt':
            pytest.skip("Permission test not reliable on Windows")

        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()
        restricted_dir.chmod(0o000)

        try:
            _make_mock_ydl(monkeypatch, download_exception=PermissionError("Permission denied"))
            with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', '-o', str(restricted_dir), 'https://youtu.be/test']):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
        finally:
            restricted_dir.chmod(0o755)

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_disk_full_simulation(self, mock_no_auto_deps, capsys, monkeypatch):
        """Simulação de disco cheio."""
        _make_mock_ydl(monkeypatch, download_exception=OSError("No space left on device"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output

    def test_keyboard_interrupt(self, mock_no_auto_deps, monkeypatch):
        """Interrupção por Ctrl+C."""
        _make_mock_ydl_both_fail(monkeypatch, KeyboardInterrupt())
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code in (1, 130)

    def test_memory_error(self, mock_no_auto_deps, capsys, monkeypatch):
        """Erro de memória (simulado)."""
        _make_mock_ydl(monkeypatch, download_exception=MemoryError("Out of memory"))
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Traceback" not in output


# =============================================================================
# VALIDAÇÃO DE MENSAGENS AMIGÁVEIS
# =============================================================================

class TestFriendlyErrorMessages:
    """Valida que mensagens de erro são amigáveis (sem traceback)."""

    # Network errors get specific friendly messages
    NETWORK_SCENARIOS = [
        ("network_dns", socket.gaierror(-3, "Temporary failure"), ["rede", "internet", "conexão", "dns", "endereço"]),
        ("network_timeout", socket.timeout("Connection timed out"), ["tempo limite", "timeout", "conexão", "conectar"]),
    ]

    # Non-network errors get generic message
    GENERIC_SCENARIOS = [
        ("invalid_url", ValueError("Invalid URL")),
        ("private_video", yt_dlp.utils.ExtractorError("Video is private")),
        ("age_gate", yt_dlp.utils.ExtractorError("Sign in to confirm age")),
        ("rate_limit", yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests")),
        ("corrupted_part", yt_dlp.utils.DownloadError("corrupted .part file")),
        ("ffmpeg_missing", FileNotFoundError("ffmpeg not found")),
    ]

    @pytest.mark.parametrize("scenario_name,exception,expected_keywords", NETWORK_SCENARIOS)
    def test_friendly_message_for_network_error(self, scenario_name, exception, expected_keywords, mock_no_auto_deps, capsys, monkeypatch):
        """Erros de rede devem produzir mensagem amigável específica sem traceback."""
        _make_mock_ydl_both_fail(monkeypatch, exception)
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = (captured.out + captured.err).lower()

        assert "traceback" not in output, f"{scenario_name}: Traceback found in output"

        has_keyword = any(kw in output for kw in expected_keywords)
        assert has_keyword, f"{scenario_name}: Expected one of {expected_keywords} in output. Got: {output[:200]}"

    @pytest.mark.parametrize("scenario_name,exception", GENERIC_SCENARIOS)
    def test_generic_message_for_other_errors(self, scenario_name, exception, mock_no_auto_deps, capsys, monkeypatch):
        """Erros não-rede devem produzir mensagem genérica sem traceback."""
        _make_mock_ydl_both_fail(monkeypatch, exception)
        with patch.object(sys, 'argv', ['main.py', '--no-auto-deps', 'https://youtu.be/test']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = (captured.out + captured.err).lower()

        assert "traceback" not in output, f"{scenario_name}: Traceback found in output"
        # Deve ter mensagem genérica de falha
        assert "download não concluído" in output or "não concluído" in output, f"{scenario_name}: Expected generic failure message. Got: {output[:200]}"


# =============================================================================
# EXECUÇÃO DIRETA
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])