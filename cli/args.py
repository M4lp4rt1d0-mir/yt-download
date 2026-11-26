"""Argument parsing and help text."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from platforms import list_platforms, detect_platform_from_url

if TYPE_CHECKING:
    from cli.output import VERMELHO, VERDE, AMARELO, AZUL, RESET

# Lazy imports for colors to avoid circular deps


def _get_colors() -> tuple[str, str, str, str, str]:
    """Get color codes lazily to avoid circular imports."""
    from cli.output import VERMELHO, VERDE, AMARELO, AZUL, RESET
    return VERMELHO, VERDE, AMARELO, AZUL, RESET


@dataclass
class Args:
    """Parsed command line arguments."""

    url: str | None
    resolution: str
    output: str | None
    audio: bool
    platform: str
    cookies: str | None
    cookie_file: str | None
    forget_cookies: bool
    changelog: bool
    no_auto_deps: bool


BROWSERS_SUPORTADOS = ["chrome", "edge", "firefox", "vivaldi", "opera", "safari"]
PLATFORM_CHOICES = list_platforms() + ["AUTO"]  # ["YT", "ITG", "FB", "TW", "AUTO"]


def build_instructions() -> str:
    """Build the usage instructions string."""
    VERMELHO, VERDE, AMARELO, AZUL, RESET = _get_colors()

    from platforms import get_platform
    platform_list = ", ".join(
        f"{p} ({get_platform(p).info.display_name})"
        for p in PLATFORM_CHOICES if p != "AUTO"
    )

    return f"""{AMARELO}#########################################################################################################
                                           MANUAL DE USO
#########################################################################################################{RESET}
{VERDE}===========================================================================================================
| Parâmetro   | Nome Completo          | Descrição                                   | Padrão (Default)   |
===========================================================================================================
| url         | URL (VIDEOS)           | Link do vídeo ou da playlist.               | Obrigatório        |
|             |                        | (SEMPRE USE ASPAS DUPLAS "")                |                    |
|-------------|------------------------|---------------------------------------------|--------------------|
| -r          | --resolution           | Define a resolução máxima do                | 1080p              |
|             |                        | vídeo (ex: 1080p, 720p, 480p).              |                    |
|-------------|------------------------|---------------------------------------------|--------------------|
| -o          | --output               | Nome da pasta onde o arquivo será salvo.    | Por plataforma     |
|             |                        | (padrão varia por plataforma)               |                    |
|-------------|------------------------|---------------------------------------------|--------------------|
| -a          | --audio                | Flag que ativa o modo econômico. Baixa      | Desativado         |
|             |                        | apenas o áudio e converte em MP3.           |                    |
|-------------|------------------------|---------------------------------------------|--------------------|
| -p          | --platform             | Plataforma: {platform_list} | AUTO (detectar)    |
|-------------|------------------------|---------------------------------------------|--------------------|
| --cookies   | --cookies              | Lê cookies de um navegador logado           | Desativado         |
|             |                        | (chrome, firefox, edge, opera, safari,      |                    |
|             |                        | vivaldi). Ex: --cookies vivaldi             |                    |
|-------------|------------------------|---------------------------------------------|--------------------|
| --cookie-file | --cookie-file        | Caminho de um arquivo de cookies (.txt).    | Desativado         |
|-------------|------------------------|---------------------------------------------|--------------------|
| --forget-cookies | --forget-cookies  | Esquece o cookie/navegador salvo.           | Desativado         |
|-------------|------------------------|---------------------------------------------|--------------------|
| --no-auto-deps | --no-auto-deps      | Não instalar dependências Python automaticamente | Desativado      |
===========================================================================================================

{AMARELO}NOTA: Se o Instagram pedir login, o script segue 3 passos:
  1) tenta os cookies do navegador que estiver aberto;
  2) se não der certo, pergunta qual navegador você usa;
  3) se você não souber, procura arquivos de cookies automaticamente.
Também é possível passar --cookies ou --cookie-file para pular a pergunta.
Após um download bem-sucedido, a escolha é salva e reutilizada nas próximas
execuções (use --forget-cookies para limpar).

Se o YouTube devolver HTTP 403 (URL de mídia expirada), o script apaga o
trecho baixado e tenta novamente até 3 vezes antes de avisar o erro.{RESET}

{VERDE}Exemplos de execução (Vídeo YouTube):{RESET}
    python main.py -r 1080p -o "C:\\Users\\SEU_USUARIO\\Downloads" "https://www.youtube.com/watch?v=EXEMPLO"

{VERDE}Exemplos de execução (Áudio YouTube):{RESET}
    python main.py "https://www.youtube.com/watch?v=EXEMPLO" -a -o "C:\\Users\\SEU_USUARIO\\Downloads"

{VERDE}Exemplos de execução (Instagram - Reels/Post):{RESET}
    python main.py "https://instagram.com/reel/EXEMPLO" -p ITG -r 720p

{VERDE}Exemplos de execução (Instagram - Áudio):{RESET}
    python main.py "https://instagram.com/p/EXEMPLO" -p ITG -a

{VERDE}Exemplos de execução (Facebook - Reels/Post):{RESET}
    python main.py "https://facebook.com/reel/EXEMPLO" -p FB -r 720p

{VERDE}Exemplos de execução (Twitter/X - Tweet):{RESET}
    python main.py "https://x.com/user/status/EXEMPLO" -p TW -r 720p

----------------------------------------------------------------------
@author: sis.marcosxavier@gmail.com
Github: https://github.com/marcosxavierdev
@author: sbrennopqd@gmail.com
Github: https://github.com/M4lp4rt1d0-mir
{AZUL}Use --changelog para consultar o histórico de versões.{RESET}

{AZUL}@version: 1.7.0{RESET}
====================================================================================================="""


def build_changelog() -> str:
    """Build the changelog string."""
    VERMELHO, VERDE, AMARELO, AZUL, RESET = _get_colors()

    return f"""{AZUL}=====================================================================
HISTÓRICO DE VERSÕES - main.py
====================================================================={RESET}

{AZUL}ORIGEM DO PROJETO{RESET}
  + Criado em 07/04/2026 por S. Brenno (Python) e pelo marido da sua prima (Java),
    inicialmente apenas por diversão. De brincadeira ao downloader modular atual.

{VERDE}[1.7.0] - 25/11/2026{RESET}
  + Adicionado: Suporte para Facebook (-p FB) e Twitter/X (-p TW)
  + Adicionado: Nova arquitetura modular (cli/, config/, deps/, downloader/, platforms/)
  + Adicionado: install_deps.bat (Windows) e install_deps.sh (Linux) para dependências de sistema
  + Adicionado: Flag --no-auto-deps para desativar instalação automática de pacotes Python
  + Adicionado: Detecção de erros de conexão (sem internet / site fora do ar) com
    mensagem clara na leitura de metadados, no download e na instalação do yt-dlp
  + Alterado: Refatoração completa mantendo compatibilidade total com YT e ITG
  + Corrigido: Organização de pastas por plataforma (FB: facebook_downloads, TW: twitter_downloads)
  + Corrigido: Mensagem de conclusão para todas as plataformas (YT, ITG, FB e TW),
    com pasta dos arquivos e aviso claro em caso de falha
  + Corrigido: Mensagem do Instagram centralizada no main.py (sem duplicação)
  + Corrigido: Cookies do Instagram também são salvos quando a plataforma é detectada automaticamente (AUTO)

{VERDE}[1.6.4] - 25/11/2026{RESET}
  + Adicionado: requirements.txt com yt-dlp>=2026.03.17 e notas sobre
    FFmpeg/Node.js (dependências externas, não instaladas via pip).

{VERDE}[1.6.3] - 25/11/2026{RESET}
  + Adicionado: changelog integrado e flag --changelog (funciona no executável).
  + Manual: agora informa como consultar o histórico.

{VERDE}[1.6.2] - 25/11/2026{RESET}
  + Corrigido: extractor_args do YouTube passou para o formato aceito pela API
    do yt-dlp (player_client=android). O cliente android_vr era ignorado e
    causava HTTP 403 após ~10 MB.
  + Corrigido: mesmo ajuste aplicado ao scan inicial, que disparava erro do
    solvedor de JS antes do download.
  + Alterado: cliente android puro passou a usar o formato 18 (MP4 completo).
  + Removido: arquivo .part órfão do formato 399 deixado pela versão anterior.

{VERDE}[1.6.1] - 25/11/2026{RESET}
  + Adicionado: retry automático (3 tentativas) em HTTP 403, limpando
    arquivos .part/.ytdl antes de cada nova tentativa.
  + Adicionado: aviso quando o yt-dlp estiver desatualizado (>90 dias).
  + Corrigido: erro 403 do YouTube deixou de ser exibido como
    "conteúdo privado/indisponível".

{VERDE}[1.6.0] - 25/11/2026{RESET}
  + Adicionado: script combinado main_combined.py, sem alterar o main.py original.
  + Adicionado: flag -p/--platform (YT ou Instagram), padrão YT.
  + Adicionado: pastas automáticas por plataforma:
      YouTube  -> Youtube_Downloads/Videos e Youtube_Downloads/Audios
      Instagram-> instagram_downloads/Videos e instagram_downloads/Instagram_audios
  + Adicionado: tratativa para Stories e conteúdo privado do Instagram.
  + Adicionado: fluxo de cookies do Instagram em 3 etapas:
      detectar navegador aberto -> perguntar ao usuário -> procurar arquivos
      de cookie; a escolha é salva para reutilização.
  + Adicionado: flags --cookies, --cookie-file e --forget-cookies.
  + Alterado: ignoreerrors=False para não imprimir sucesso quando o download falha.

{VERDE}[1.4.6] - data não registrada{RESET}
  + Versão do downloader original apenas de YouTube (main.py), preservada
    como referência e não modificada.

{VERDE}[1.0.0] - data não registrada{RESET}
  + Primeira versão registrada do projeto (youtube_downloader.py).

{AZUL}Fim do histórico.{RESET}
====================================================================="""


def parse_args(argv: list[str] | None = None) -> Args:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Baixa vídeos (MP4) ou áudios (MP3) do YouTube, Instagram, Facebook ou Twitter/X. Suporte a Playlists.",
        epilog="Exemplo: python main.py \"URL\" -p ITG -a",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Get default platform from URL if possible (handled later)
    parser.add_argument("url", nargs="?", default=None, help="URL do vídeo ou playlist (SEMPRE USE ASPAS).")
    parser.add_argument("-r", "--resolution", default="1080p",
                        help="Resolução máxima do vídeo (ex: 720p, 1080p)")
    parser.add_argument("-o", "--output", default=None,
                        help="Pasta base de saída (padrão varia por plataforma).")
    parser.add_argument("-a", "--audio", action="store_true", help="Baixar somente áudio em MP3.")
    parser.add_argument("-p", "--platform", choices=PLATFORM_CHOICES, default="AUTO",
                        help=f"Plataforma: {', '.join(PLATFORM_CHOICES)} (padrão: AUTO = detectar pela URL)")
    parser.add_argument("--cookies", default=None, metavar="BROWSER",
                        choices=BROWSERS_SUPORTADOS,
                        help="Usar cookies do navegador logado (ex: chrome, vivaldi) — RISCO DE BLOQUEIO")
    parser.add_argument("--cookie-file", default=None, metavar="CAMINHO",
                        help="Caminho para arquivo de cookies (.txt ou .json) do navegador.")
    parser.add_argument("--forget-cookies", action="store_true",
                        help="Esquece o cookie/navegador salvo para a plataforma.")
    parser.add_argument("--changelog", action="store_true",
                        help="Mostra o histórico de versões e sai.")
    parser.add_argument("--no-auto-deps", action="store_true",
                        help="Não instalar dependências Python automaticamente.")

    parsed = parser.parse_args(argv)

    return Args(
        url=parsed.url,
        resolution=parsed.resolution,
        output=parsed.output,
        audio=parsed.audio,
        platform=parsed.platform.upper(),
        cookies=parsed.cookies,
        cookie_file=parsed.cookie_file,
        forget_cookies=parsed.forget_cookies,
        changelog=parsed.changelog,
        no_auto_deps=parsed.no_auto_deps,
    )


def print_help() -> None:
    """Print the usage instructions."""
    from cli.output import print_info
    print_info(build_instructions())


def print_changelog() -> None:
    """Print the changelog."""
    from cli.output import print_info
    print_info(build_changelog())