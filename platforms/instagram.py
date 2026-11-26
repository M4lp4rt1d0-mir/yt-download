"""Instagram platform implementation with 3-step auth flow."""

from __future__ import annotations

import glob
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from config.store import (
    get_saved_auth,
    remember_auth,
    validate_cookie_file,
    CONFIG_PATH,
)
from platforms.base import PlatformInfo, PlatformProtocol, PlatformBase, register_platform
from downloader.core import run_download, extract_info_flat
from downloader.formats import FormatOptions, build_ydl_opts, detect_playlist
from cli.output import (
    print_info, print_success, print_warning, print_error,
    VERDE, AMARELO, AZUL, VERMELHO, RESET,
)

if TYPE_CHECKING:
    from cli.args import Args


BROWSERS_SUPORTADOS = ["chrome", "edge", "firefox", "vivaldi", "opera", "safari"]


def _is_auth_error(message: str) -> bool:
    """Detect errors indicating need for login/cookies."""
    text = str(message).lower()
    triggers = [
        "login required", "login", "rate-limit", "rate limit",
        "requested content is not available", "not available",
        "private", "cookie", "403", "401", "authentication",
    ]
    return any(t in text for t in triggers)


def _detect_running_browsers() -> list[str]:
    """Detect running browsers and return supported names."""
    mapping = {
        "chrome": "chrome",
        "msedge": "edge",
        "firefox": "firefox",
        "vivaldi": "vivaldi",
        "opera": "opera",
        "safari": "safari",
    }
    found = []
    try:
        if sys.platform.startswith("win"):
            output = subprocess.check_output(
                ["tasklist"], text=True, errors="ignore",
                stderr=subprocess.DEVNULL,
            ).lower()
            for exe, name in mapping.items():
                if f"{exe}.exe" in output and name not in found:
                    found.append(name)
        else:
            for name in mapping.values():
                try:
                    subprocess.check_output(
                        ["pgrep", "-x", name], stderr=subprocess.DEVNULL
                    )
                    if name not in found:
                        found.append(name)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
    except Exception:
        pass
    return found


def _find_cookie_candidates(extra_dirs: list[str] | None = None) -> list[str]:
    """Search for cookie files in likely locations."""
    patterns = [
        "cookies*.txt", "*cookie*.txt", "cookies*.json", "*cookie*.json",
        "instagram*.txt", "*instagram*cookie*", "*.cookies",
    ]

    home = Path.home()
    folders = [
        Path(__file__).parent.parent.parent,
        Path.cwd(),
        home / "Downloads",
        home / "Desktop",
        home / "Documents",
        home / "AppData" / "Local" / "Temp",
    ]
    if extra_dirs:
        folders.extend(Path(d) for d in extra_dirs)

    found = []
    seen = set()
    for folder in folders:
        if not folder or not folder.is_dir():
            continue
        for pattern in patterns:
            for path in folder.glob(pattern):
                abs_path = path.resolve()
                if abs_path.is_file() and abs_path not in seen:
                    seen.add(abs_path)
                    found.append(str(abs_path))
            for path in folder.glob(f"*/{pattern}"):
                abs_path = path.resolve()
                if abs_path.is_file() and abs_path not in seen:
                    seen.add(abs_path)
                    found.append(str(abs_path))
        if len(found) >= 30:
            break
    return found[:30]


def _opts_with_auth(base_opts: dict, escolha: dict) -> dict:
    """Apply auth choice to yt-dlp options."""
    opts = dict(base_opts)
    opts.pop("cookiesfrombrowser", None)
    opts.pop("cookiefile", None)
    if escolha.get("browser"):
        opts["cookiesfrombrowser"] = (escolha["browser"],)
    elif escolha.get("cookie_file"):
        opts["cookiefile"] = escolha["cookie_file"]
    return opts


def _ask_browser_choice(detected: list[str] | None = None) -> dict | None:
    """Step 2: ask user which browser they use."""
    print(f"\n{AMARELO}{'=' * 72}{RESET}")
    print(f"{AMARELO}Não consegui baixar automaticamente.{RESET}")
    print(f"{AMARELO}Qual navegador você usa para acessar o Instagram?{RESET}")
    print(f"{AMARELO}{'=' * 72}{RESET}")

    for i, browser in enumerate(BROWSERS_SUPORTADOS, start=1):
        mark = " (aberto agora)" if detected and browser in detected else ""
        print(f"  [{i}] {browser}{mark}")
    print(f"  [{AZUL}0{RESET}] Não sei — procurar arquivo de cookies automaticamente")
    print(f"  [{AZUL}c{RESET}] Informar o caminho de um arquivo de cookies")
    print(f"  Pressione {AZUL}Enter{RESET} para cancelar")

    while True:
        try:
            resp = input(f"\n{VERDE}Sua escolha: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if resp == "":
            return None

        if resp == "0":
            return {"hunt": True}

        if resp.lower() == "c":
            try:
                path = input(f"{VERDE}Caminho do arquivo: {RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                return None
            path = path.strip('"').strip("'")
            if os.path.isfile(path):
                return {"cookie_file": os.path.abspath(path)}
            print(f"{VERMELHO}Arquivo não encontrado: {path}{RESET}")
            continue

        if resp.isdigit():
            idx = int(resp) - 1
            if 0 <= idx < len(BROWSERS_SUPORTADOS):
                return {"browser": BROWSERS_SUPORTADOS[idx]}

        print(f"{VERMELHO}Opção inválida.{RESET}")


def _hunt_cookie_files() -> dict | None:
    """Step 3: hunt for cookie files automatically."""
    print(f"\n{AZUL}Procurando arquivos de cookies nos locais mais prováveis...{RESET}")
    candidates = _find_cookie_candidates()

    if candidates:
        print(f"{VERDE}Arquivos encontrados:{RESET}")
        for i, path in enumerate(candidates, start=1):
            print(f"  [{i}] {path}")
        print(f"\nDigite o {AZUL}número{RESET}, cole o {AZUL}caminho completo{RESET} "
              f"ou pressione {AZUL}Enter{RESET} para cancelar.")
    else:
        print(f"{AMARELO}Nenhum arquivo de cookies encontrado automaticamente.{RESET}")
        print(f"Cole o {AZUL}caminho completo{RESET} de um arquivo de cookies "
              f"ou pressione {AZUL}Enter{RESET} para cancelar.")

    while True:
        try:
            resp = input(f"\n{VERDE}Sua escolha: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if resp == "":
            return None

        if resp.isdigit() and candidates:
            idx = int(resp) - 1
            if 0 <= idx < len(candidates):
                return {"cookie_file": candidates[idx]}
            print(f"{VERMELHO}Número fora da lista.{RESET}")
            continue

        path = resp.strip('"').strip("'")
        if os.path.isfile(path):
            return {"cookie_file": os.path.abspath(path)}

        print(f"{VERMELHO}Arquivo não encontrado: {path}{RESET}")


def _attempt_recovery(
    url: str,
    base_opts: dict,
    output_path: Path,
) -> bool:
    """3-step recovery flow: running browsers -> ask -> hunt files."""
    max_attempts = 4
    attempts = 0

    print(f"\n{AMARELO}{'=' * 72}{RESET}")
    print(f"{AMARELO}O Instagram pediu login. Vou tentar resolver automaticamente.{RESET}")
    print(f"{AMARELO}{'=' * 72}{RESET}")

    # Step 1: running browsers
    detected = _detect_running_browsers()
    if detected:
        print(f"{VERDE}Navegador(es) em execução detectado(s): {', '.join(detected)}{RESET}")
        print(f"{AZUL}Tentando usar os cookies desses navegadores...{RESET}")
        for browser in detected:
            if attempts >= max_attempts:
                break
            attempts += 1
            print(f"{AZUL}[{attempts}] Tentando navegador '{browser}'...{RESET}")
            escolha = {"browser": browser}
            opts = _opts_with_auth(base_opts, escolha)
            success, error = run_download(url, opts, output_path)
            if success:
                remember_auth("ITG", escolha)
                print(f"\n{VERDE}Processo concluído com sucesso! Verifique a pasta base: {output_path}{RESET}")
                return True
            print(f"{AMARELO}   Não funcionou: {error}{RESET}")
            if not _is_auth_error(error):
                print(f"{VERMELHO}O erro não parece ser de autenticação. Abortando.{RESET}")
                return False
    else:
        print(f"{AMARELO}Nenhum navegador em execução foi detectado.{RESET}")

    # Steps 2 & 3: ask and/or hunt
    while attempts < max_attempts:
        escolha = _ask_browser_choice(detected)
        if escolha is None:
            print(f"{AMARELO}Download cancelado pelo usuário.{RESET}")
            return False

        if escolha.get("hunt"):
            escolha = _hunt_cookie_files()
            if escolha is None:
                print(f"{AMARELO}Download cancelado pelo usuário.{RESET}")
                return False

        attempts += 1
        opts = _opts_with_auth(base_opts, escolha)
        if escolha.get("browser"):
            print(f"{AMARELO}[AVISO] Usando cookies do navegador '{escolha['browser']}'. "
                  f"Pode gerar bloqueio se usado em excesso!{RESET}")
        else:
            print(f"{VERDE}[OK] Usando arquivo de cookies: {escolha['cookie_file']}{RESET}")
            validate_cookie_file(escolha["cookie_file"])

        success, error = run_download(url, opts, output_path)
        if success:
            remember_auth("ITG", escolha)
            print(f"\n{VERDE}Processo concluído com sucesso! Verifique a pasta base: {output_path}{RESET}")
            return True

        print(f"{VERMELHO}Tentativa {attempts} falhou: {error}{RESET}")
        if not _is_auth_error(error):
            print(f"{VERMELHO}O erro não parece ser de autenticação. Abortando.{RESET}")
            return False

    print(f"{VERMELHO}Número máximo de tentativas atingido.{RESET}")
    return False


@register_platform
class InstagramPlatform(PlatformBase):
    """Instagram downloader with 3-step auth flow."""

    info = PlatformInfo(
        name="ITG",
        display_name="Instagram",
        url_patterns=[
            "instagram.com",
            "instagr.am",
        ],
        default_output_dir="instagram_downloads",
        video_subdir="Videos",
        audio_subdir="Instagram_audios",
    )

    def detect_url(self, url: str) -> bool:
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.info.url_patterns)

    def prepare_opts(self, args: Args, url: str) -> dict:
        """Prepare base yt-dlp options for Instagram."""
        # Block Stories
        if "/stories/" in url.lower():
            print_error("Erro: Stories não são suportados sem login. "
                        "Tentar baixar pode gerar bloqueio da conta ou exigir login manual.")
            sys.exit(1)

        # Check for playlist
        info = extract_info_flat(url)
        is_playlist, playlist_title = detect_playlist(info)

        opts = {
            "ignoreerrors": False,
            "quiet": False,
            "noplaylist": False,
            "windowsfilenames": True,
            "js_runtimes": {"node": {}},
        }

        # Handle explicit cookies from CLI
        if args.cookies:
            opts["cookiesfrombrowser"] = (args.cookies,)
        if args.cookie_file:
            opts["cookiefile"] = args.cookie_file

        opts["_playlist_info"] = {"is_playlist": is_playlist, "title": playlist_title}
        return opts

    def download(
        self,
        url: str,
        opts: dict,
        output_path: Path,
        fmt_opts: FormatOptions,
    ) -> tuple[bool, str]:
        """Execute Instagram download with auth recovery."""
        # Extract playlist info
        playlist_info = opts.pop("_playlist_info", {})
        fmt_opts.is_playlist = playlist_info.get("is_playlist", False)
        fmt_opts.playlist_title = playlist_info.get("title")

        # Build final options
        ydl_opts = build_ydl_opts(opts, fmt_opts)

        # Try initial download
        success, error = run_download(url, ydl_opts, output_path)
        if success:
            print(f"\n{VERDE}Processo concluído com sucesso! Verifique a pasta base: {output_path}{RESET}")
            return True, ""

        # Handle errors
        error_lower = error.lower()
        if "403" in error_lower or "forbidden" in error_lower:
            print(f"\n{VERMELHO}Erro HTTP 403: o servidor recusou o download após as tentativas.{RESET}")
            print(f"{AMARELO}Geralmente é URL expirada, bloqueio temporário ou região restrita — NÃO é conteúdo privado.{RESET}")
            print(f"{AMARELO}Detalhe: {error}{RESET}")
            return False, error

        if _is_auth_error(error):
            print(f"\n{VERMELHO}Erro de autenticação: {error}{RESET}")
            if _attempt_recovery(url, ydl_opts, output_path):
                return True, ""
        else:
            print(f"\n{VERMELHO}Erro: conteúdo privado/indisponível — não é possível baixar sem acesso autorizado.{RESET}")
            print(f"{AMARELO}Detalhe: {error}{RESET}")

        return False, error