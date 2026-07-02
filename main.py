import sys
import subprocess
import os
import shutil


REQUIRED_PACKAGES = {
    'yt-dlp': 'yt_dlp',
    'curl-cffi': 'curl_cffi'
}


VERMELHO = '\033[91m'
VERDE = '\033[92m'
AMARELO = '\033[93m'
AZUL = '\033[94m'
RESET = '\033[0m'

INSTRUCOES = f"""{AMARELO}#########################################################################################################
                                         MANUAL DE USO
#########################################################################################################{RESET}
{VERDE}=========================================================================================================
| Parâmetro   | Nome Completo          | Descrição                                | Padrão (Default)    |
=========================================================================================================
| url         | URL (VIDEOS)           | Link do vídeo ou da playlist.            | Obrigatório         |
|             |                        | (SEMPRE USE ASPAS DUPLAS "")             |                     |
|-------------|------------------------|------------------------------------------|---------------------|
| -r          | --resolution           | Define a resolução máxima do             | 1080p               |
|             |                        | vídeo (ex: 1080p, 720p, 480p).           |                     |
|-------------|------------------------|------------------------------------------|---------------------|
| -o          | --output_path          | Nome da pasta onde o arquivo será salvo. | Youtube_Downloads   |
|             |                        | (Não utilize espaços no nome!)           |                     |
|-------------|------------------------|------------------------------------------|---------------------|
| -a          | --audio_only           | Flag que ativa o modo econômico. Baixa   | Desativado          |
|             |                        | apenas o áudio e converte em MP3.        |                     |
========================================================================================================={RESET}

{VERDE}Exemplos de execução (Vídeo):{RESET}
    python main.py -r 1080p -o C:\"Users\SEU_USUARIO\Downloads "https://www.youtube.com/watch?v=EXEMPLO"

{VERDE}Exemplos de execução (Áudio):{RESET}
    python main.py "https://www.youtube.com/watch?v=EXEMPLO" -a -o C:\"Users\SEU_USUARIO\Downloads

{VERDE}Exemplos de execução (Playlist - vídeo):{RESET}
    python main.py "https://www.youtube.com/playlist?list=EXEMPLO" -r 480p

{VERDE}Exemplos de execução (Playlist - Áudio):{RESET}
    python main.py -a "https://www.youtube.com/playlist?list=EXEMPLO"

----------------------------------------------------------------------
@author: sis.marcosxavier@gmail.com
Github: https://github.com/marcosxavierdev
@author: sbrennopqd@gmail.com
Github: https://github.com/M4lp4rt1d0-mir
{AZUL}@version: 1.4.6{RESET}
======================================================================
"""


def install_python_dependencies():
    print(f"{AZUL}Verificando pacotes Python do script...{RESET}")
    is_ready = True
    for package_name, import_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
            print(f"  [OK] '{package_name}' já está instalado.")
        except ImportError:
            print(f"  {AMARELO}[AVISO] Pacote '{package_name}' não encontrado. Instalando...{RESET}")
            is_ready = False
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "--quiet"])
                print(f"  {VERDE}[SUCESSO] Pacote '{package_name}' instalado.{RESET}")
            except subprocess.CalledProcessError:
                print(f"  {VERMELHO}[ERRO] Falha ao instalar '{package_name}'.{RESET}")
                sys.exit(1)
    if not is_ready:
        print(f"\n{VERDE}Dependências Python atualizadas.{RESET}\n")


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        print(f"  [OK] FFmpeg encontrado no sistema.")
        return True
    else:
        print(f"\n  {AMARELO}[AVISO] FFmpeg não encontrado. Iniciando instalação automática...{RESET}")
        if sys.platform.startswith("linux"):
            print(f"  {AZUL}O sistema pode pedir sua senha (sudo) para instalar pacotes do Linux.{RESET}")
            try:
                subprocess.check_call("sudo apt update && sudo apt install ffmpeg -y", shell=True)
                print(f"  {VERDE}[SUCESSO] FFmpeg instalado corretamente!{RESET}")
                return True
            except subprocess.CalledProcessError:
                print(f"  {VERMELHO}[ERRO] Falha na instalação automática do FFmpeg.{RESET}")
                return False
        else:
            print(f"  {VERMELHO}[ERRO] Auto-instalação suportada apenas no Linux. Instale o FFmpeg manualmente.{RESET}")
            return False


def check_nodejs():
    if shutil.which("node") or shutil.which("nodejs"):
        print(f"  [OK] Node.js encontrado no sistema.")
        return True
    else:
        print(f"\n  {AMARELO}[AVISO] Node.js não encontrado. Iniciando instalação automática (Versão 20)...{RESET}")
        if sys.platform.startswith("linux"):
            print(f"  {AZUL}O sistema pode pedir sua senha (sudo) para instalar pacotes do Linux.{RESET}")
            try:
                cmd = "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs"
                subprocess.check_call(cmd, shell=True)
                print(f"  {VERDE}[SUCESSO] Node.js instalado corretamente!{RESET}")
                return True
            except subprocess.CalledProcessError:
                print(f"  {VERMELHO}[ERRO] Falha na instalação automática do Node.js.{RESET}")
                return False
        else:
            print(f"  {VERMELHO}[ERRO] Auto-instalação suportada apenas no Linux. Instale o Node.js manualmente.{RESET}")
            return False


def download_media(url, resolution, output_path, audio_only):
    res_limit = resolution.replace('p', '')
    pasta = "Audios" if audio_only else "Videos"
    output_path_clean = output_path.replace('\\', '/')

    out_template = f"{output_path_clean}/{pasta}/%(title)s.%(ext)s"

    print(f"{AZUL}Analisando o link para organizar as pastas...{RESET}")

    try:
        import yt_dlp
        check_opts = {
            'extract_flat': True,
            'quiet': True,
            'ignoreerrors': True,
            'js_runtimes': {'node': {}},
        }
        with yt_dlp.YoutubeDL(check_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info and info.get('_type') == 'playlist':
                entries = info.get('entries', [])
                if entries and len(list(entries)) > 1:
                    print(f"{VERDE}Playlist com múltiplas músicas detectada! Criando pasta própria...{RESET}")
                    out_template = f"{output_path_clean}/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"
                else:
                    print(f"{AMARELO}Playlist de item único detectada. Salvando em '{pasta}'...{RESET}")
            else:
                print(f"{AMARELO}Vídeo avulso detectado! Salvando em '{pasta}'...{RESET}")

    except Exception as e:
        print(f"{AMARELO}Aviso: Não foi possível escanear o link ({e}). Usando pasta padrão...{RESET}")

    ydl_opts: dict = {
        'outtmpl': out_template,
        'ignoreerrors': True,
        'quiet': False,
        'noplaylist': False,
        'windowsfilenames': True,
        'js_runtimes': {'node': {}},
        'extractor_args': {'youtube': ['player_client=android,ios']},
        'remote_components': ['ejs:github'],
    }

    if audio_only:
        print(f"\n{AMARELO}Modo: Somente Áudio (MP3) de Playlist/Vídeo{RESET}")
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        print(f"\n{AMARELO}Modo: Vídeo (MP4) de Playlist/Vídeo - Resolução máxima: {resolution}{RESET}")
        ydl_opts.update({
            'format': f'bestvideo[height<={res_limit}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4'
        })

    try:
        import yt_dlp
        print(f"{AZUL}\nIniciando o yt-dlp...{RESET}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n{VERDE}Processo concluído com sucesso! Verifique a pasta base: {output_path}{RESET}")
    except Exception as e:
        print(f"\n{VERMELHO}Erro durante o processamento: {e}{RESET}")


def main():
    if len(sys.argv) == 1:
        print(INSTRUCOES)
        sys.exit(0)

    install_python_dependencies()

    try:
        import yt_dlp
    except ImportError as e:
        print(f"\n{VERMELHO}[ERRO] Falha ao importar bibliotecas: {e}{RESET}")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description="Baixa vídeos (MP4) ou áudios (MP3) do YouTube. Suporta Playlists.",
                                     epilog="Exemplo: python youtube_downloader.py \"URL\" -a")
    parser.add_argument("url", help="URL do vídeo ou playlist (SEMPRE USE ASPAS).")
    parser.add_argument("-r", "--resolution", default="1080p",
                        help="Resolução máxima do vídeo (ex: 720p, 1080p)")
    parser.add_argument("-o", "--output", default="Youtube_Downloads",
                        help="Pasta base de saída.")
    parser.add_argument("-a", "--audio", action="store_true", help="Baixar somente áudio em MP3.")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if not check_ffmpeg() or not check_nodejs():
        print(f"\n{VERMELHO}O script não pode continuar sem as dependências do sistema.{RESET}")
        sys.exit(1)

    download_media(args.url, args.resolution, args.output, args.audio)


if __name__ == "__main__":
    main()