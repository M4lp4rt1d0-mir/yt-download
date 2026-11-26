"""Configuration storage (JSON file)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cli.output import print_warning, print_success


CONFIG_PATH = Path.home() / ".main_combined_config.json"


def load_config() -> dict[str, Any]:
    """Load user configuration from JSON file."""
    try:
        if CONFIG_PATH.is_file():
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:  # nosec B110 - silently handle missing/corrupt config file
        pass
    return {}


def save_config(config: dict[str, Any]) -> bool:
    """Save user configuration to JSON file."""
    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print_warning(f"Não foi possível salvar a configuração: {e}")
        return False


def get_saved_auth(platform: str) -> dict[str, Any] | None:
    """Return saved cookie/browser auth for platform if still valid."""
    if platform != "ITG":
        return None
    auth = load_config().get("instagram_auth")
    if not auth:
        return None
    if auth.get("cookie_file"):
        if os.path.isfile(auth["cookie_file"]):
            return auth
        print_warning(f"O cookie salvo não existe mais: {auth['cookie_file']}")
        return None
    if auth.get("browser"):
        return auth
    return None


def remember_auth(platform: str, escolha: dict[str, Any]) -> None:
    """Save auth choice for future runs."""
    config = load_config()
    config[f"{platform.lower()}_auth"] = escolha
    if save_config(config):
        if escolha.get("cookie_file"):
            print_success(f"Cookie salvo para as próximas execuções: {escolha['cookie_file']}")
        elif escolha.get("browser"):
            print_success(f"Navegador salvo para as próximas execuções: {escolha['browser']}")
        print_warning("     (use --forget-cookies para esquecer)")


def forget_auth(platform: str) -> None:
    """Remove saved auth for platform."""
    config = load_config()
    config.pop(f"{platform.lower()}_auth", None)
    save_config(config)


def get_auth(platform: str) -> dict[str, Any] | None:
    """Get saved auth for a platform (alias for get_saved_auth)."""
    return get_saved_auth(platform)


def validate_cookie_file(path: str) -> bool:
    """Warn if cookie file doesn't contain sessionid."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "sessionid" not in content:
            print_warning("O arquivo não contém o cookie 'sessionid'. "
                          "O Instagram provavelmente continuará pedindo login.")
            return False
    except Exception:  # nosec B110 - silently handle unreadable cookie file
        pass
    return True