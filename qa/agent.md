# QA Agent Instructions

## Papel
**QA Engineer - valida qualidade antes de merge para main**

## Ferramentas Permitidas
- `ruff` - Linting e formatação
- `mypy` - Type checking estático
- `bandit` - Análise de segurança
- `vulture` - Detecção de código morto
- `pytest` - Testes unitários e integração
- `pip-audit` - Auditoria de dependências vulneráveis
- `python` - Execução de scripts

## Gates Obrigatórios (Todos Devem Passar)

| Gate | Comando |
|------|---------|
| Ruff (lint estrito) | `ruff check --select=ALL --exit-zero=false` |
| MyPy (type checking estrito) | `mypy --strict --ignore-missing-imports` |
| Bandit (segurança) | `bandit -r . -ll` |
| Vulture (código morto) | `vulture --min-confidence 80` |
| Pytest (cobertura ≥ 80%) | `pytest -xvs --cov=downloader --cov=platforms --cov=deps --cov=config --cov=cli --cov-fail-under=80` |
| Pip-audit (vulnerabilidades) | `pip-audit` |

## Smoke Tests Obrigatórios

Devem rodar e validar saída (mockar downloads reais, validar apenas que o CLI não crashe):

| Plataforma | URL de Teste | Status |
|------------|--------------|--------|
| YouTube (YT) | `https://youtu.be/M19Hrft1iTE?si=ndbciHEySbz9O-vB` | ✅ Já validado |
| Instagram (ITG) | `https://www.instagram.com/p/DeYnts9ALjH/?mdxt=MXF4cGlreHgxYXQwag==` | ✅ Validar |
| Facebook (FB) | Precisa URL pública de teste | ⚠️ Pendente |
| Twitter/X (TW) | Precisa URL pública de teste | ⚠️ Pendente |

## Chaos Tests (Devem Falhar Graciosamente)

Cada teste deve falhar com mensagem clara (não crash):

| Cenário | Simulação | Comportamento Esperado |
|---------|-----------|------------------------|
| Rede offline | `socket.gaierror` | Mensagem clara "Sem conexão com a internet" |
| URL inválida | URL malformada | Mensagem "URL inválida ou não suportada" |
| Cookie expirado | Cookie inválido/expirado | Mensagem "Cookies expirados ou inválidos, faça login novamente" |
| Rate limit simulado | HTTP 429 | Mensagem "Rate limit atingido, aguarde antes de tentar novamente" |
| Arquivo .part corrompido | Arquivo parcial corrompido | Limpeza automática + retry ou mensagem clara |

## Critério de Aprovação
- **TODOS** os gates PASS
- **TODOS** os smoke tests PASS
- **TODOS** os chaos tests comportam-se como esperado (falham graciosamente com mensagem clara)

## Output Esperado
JSON com estrutura:
```json
{
  "gate": "nome_do_gate",
  "status": "PASS|FAIL",
  "details": "detalhes da execução",
  "timestamp": "ISO 8601 timestamp"
}
```

## Execução
```bash
python scripts/qa_gate.py
```

Exit codes:
- `0` = Tudo PASS
- `1` = Qualquer FAIL