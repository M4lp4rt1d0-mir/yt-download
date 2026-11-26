#!/usr/bin/env bash
# =====================================================================
# install_deps.sh - Instala dependencias de sistema no Linux
# FFmpeg, yt-dlp (via pip), Node.js (para yt-dlp JS runtime)
# =====================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

print_info() { echo -e "${BLUE}$*${RESET}"; }
print_success() { echo -e "${GREEN}$*${RESET}"; }
print_warning() { echo -e "${YELLOW}$*${RESET}"; }
print_error() { echo -e "${RED}$*${RESET}"; }

echo
echo "====================================================================="
echo "  INSTALADOR DE DEPENDENCIAS - Linux"
echo "====================================================================="
echo

# ----------------------------------------------------------------------
# Detect package manager
# ----------------------------------------------------------------------
detect_pkg_mgr() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v yum >/dev/null 2>&1; then
        echo "yum"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper"
    elif command -v apk >/dev/null 2>&1; then
        echo "apk"
    else
        echo "unknown"
    fi
}

PKG_MGR=$(detect_pkg_mgr)
print_info "Gerenciador de pacotes detectado: $PKG_MGR"

# ----------------------------------------------------------------------
# FFmpeg
# ----------------------------------------------------------------------
print_info "[1/3] Verificando FFmpeg..."
if command -v ffmpeg >/dev/null 2>&1; then
    print_success "[OK] FFmpeg ja instalado: $(ffmpeg -version | head -n1)"
else
    print_warning "FFmpeg nao encontrado. Instalando..."
    case "$PKG_MGR" in
        apt)
            sudo apt-get update && sudo apt-get install -y ffmpeg
            ;;
        dnf)
            sudo dnf install -y ffmpeg
            ;;
        yum)
            sudo yum install -y epel-release && sudo yum install -y ffmpeg
            ;;
        pacman)
            sudo pacman -S --noconfirm ffmpeg
            ;;
        zypper)
            sudo zypper install -y ffmpeg
            ;;
        apk)
            sudo apk add ffmpeg
            ;;
        *)
            print_error "Gerenciador de pacotes nao suportado: $PKG_MGR"
            print_warning "Instale FFmpeg manualmente e tente novamente."
            ;;
    esac

    if command -v ffmpeg >/dev/null 2>&1; then
        print_success "[SUCESSO] FFmpeg instalado."
    else
        print_error "[ERRO] Falha na instalacao do FFmpeg."
        print_warning "Tente instalar manualmente:"
        echo "  Ubuntu/Debian: sudo apt install ffmpeg"
        echo "  Fedora: sudo dnf install ffmpeg"
        echo "  Arch: sudo pacman -S ffmpeg"
        echo "  openSUSE: sudo zypper install ffmpeg"
        echo "  Alpine: sudo apk add ffmpeg"
    fi
fi

# ----------------------------------------------------------------------
# yt-dlp (via pip - gerenciado pelo script Python)
# ----------------------------------------------------------------------
echo
print_info "[2/3] Verificando yt-dlp (Python)..."
if python3 -c "import yt_dlp" 2>/dev/null; then
    VERSION=$(python3 -c "import yt_dlp; print(yt_dlp.version.__version__)")
    print_success "[OK] yt-dlp ja instalado: $VERSION"
else
    print_warning "yt-dlp nao encontrado. Sera instalado automaticamente pelo script Python."
    print_info "Ou instale manualmente: python3 -m pip install -U yt-dlp"
fi

# ----------------------------------------------------------------------
# Node.js (necessario para extractor JS do yt-dlp)
# ----------------------------------------------------------------------
echo
print_info "[3/3] Verificando Node.js (para extractor JS do yt-dlp)..."
if command -v node >/dev/null 2>&1; then
    print_success "[OK] Node.js ja instalado: $(node --version)"
else
    print_warning "Node.js nao encontrado. Instalando..."

    # Try NodeSource repository for latest LTS
    if [ "$PKG_MGR" = "apt" ]; then
        print_info "Adicionando repositorio NodeSource (LTS)..."
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [ "$PKG_MGR" = "dnf" ] || [ "$PKG_MGR" = "yum" ]; then
        print_info "Adicionando repositorio NodeSource (LTS)..."
        curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
        sudo "$PKG_MGR" install -y nodejs
    elif [ "$PKG_MGR" = "pacman" ]; then
        sudo pacman -S --noconfirm nodejs npm
    elif [ "$PKG_MGR" = "zypper" ]; then
        sudo zypper install -y nodejs
    elif [ "$PKG_MGR" = "apk" ]; then
        sudo apk add nodejs npm
    else
        print_error "Gerenciador de pacotes nao suportado para Node.js: $PKG_MGR"
        print_warning "Instale Node.js manualmente (versao LTS):"
        echo "  https://nodejs.org/"
    fi

    if command -v node >/dev/null 2>&1; then
        print_success "[SUCESSO] Node.js instalado: $(node --version)"
    else
        print_error "[ERRO] Falha na instalacao do Node.js."
        print_warning "Instale manualmente: https://nodejs.org/"
    fi
fi

# ----------------------------------------------------------------------
# Final verification
# ----------------------------------------------------------------------
echo
echo "====================================================================="
echo "  Verificacao final"
echo "====================================================================="
echo

command -v ffmpeg >/dev/null 2>&1 && print_success "[OK] FFmpeg: $(ffmpeg -version | head -n1 | cut -d' ' -f3)" || print_error "[FALTA] FFmpeg"
python3 -c "import yt_dlp; print('[OK] yt-dlp:', yt_dlp.version.__version__)" 2>/dev/null || print_error "[FALTA] yt-dlp"
command -v node >/dev/null 2>&1 && print_success "[OK] Node.js: $(node --version)" || print_error "[FALTA] Node.js"

echo
print_info "Se tudo estiver OK, voce pode executar: python3 main.py \"URL\""
echo