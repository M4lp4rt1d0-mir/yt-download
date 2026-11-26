#!/usr/bin/env python3
"""
QA Gate Orchestrator - Executa todos os gates de qualidade e testes.
Exit code: 0 se tudo PASS, 1 se qualquer FAIL.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def run_gate(name: str, cmd: list[str], cwd: Path) -> dict[str, Any]:
    """Executa um gate individual e retorna resultado padronizado."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.time() - start
        status = "PASS" if result.returncode == 0 else "FAIL"
        details = {
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
            "duration_seconds": round(elapsed, 2),
        }
    except subprocess.TimeoutExpired:
        status = "FAIL"
        details = {
            "returncode": -1,
            "stdout": "",
            "stderr": "Timeout after 300s",
            "duration_seconds": 300,
        }
    except Exception as e:
        status = "FAIL"
        details = {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration_seconds": round(time.time() - start, 2),
        }

    return {
        "gate": name,
        "status": status,
        "details": details,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def run_all_gates(project_root: Path) -> list[dict[str, Any]]:
    """Executa todos os gates obrigatórios."""
    gates = [
        ("ruff", ["ruff", "check", "--select=ALL", "--exit-zero=false"]),
        ("mypy", ["mypy", "--strict", "--ignore-missing-imports"]),
        ("bandit", ["bandit", "-r", ".", "-ll"]),
        ("vulture", ["vulture", "--min-confidence", "80"]),
        (
            "pytest",
            [
                "pytest",
                "-xvs",
                "--cov=downloader",
                "--cov=platforms",
                "--cov=deps",
                "--cov=config",
                "--cov=cli",
                "--cov-fail-under=80",
            ],
        ),
        ("pip-audit", ["pip-audit"]),
    ]

    results = []
    for name, cmd in gates:
        print(f"\n{'=' * 60}")
        print(f"Running gate: {name}")
        print(f"{'=' * 60}")
        result = run_gate(name, cmd, project_root)
        results.append(result)
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {name}: {result['status']} ({result['details']['duration_seconds']}s)")
        if result["status"] == "FAIL":
            print(f"   stderr: {result['details']['stderr'][:500]}")

    return results


def run_smoke_tests(project_root: Path) -> list[dict[str, Any]]:
    """Executa smoke tests mockados (validar que CLI não crashe)."""
    print(f"\n{'=' * 60}")
    print("Running smoke tests (mocked)")
    print(f"{'=' * 60}")

    smoke_tests = [
        ("smoke_yt", "YT", "https://youtu.be/M19Hrft1iTE?si=ndbciHEySbz9O-vB"),
        ("smoke_itg", "ITG", "https://www.instagram.com/p/DeYnts9ALjH/?mdxt=MXF4cGlreHgxYXQwag=="),
        ("smoke_fb", "FB", "https://www.facebook.com/reel/test/"),
        ("smoke_tw", "TW", "https://x.com/user/status/123456789"),
    ]

    results = []
    for name, platform, url in smoke_tests:
        start = time.time()
        # Mock: apenas validar que o CLI parseia args e não crashe no início
        # Usamos --no-auto-deps e --changelog para evitar downloads reais
        cmd = [
            sys.executable,
            "main.py",
            "--no-auto-deps",
            "--platform",
            platform,
            "--changelog",  # Sai antes de tentar download
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            elapsed = time.time() - start
            # --changelog deve retornar 0
            status = "PASS" if result.returncode == 0 else "FAIL"
            details = {
                "platform": platform,
                "url": url,
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:] if result.stdout else "",
                "stderr": result.stderr[-1000:] if result.stderr else "",
                "duration_seconds": round(elapsed, 2),
            }
        except subprocess.TimeoutExpired:
            status = "FAIL"
            details = {
                "platform": platform,
                "url": url,
                "returncode": -1,
                "stdout": "",
                "stderr": "Timeout after 30s",
                "duration_seconds": 30,
            }
        except Exception as e:
            status = "FAIL"
            details = {
                "platform": platform,
                "url": url,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration_seconds": round(time.time() - start, 2),
            }

        results.append({
            "gate": name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {name} ({platform}): {status}")

    return results


def run_chaos_tests(project_root: Path) -> list[dict[str, Any]]:
    """Executa chaos tests (devem falhar graciosamente)."""
    print(f"\n{'=' * 60}")
    print("Running chaos tests (expected to fail gracefully)")
    print(f"{'=' * 60}")

    chaos_tests = [
        (
            "chaos_network_offline",
            "Rede offline (socket.gaierror)",
            ["python", "-c", """
import socket
from unittest.mock import patch
from main import main
import sys

# Simular gaierror em socket.getaddrinfo
with patch('socket.getaddrinfo', side_effect=socket.gaierror('Temporary failure in name resolution')):
    sys.argv = ['main.py', '--no-auto-deps', 'https://youtu.be/test']
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)
"""],
        ),
        (
            "chaos_invalid_url",
            "URL inválida",
            [sys.executable, "main.py", "--no-auto-deps", "not-a-valid-url"],
        ),
        (
            "chaos_expired_cookie",
            "Cookie expirado",
            [sys.executable, "main.py", "--no-auto-deps", "--cookies", "chrome", "https://youtu.be/test"],
        ),
        (
            "chaos_rate_limit",
            "Rate limit simulado (HTTP 429)",
            ["python", "-c", """
from unittest.mock import patch
from main import main
import sys
import yt_dlp

def mock_extract_info(*args, **kwargs):
    raise yt_dlp.utils.DownloadError('HTTP Error 429: Too Many Requests')

with patch('yt_dlp.YoutubeDL.extract_info', side_effect=mock_extract_info):
    sys.argv = ['main.py', '--no-auto-deps', 'https://youtu.be/test']
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)
"""],
        ),
        (
            "chaos_corrupted_part",
            "Arquivo .part corrompido",
            ["python", "-c", """
from pathlib import Path
from unittest.mock import patch
from main import main
import sys
import yt_dlp

# Criar arquivo .part corrompido
part_file = Path('test_video.part')
part_file.write_bytes(b'corrupted data')

def mock_download(*args, **kwargs):
    raise yt_dlp.utils.DownloadError('Unable to resume: corrupted .part file')

with patch('yt_dlp.YoutubeDL.download', side_effect=mock_download):
    sys.argv = ['main.py', '--no-auto-deps', 'https://youtu.be/test']
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)
finally:
    part_file.unlink(missing_ok=True)
"""],
        ),
    ]

    results = []
    for name, description, cmd in chaos_tests:
        start = time.time()
        print(f"\n  Testing: {description}")
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            elapsed = time.time() - start
            # Chaos tests devem falhar (returncode != 0) mas COM MENSAGEM CLARA
            # Verificar se stderr/stdout contém mensagem de erro amigável
            output = (result.stdout or "") + (result.stderr or "")
            friendly_keywords = [
                "conexão", "internet", "rede", "network",
                "inválida", "inválido", "invalid", "url",
                "cookie", "expirado", "expired", "login",
                "rate limit", "429", "muitas requisições",
                "corrompido", "corrupted", ".part", "resume",
            ]
            has_friendly_msg = any(kw in output.lower() for kw in friendly_keywords)
            no_crash = "Traceback" not in output and "Error:" not in output

            # PASS se: falhou (returncode != 0) E tem mensagem amigável E não crashou
            status = "PASS" if (result.returncode != 0 and has_friendly_msg and no_crash) else "FAIL"

            details = {
                "description": description,
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:] if result.stdout else "",
                "stderr": result.stderr[-1000:] if result.stderr else "",
                "has_friendly_message": has_friendly_msg,
                "no_traceback": no_crash,
                "duration_seconds": round(elapsed, 2),
            }
        except subprocess.TimeoutExpired:
            status = "FAIL"
            details = {
                "description": description,
                "returncode": -1,
                "stdout": "",
                "stderr": "Timeout after 60s",
                "has_friendly_message": False,
                "no_traceback": False,
                "duration_seconds": 60,
            }
        except Exception as e:
            status = "FAIL"
            details = {
                "description": description,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "has_friendly_message": False,
                "no_traceback": False,
                "duration_seconds": round(time.time() - start, 2),
            }

        results.append({
            "gate": name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"  {status_icon} {name}: {status}")
        if status == "FAIL":
            print(f"     Friendly msg: {details.get('has_friendly_message', False)}")
            print(f"     No traceback: {details.get('no_traceback', False)}")

    return results


def print_summary(all_results: list[dict[str, Any]]) -> None:
    """Imprime relatório final bonito."""
    print(f"\n{'=' * 60}")
    print("QA GATE REPORT")
    print(f"{'=' * 60}")

    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = total - passed

    for result in all_results:
        icon = "✅" if result["status"] == "PASS" else "❌"
        gate = result["gate"]
        status = result["status"]
        duration = result["details"].get("duration_seconds", 0)
        print(f"  {icon} {gate:<25} {status:<4} ({duration}s)")

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {total} | PASS: {passed} | FAIL: {failed}")
    print(f"{'=' * 60}")


def save_report(all_results: list[dict[str, Any]], project_root: Path) -> Path:
    """Salva relatório em qa/report_<timestamp>.json."""
    qa_dir = project_root / "qa"
    qa_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = qa_dir / f"report_{timestamp}.json"

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total": len(all_results),
            "passed": sum(1 for r in all_results if r["status"] == "PASS"),
            "failed": sum(1 for r in all_results if r["status"] == "FAIL"),
        },
        "results": all_results,
    }

    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n📄 Report saved to: {report_file}")
    return report_file


def main() -> int:
    """Main entry point for QA Gate."""
    parser = argparse.ArgumentParser(
        description="QA Gate Orchestrator - Executa todos os gates de qualidade",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/qa_gate.py              # Executa todos os gates
  python scripts/qa_gate.py --gates-only # Apenas gates (sem smoke/chaos)
  python scripts/qa_gate.py --help       # Mostra esta ajuda
        """,
    )
    parser.add_argument(
        "--gates-only",
        action="store_true",
        help="Executar apenas os gates obrigatórios (pular smoke/chaos tests)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Não salvar relatório JSON",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    print("🚀 QA Gate Orchestrator Starting...")
    print(f"📁 Project root: {project_root}")

    all_results = []

    # Gates obrigatórios
    all_results.extend(run_all_gates(project_root))

    if not args.gates_only:
        # Smoke tests
        all_results.extend(run_smoke_tests(project_root))

        # Chaos tests
        all_results.extend(run_chaos_tests(project_root))

    # Relatório
    print_summary(all_results)

    if not args.no_save:
        save_report(all_results, project_root)

    # Exit code
    has_failures = any(r["status"] == "FAIL" for r in all_results)
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())