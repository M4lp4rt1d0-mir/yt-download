"""Terminal colors and formatted output utilities."""

from __future__ import annotations

# ANSI color codes
VERMELHO = "\033[91m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
RESET = "\033[0m"

BOLD = "\033[1m"
DIM = "\033[2m"


def color(text: str, color_code: str) -> str:
    """Wrap text with color codes."""
    return f"{color_code}{text}{RESET}"


def red(text: str) -> str:
    """Return red colored text."""
    return color(text, VERMELHO)


def green(text: str) -> str:
    """Return green colored text."""
    return color(text, VERDE)


def yellow(text: str) -> str:
    """Return yellow colored text."""
    return color(text, AMARELO)


def blue(text: str) -> str:
    """Return blue colored text."""
    return color(text, AZUL)


def bold(text: str) -> str:
    """Return bold text."""
    return color(text, BOLD)


def dim(text: str) -> str:
    """Return dim text."""
    return color(text, DIM)


def print_info(msg: str) -> None:
    """Print info message in blue."""
    print(f"{AZUL}{msg}{RESET}")


def print_success(msg: str) -> None:
    """Print success message in green."""
    print(f"{VERDE}{msg}{RESET}")


def print_warning(msg: str) -> None:
    """Print warning message in yellow."""
    print(f"{AMARELO}{msg}{RESET}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    print(f"{VERMELHO}{msg}{RESET}")


def print_header(title: str, width: int = 72) -> None:
    """Print a formatted header."""
    border = "=" * width
    print(f"{AMARELO}{border}{RESET}")
    print(f"{AMARELO}{title}{RESET}")
    print(f"{AMARELO}{border}{RESET}")


def print_section(title: str) -> None:
    """Print a section title."""
    print(f"\n{VERDE}{title}{RESET}")