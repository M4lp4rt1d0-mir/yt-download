# Guia de Teste Beta — yt-download v1.7.0

Obrigado por testar! Este guia explica como rodar, o que testar e como reportar problemas.

---

## 1. Como instalar e rodar

```bash
# Clone a branch de desenvolvimento
git clone -b development https://github.com/M4lp4rt1d0-mir/yt-download.git
cd yt-download

# Instale dependências Python
pip install -r requirements.txt

# Instale dependências de sistema (FFmpeg + Node.js)
# Windows:
installer\install_deps.bat
# Linux:
bash installer/install_deps.sh

# Teste básico
python main.py --help
python main.py --changelog
```

---

## 2. Checklist de Testes por Plataforma

### YouTube (`-p YT` ou `AUTO`)
| Cenário | URL de teste | Esperado |
|---|---|---|
| Vídeo normal | `https://youtu.be/M19Hrft1iTE?si=ndbciHEySbz9O-vB` | MP4 1080p ou MP3 |
| Playlist | `https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOG5v1NtE2b4R1g` | Pasta com numeração |
| Shorts | `https://youtube.com/shorts/abc123` | Vídeo vertical |
| Live passada | `https://youtube.com/watch?v=live_id` | Vídeo completo |
| Áudio apenas | mesma URL + `-a` | MP3 192kbps |

### Instagram (`-p ITG` ou `AUTO`)
| Cenário | URL de teste | Esperado |
|---|---|---|
| Post público | `https://www.instagram.com/p/DeYnts9ALjH/?mdxt=MXF4cGlreHgxYXQwag==` | Vídeo/imagem |
| Reels | `https://www.instagram.com/reel/abc123/` | MP4 |
| Carrossel | `https://www.instagram.com/p/carrossel_id/` | Múltiplos arquivos |
| **Stories** | `https://www.instagram.com/stories/user/123/` | **Erro claro: não suportado** |
| **Privado** | URL de conta privada | **Erro claro: precisa login/cookies** |

### Facebook (`-p FB` ou `AUTO`)
| Cenário | URL de teste | Esperado |
|---|---|---|
| Reels público | `https://www.facebook.com/reel/123456789/` | MP4 |
| Post com vídeo | `https://www.facebook.com/user/posts/123/` | MP4 |
| Watch | `https://www.facebook.com/watch/?v=123` | MP4 |

### Twitter/X (`-p TW` ou `AUTO`)
| Cenário | URL de teste | Esperado |
|---|---|---|
| Tweet com vídeo | `https://x.com/user/status/123456789` | MP4 |
| Tweet com GIF | `https://twitter.com/user/status/123` | MP4 (GIF vira vídeo) |
| Space (áudio) | `https://x.com/i/spaces/123` | MP3 |

---

## 3. Flags para testar

| Flag | Teste |
|---|---|
| `-r 720p` | Limita resolução |
| `-o /caminho/custom` | Pasta de saída customizada |
| `-a` | Apenas áudio (MP3) |
| `--cookies edge` | Usa cookies do Edge (Instagram) |
| `--cookie-file /path/cookies.txt` | Arquivo Netscape |
| `--forget-cookies` | Limpa config salva |
| `--no-auto-deps` | Não instala deps Python |
| `--changelog` | Mostra histórico |

---

## 4. Cenários de Erro (Chaos Tests)

Tente estes e veja se a mensagem é **clara em PT-BR**:

| Ação | Esperado |
|---|---|
| Desligue a internet e rode download | "Sem internet: não foi possível encontrar o endereço do site..." |
| URL inexistente: `https://youtube.com/watch?v=naoexiste` | Erro 404 claro, não crash |
| Cookie Instagram expirado | Fluxo de 3 etapas: navegador → pergunta → caça arquivos |
| Rate limit Twitter (muitos downloads seguidos) | Backoff exponencial + aviso |
| Arquivo `.part` corrompido na pasta | Limpeza automática + retry |

---

## 5. Como Reportar

Abra issue no GitHub ou mande direto pro Brenno com:

```
**Plataforma:** YT / ITG / FB / TW / AUTO
**Comando exato:** python main.py "URL" -p PLATAFORMA -r 1080p -a --cookies edge
**SO:** Windows 10/11 / Ubuntu 22.04 / etc.
**Python:** python --version
**O que aconteceu:** (cole o output completo)
**O que esperava:**
**Logs/prints:** (se der, anexe screenshot do terminal)
```

---

## 6. Critérios de Aprovação (para merge na main)

- [ ] Todos os 4 plataformas baixam vídeo + áudio sem erro
- [ ] Playlists funcionam (pasta organizada, numeração)
- [ ] Flags `-r`, `-o`, `-a`, `--cookies`, `--forget-cookies` funcionam
- [ ] Mensagens de erro em PT-BR claras (sem stack trace crú)
- [ ] Sem internet → aviso amigável
- [ ] Instagram Stories/Privado → erro claro (não crash)
- [ ] Cookies salvos funcionam na 2ª execução
- [ ] `install_deps.bat/.sh` instalam FFmpeg + Node em máquina limpa
- [ ] `python -m compileall` passa sem erro
- [ ] QA Gate (`python scripts/qa_gate.py`) retorna PASS

---

## 7. URLs de Referência (já validadas)

- **YouTube:** `https://youtu.be/M19Hrft1iTE?si=ndbciHEySbz9O-vB` (88 MB, testado)
- **Instagram:** `https://www.instagram.com/p/DeYnts9ALjH/?mdxt=MXF4cGlreHgxYXQwag==` (testado)

> **Precisamos de URLs públicas válidas para Facebook e Twitter/X.** Se você tiver, mande junto no report.

---

**Qualquer dúvida, chama.** Valeu por testar! 🚀