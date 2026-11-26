"""System dependency checks and installation."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from cli.output import print_info, print_success, print_error, print_warning

if TYPE_CHECKING:
    from cli.args import Args


REQUIRED_PACKAGES = {
    "yt-dlp": "yt_dlp",
}


def check_python_deps() -> bool:
    """Check if required Python packages are installed."""
    print_info("Verificando pacotes Python do script...")
    all_ok = True
    for package_name, import_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
            print(f"  [OK] '{package_name}' já está instalado.")
        except ImportError:
            print_warning(f"Pacote '{package_name}' não encontrado.")
            all_ok = False
    return all_ok


def install_python_deps() -> None:
    """Install missing Python packages via pip."""
    for package_name, import_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            print_warning(f"Instalando '{package_name}'...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name, "--quiet"]
                )
                print_success(f"Pacote '{package_name}' instalado.")
            except subprocess.CalledProcessError:
                print_error(f"Falha ao instalar '{package_name}'.")
                sys.exit(1)
    print_success("Dependências Python atualizadas.\n")


def check_ytdlp_version() -> None:
    """Warn if yt-dlp is older than 90 days."""
    try:
        import datetime
        import yt_dlp.version
        partes = yt_dlp.version.__version__.split(".")[:3]
        if len(partes) == 3:
            release_date = datetime.date(int(partes[0]), int(partes[1]), int(partes[2]))
            age = (datetime.date.today() - release_date).days
            if age > 90:
                print_warning(
                    f"yt-dlp {yt_dlp.version.__version__} tem {age} dias. "
                    f"Considere atualizar: python -m pip install -U yt-dlp"
                )
    except Exception:
        pass


def _check_ffmpeg() -> bool:
    """Check if FFmpeg is available."""
    if shutil.which("ffmpeg"):
        print(f"  [OK] FFmpeg encontrado no sistema.")
        return True
    return False


def _check_nodejs() -> bool:
    """Check if Node.js is available."""
    if shutil.which("node"):
        print(f"  [OK] Node.js encontrado no sistema.")
        return True
    return False


def _run_system_installer() -> bool:
    """Run the platform-specific system dependency installer."""
    project_root = Path(__file__).parent.parent
    if sys.platform.startswith("win"):
        installer = project_root / "installer" / "install_deps.bat"
        if not installer.is_file():
            print_error(f"Instalador não encontrado: {installer}")
            return False
        print_info("Executando instalador de dependências do Windows...")
        try:
            subprocess.run([str(installer)], check=False, shell=True)
            return True
        except Exception as e:
            print_error(f"Falha ao executar instalador: {e}")
            return False
    else:
        installer = project_root / "installer" / "install_deps.sh"
        if not installer.is_file():
            print_error(f"Instalador não encontrado: {installer}")
            return False
        print_info("Executando instalador de dependências do Linux...")
        try:
            subprocess.run(["bash", str(installer)], check=False)
            return True
        except Exception as e:
            print_error(f"Falha ao executar instalador: {e}")
            return False


def check_system_deps(args: Args | None = None) -> bool:
    """
    Check all system dependencies (FFmpeg, Node.js).
    If missing and auto-install is enabled, prompt and run installer.
    Returns True if all dependencies are available.
    """
    no_auto_deps = getattr(args, "no_auto_deps", False)

    # Check current status
    has_ffmpeg = _check_ffmpeg()
    has_nodejs = _check_nodejs()

    if has_ffmpeg and has_nodejs:
        return True

    missing = []
    if not has_ffmpeg:
        missing.append("FFmpeg")
    if not has_nodejs:
        missing.append("Node.js")

    if no_auto_deps:
        print_error(f"Dependências de sistema ausentes: {', '.join(missing)}")
        print_error("Use --no-auto-deps para pular a instalação automática, mas instale manualmente:")
        print_error("  FFmpeg: https://www.gyan.dev/ffmpeg/builds/ (Windows) ou gerenciador de pacotes (Linux)")
        print_error("  Node.js LTS: https://nodejs.org/")
        return False

    print_warning(f"Dependências ausentes: {', '.join(missing)}")
    try:
        resp = input("Instalar automaticamente? [S/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        resp = "n"

    if resp in ("", "s", "sim", "y", "yes"):
        if _run_system_installer():
            print_info("Re-verificando dependências após instalação...")
            has_ffmpeg = _check_ffmpeg()
            has_nodejs = _check_nodejs()
            if has_ffmpeg and has_nodejs:
                print_success("Todas as dependências de sistema estão disponíveis.")
                return True
            else:
                still_missing = []
                if not has_ffmpeg:
                    still_missing.append("FFmpeg")
                if not has_nodejs:
                    still_missing.append("Node.js")
                print_error(f"Dependências ainda ausentes: {', '.join(still_missing)}")
                print_error("Instale manualmente e tente novamente.")
                return False
        else:
            print_error("Falha na instalação automática.")
            return False
    else:
        print_error("Instalação cancelada. As dependências de sistema são obrigatórias.")
        return False