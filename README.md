# YouTube / Instagram / Facebook / Twitter Downloader

Um downloader modular em Python para baixar vídeos (MP4) e áudios (MP3) do YouTube, Instagram, Facebook e Twitter/X. Suporte a playlists, retry automático em HTTP 403, fluxo de autenticação em 3 etapas para Instagram.

## Características

- **Multi-plataforma**: YouTube (YT), Instagram (ITG), Facebook (FB), Twitter/X (TW)
- **Formatos**: Vídeo MP4 (até 1080p/4K) ou Áudio MP3 (192 kbps)
- **Playlists**: Detecção automática e organização em pastas
- **Retry inteligente**: 3 tentativas em HTTP 403 com limpeza de arquivos parciais
- **Instagram Auth**: Fluxo de 3 etapas (navegador aberto → pergunta → caça arquivos) com cache
- **Cookies**: Suporte a `--cookies <browser>` e `--cookie-file <path>`
- **Modular**: Arquitetura limpa para fácil adição de novas plataformas

## Instalação Rápida

### Windows
```cmd
# 1. Instalar dependências de sistema (FFmpeg, Node.js)
installer\install_deps.bat

# 2. Instalar dependências Python
python -m pip install -r requirements.txt

# 3. Executar
python main.py "https://youtube.com/watch?v=EXEMPLO"
```

### Linux
```bash
# 1. Instalar dependências de sistema (FFmpeg, Node.js)
./installer/install_deps.sh

# 2. Instalar dependências Python
python3 -m pip install -r requirements.txt

# 3. Executar
python3 main.py "https://youtube.com/watch?v=EXEMPLO"
```

## Uso Básico

```bash
# YouTube vídeo (padrão)
python main.py "https://youtube.com/watch?v=VIDEO_ID"

# YouTube áudio
python main.py "https://youtube.com/watch?v=VIDEO_ID" -a

# Instagram Reels/Post
python main.py "https://instagram.com/reel/EXEMPLO" -p ITG

# Instagram áudio
python main.py "https://instagram.com/p/EXEMPLO" -p ITG -a

# Facebook Reels/Post
python main.py "https://facebook.com/reel/EXEMPLO" -p FB

# Twitter/X Tweet
python main.py "https://x.com/user/status/EXEMPLO" -p TW

# Playlist YouTube em 720p
python main.py "https://youtube.com/playlist?list=PLAYLIST_ID" -r 720p

# Especificar pasta de saída
python main.py "URL" -o "C:\Downloads\Meus_Videos"
```

## Flags Disponíveis

| Flag | Longa | Descrição | Padrão |
|------|-------|-----------|--------|
| `url` | - | URL do vídeo/playlist (use aspas) | Obrigatório |
| `-r` | `--resolution` | Resolução máxima (720p, 1080p, 480p) | `1080p` |
| `-o` | `--output` | Pasta base de saída | Por plataforma |
| `-a` | `--audio` | Apenas áudio (MP3) | Vídeo |
| `-p` | `--platform` | Plataforma: YT, ITG, FB, TW | `YT` |
| | `--cookies` | Cookies do navegador (chrome, firefox, edge, opera, safari, vivaldi) | - |
| | `--cookie-file` | Caminho para arquivo de cookies (.txt/.json) | - |
| | `--forget-cookies` | Esquecer cookies/navegador salvos | - |
| | `--changelog` | Mostrar histórico de versões | - |
| | `--no-auto-deps` | Não instalar dependências Python automaticamente | - |

## Pastas de Saída por Plataforma

| Plataforma | Vídeos | Áudios |
|------------|--------|--------|
| YouTube (YT) | `Youtube_Downloads/Videos` | `Youtube_Downloads/Audios` |
| Instagram (ITG) | `instagram_downloads/Videos` | `instagram_downloads/Instagram_audios` |
| Facebook (FB) | `facebook_downloads/Videos` | `facebook_downloads/Audios` |
| Twitter/X (TW) | `twitter_downloads/Videos` | `twitter_downloads/Audios` |

## Autenticação Instagram

Para contas privadas ou conteúdo restrito:

1. **Automático**: Deixe o navegador (Chrome, Edge, Firefox, etc.) aberto e logado no Instagram
2. **Interativo**: O script pergunta qual navegador você usa
3. **Arquivo**: Forneça `--cookie-file caminho/cookies.txt` ou `--cookies chrome`

A escolha bem-sucedida é salva em `~/.main_combined_config.json` para reutilização.

Use `--forget-cookies` para limpar.

## Dependências de Sistema

O script **não** instala FFmpeg ou Node.js via pip. Use os instaladores incluídos:

- **Windows**: `installer/install_deps.bat` (usa winget/Chocolatey)
- **Linux**: `installer/install_deps.sh` (detecta apt/dnf/pacman/zypper/apk)

Ou instale manualmente:
- **FFmpeg**: https://www.gyan.dev/ffmpeg/builds/ (Windows) / gerenciador de pacotes (Linux)
- **Node.js LTS**: https://nodejs.org/

## Estrutura do Projeto

```
project/
├── main.py                     # Entry point (~30 linhas)
├── cli/
│   ├── args.py                 # argparse, help, --changelog
│   └── output.py               # Cores, prints formatados
├── config/
│   └── store.py                # JSON config, cookies Instagram
├── deps/
│   └── system.py               # check_system_deps(), instaladores
├── downloader/
│   ├── core.py                 # _run_download, retry 403, cleanup
│   └── formats.py              # Resolução, format strings, merge
├── platforms/
│   ├── base.py                 # PlatformProtocol, registry
│   ├── youtube.py              # YT (android client, Videos/Audios)
│   ├── instagram.py            # IG (stories block, 3-step auth)
│   ├── facebook.py             # FB (reels, posts, watch)
│   └── twitter.py              # TW (tweets, spaces, rate limit)
├── installer/
│   ├── install_deps.bat        # Windows: winget + fallback
│   └── install_deps.sh         # Linux: detecta pkg mgr + fallback
├── CHANGELOG.md
├── README.md
├── requirements.txt
└── .main_combined_config.json  # (runtime, criado automaticamente)
```

## Adicionando Nova Plataforma

1. Crie `platforms/nova.py` implementando `PlatformProtocol`
2. Decore com `@register_platform`
3. Defina `info = PlatformInfo(name="XX", ...)` 
4. Pronto! Use `-p XX`

## Changelog

Use `--changelog` para ver o histórico completo.

### Versão 1.7.0 (25/11/2026)
- Suporte para Facebook (-p FB) e Twitter/X (-p TW)
- Arquitetura modular completa
- Scripts de instalação de dependências de sistema
- Flag --no-auto-deps

## Licença

MIT

## Autores

- Marcos Xavier (sis.marcosxavier@gmail.com) - https://github.com/marcosxavierdev
- S. Brenno (sbrennopqd@gmail.com) - https://github.com/M4lp4rt1d0-mir