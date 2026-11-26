# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## Origem

A primeira versão deste projeto foi criada em **07/04/2026** por S. Brenno (Python)
e pelo marido da sua prima Marcos Xavier (Java), inicialmente apenas por diversão. O que começou
como brincadeira entre amigos evoluiu para o downloader modular atual.

## [1.7.0] - 2026-11-25

### Adicionado
- Suporte para **Facebook** (`-p FB`): reels, posts, watch
  - Pasta padrão: `facebook_downloads/Videos` e `facebook_downloads/Audios`
- Suporte para **Twitter/X** (`-p TW`): tweets, spaces
  - Pasta padrão: `twitter_downloads/Videos` e `twitter_downloads/Audios`
  - Tratamento de rate limit com backoff exponencial
- Nova arquitetura modular:
  - `cli/args.py` - Parseamento de argumentos e help
  - `cli/output.py` - Cores e prints formatados
  - `config/store.py` - Configuração JSON e cache de cookies
  - `deps/system.py` - Verificação de dependências de sistema
  - `downloader/core.py` - Download com retry e limpeza
  - `downloader/formats.py` - Seleção de formato e templates
  - `platforms/base.py` - Protocolo e registry de plataformas
  - `platforms/youtube.py` - Lógica do YouTube
  - `platforms/instagram.py` - Lógica do Instagram (3-step auth)
  - `platforms/facebook.py` - Lógica do Facebook
  - `platforms/twitter.py` - Lógica do Twitter/X
- Scripts de instalação de dependências de sistema:
  - `installer/install_deps.bat` (Windows: winget + Chocolatey fallback)
  - `installer/install_deps.sh` (Linux: detecta apt/dnf/pacman/zypper/apk)
- Flag `--no-auto-deps` para desativar instalação automática de pacotes Python
- Flag `--platform` aceita: `YT`, `ITG`, `FB`, `TW` (padrão: `YT`)
- Detecção automática de plataforma pela URL quando `-p` não especificado
- Detecção de erros de conexão (sem internet / site fora do ar) com mensagem clara
  na leitura de metadados, no download e na instalação do `yt-dlp`

### Alterado
- Refatoração completa mantendo **compatibilidade total** com YouTube e Instagram
- `main.py` reduzido para ~30 linhas (entry point fino)
- Código organizado por responsabilidade (baixo acoplamento, alta coesão)
- Open/Closed: nova plataforma = novo arquivo em `platforms/`, sem outras mudanças

### Corrigido
- Organização de pastas por plataforma padronizada
- Imports com `TYPE_CHECKING` para evitar dependências circulares
- Mensagem de conclusão agora aparece para **todas** as plataformas (YT, ITG, FB e TW),
  informando a pasta dos arquivos; falhas também exibem aviso claro
- Mensagem do Instagram centralizada no `main.py` (evita duplicação)
- Cookies do Instagram também são salvos quando a plataforma é detectada automaticamente (`AUTO`)

## [1.6.4] - 2026-11-25

### Adicionado
- `requirements.txt` com `yt-dlp>=2026.03.17`
- Notas sobre FFmpeg/Node.js como dependências externas (não pip)

## [1.6.3] - 2026-11-25

### Adicionado
- Changelog integrado e flag `--changelog` (funciona no executável)
- Manual informa como consultar o histórico

## [1.6.2] - 2026-11-25

### Corrigido
- `extractor_args` do YouTube para formato aceito pela API do yt-dlp (`player_client=android`)
- Cliente `android_vr` era ignorado e causava HTTP 403 após ~10 MB
- Mesmo ajuste aplicado ao scan inicial (evitava erro do solvedor de JS antes do download)
- Cliente android puro passou a usar formato 18 (MP4 completo)
- Removido arquivo `.part` órfão do formato 399 deixado pela versão anterior

## [1.6.1] - 2026-11-25

### Adicionado
- Retry automático (3 tentativas) em HTTP 403, limpando arquivos `.part/.ytdl`
- Aviso quando yt-dlp estiver desatualizado (>90 dias)

### Corrigido
- Erro 403 do YouTube deixou de ser exibido como "conteúdo privado/indisponível"

## [1.6.0] - 2026-11-25

### Adicionado
- Script combinado `main_combined.py` (preservando `main.py` original)
- Flag `-p/--platform` (YT ou ITG), padrão YT
- Pastas automáticas por plataforma:
  - YouTube → `Youtube_Downloads/Videos` e `Youtube_Downloads/Audios`
  - Instagram → `instagram_downloads/Videos` e `instagram_downloads/Instagram_audios`
- Tratativa para Stories e conteúdo privado do Instagram
- Fluxo de cookies do Instagram em 3 etapas:
  1. Detectar navegador aberto
  2. Perguntar ao usuário
  3. Procurar arquivos de cookie
  - Escolha salva para reutilização
- Flags `--cookies`, `--cookie-file` e `--forget-cookies`
- `ignoreerrors=False` para não imprimir sucesso quando o download falha

## [1.4.6] - 2026-04-09

### Mantido
- Versão do downloader original apenas de YouTube (`main.py`), preservada como referência

## [1.0.0] - 2026-04-07

### Adicionado
- Primeira versão registrada do projeto (`youtube_downloader.py`)