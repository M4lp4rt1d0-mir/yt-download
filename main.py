#!/usr/bin/env python3
"""Main entry point for the modular downloader."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.args import parse_args, print_help, print_changelog
from cli.output import print_info, print_success, print_error, print_warning
from config.store import forget_auth
from deps.system import check_python_deps, install_python_deps, check_ytdlp_version, check_system_deps
from platforms import get_platform, detect_platform_from_url, list_platforms


def main() -> None:
    args = parse_args()

    # Handle special flags first
    if args.changelog:
        print_changelog()
        sys.exit(0)

    if args.url is None:
        print_help()
        sys.exit(0)

    if args.forget_cookies:
        forget_auth(args.platform)
        print_success("Configuração de cookies removida.")
        sys.exit(0)

    # Check Python dependencies
    if not args.no_auto_deps:
        if not check_python_deps():
            install_python_deps()
    else:
        # Still verify imports work
        try:
            import yt_dlp
        except ImportError as e:
            print_error(f"Falha ao importar yt-dlp: {e}")
            print_error("Execute sem --no-auto-deps ou instale manualmente: pip install yt-dlp")
            sys.exit(1)

    check_ytdlp_version()

    # Determine platform
    platform_name = args.platform
    if platform_name == "AUTO" or not platform_name:
        detected = detect_platform_from_url(args.url)
        if detected:
            platform_name = detected
            print_info(f"Plataforma detectada automaticamente: {platform_name}")
        else:
            platform_name = "YT"
            print_warning(f"Não foi possível detectar a plataforma. Usando padrão: {platform_name}")

    platform_cls = get_platform(platform_name)
    if not platform_cls:
        print_error(f"Plataforma desconhecida: {platform_name}")
        print_error(f"Plataformas disponíveis: {', '.join(list_platforms())}")
        sys.exit(1)

    platform = platform_cls()

    # Determine output directory
    output_dir = args.output or platform.get_default_output_dir()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    # Check system dependencies
    if not check_system_deps(args):
        print_error("O script não pode continuar sem as dependências do sistema.")
        print_error("Execute 'installer/install_deps.bat' (Windows) ou 'installer/install_deps.sh' (Linux)")
        sys.exit(1)

    # Prepare options
    opts = platform.prepare_opts(args, args.url)

    # Build format options
    from downloader.formats import FormatOptions, get_platform_subdirs
    video_subdir, audio_subdir = get_platform_subdirs(platform_name, args.audio)
    fmt_opts = FormatOptions(
        audio_only=args.audio,
        resolution=args.resolution,
        output_path=output_path,
        subdir=audio_subdir if args.audio else video_subdir,
    )

    # Execute download
    success, error = platform.download(args.url, opts, output_path, fmt_opts)

    if success:
        # Save auth for Instagram (and other platforms if they implement it)
        if args.platform == "ITG":
            if args.cookie_file:
                from config.store import remember_auth
                remember_auth("ITG", {"cookie_file": str(Path(args.cookie_file).resolve())})
            elif args.cookies:
                from config.store import remember_auth
                remember_auth("ITG", {"browser": args.cookies})
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()