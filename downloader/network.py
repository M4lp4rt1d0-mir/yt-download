"""Detecção de erros de rede e mensagens amigáveis para o usuário."""

from __future__ import annotations

from cli.output import print_error

# Erros de DNS / resolução de nome
_DNS_MARKERS = (
    "gaierror",
    "getaddrinfo failed",
    "temporary failure in name resolution",
    "name or service not known",
    "nodename nor servname",
    "unable to resolve host",
    "err_name_not_resolved",
)

# Erros de conexão TCP / proxy / timeout
_CONNECTION_MARKERS = (
    "urlopen error",
    "connection refused",
    "connectionreseterror",
    "connection aborted",
    "connection timed out",
    "timed out",
    "read timeout",
    "max retries exceeded",
    "network is unreachable",
    "no route to host",
    "newconnectionerror",
    "failed to establish a new connection",
    "remote end closed connection",
    "could not connect",
    "proxyerror",
    "err_tunnel_connection_failed",
    "10054",  # Windows: conexão resetada pelo par
    "10060",  # Windows: timeout de conexão
    "10061",  # Windows: conexão recusada
)

_MSG_DNS = (
    "Sem internet: não foi possível encontrar o endereço do site. "
    "Verifique sua conexão e tente novamente em instantes."
)
_MSG_CONNECTION = (
    "Sem internet (ou o site está fora do ar): não foi possível conectar. "
    "Verifique sua conexão e tente novamente em instantes."
)

# Evita repetir o mesmo aviso na extração de info e no download.
_reported = False


def network_error_message(error: str | Exception) -> str | None:
    """Retorna uma mensagem amigável se o erro parecer de conexão."""
    text = str(error).lower()

    if any(marker in text for marker in _DNS_MARKERS):
        return _MSG_DNS
    if any(marker in text for marker in _CONNECTION_MARKERS):
        return _MSG_CONNECTION
    return None


def report_network_error(error: str | Exception) -> bool:
    """Mostra o aviso uma única vez. Retorna True se era erro de rede."""
    global _reported

    message = network_error_message(error)
    if message is None:
        return False
    if not _reported:
        print_error(f"\n{message}")
        _reported = True
    return True


def reset_network_report() -> None:
    """Libera o aviso para uma nova execução (ou novo teste)."""
    global _reported
    _reported = False
