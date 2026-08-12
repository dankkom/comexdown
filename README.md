# comex-fetcher

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square) ![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)

Coletor de dados de comércio exterior brasileiro. Funções para download de dados publicados pelo [Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC)][1]. Suporta exportações, importações, dados municipais, série histórica NBM e tabelas auxiliares de códigos (NCM, países, UF, via, etc.).

> **Documentação Completa:** Consulte [https://docs.quantilica.com](https://docs.quantilica.com) para obter a documentação completa, guias de uso e referência da API.

> Este pacote foi anteriormente distribuído como `comexdown`. Veja o [guia de migração](#migração-de-comexdown) abaixo.

## Instalação

```bash
pip install git+https://github.com/Quantilica/comex-fetcher.git
```

## Uso Rápido

```python
import comex_fetcher
from pathlib import Path

data_dir = Path("./dados")

# Exportações + importações de 2023
comex_fetcher.get_year(data_dir, year=2023)

# Apenas exportações
comex_fetcher.get_year(data_dir, year=2023, exp=True)

# Tabela de códigos NCM
comex_fetcher.get_table(data_dir, table="ncm")
```

## CLI

```text
comex-fetcher <comando> [argumentos]

Comandos:
  sync [ANOS...] [-exp] [-imp] [-mun] [--no-tables] [--tables-only] [--dry-run] [-o CAMINHO]
        Sincronizar transações comerciais e tabelas auxiliares. Sem ANOS,
        baixa todos os anos desde 1989; aceita anos (2023) e intervalos
        (2018:2023). -exp/-imp restringem a direção; padrão baixa ambas.
        -mun adiciona dados no nível municipal (1997+). --no-tables pula as
        tabelas; --tables-only baixa apenas as tabelas; --dry-run lista sem
        baixar.
  list  Listar as tabelas de códigos auxiliares disponíveis.
```

```bash
# Exportações + importações de 2023 (+ tabelas auxiliares)
comex-fetcher sync 2023 -o ./dados

# Apenas importações, 2018–2023, com dados municipais
comex-fetcher sync 2018:2023 -imp -mun -o ./dados

# Apenas as tabelas auxiliares de códigos
comex-fetcher sync --tables-only -o ./dados

# Tudo: todos os anos + todas as tabelas
comex-fetcher sync -o ./dados

# Listar tabelas auxiliares disponíveis
comex-fetcher list
```

## API Python

```python
from pathlib import Path
import comex_fetcher

data_dir = Path("./dados")

# Transações por ano — NCM (1997+)
comex_fetcher.get_year(data_dir, year=2023)
comex_fetcher.get_year(data_dir, year=2023, imp=True, mun=True)

# Série histórica NBM (1989–1996)
comex_fetcher.get_year_nbm(data_dir, year=1995)

# Arquivos completos (todos os anos consolidados)
comex_fetcher.get_complete(data_dir)

# Tabela de código auxiliar
comex_fetcher.get_table(data_dir, table="pais")

# Tudo de uma vez
comex_fetcher.download_all(data_dir)
```

## Datasets Disponíveis

| Grupo | Datasets |
| :--- | :--- |
| Transações (NCM, 1997+) | `exp`, `imp`, `exp-mun`, `imp-mun` |
| Histórico (NBM, 1989–96) | `exp-nbm`, `imp-nbm` |
| Completos (arquivo único) | `exp-completa`, `imp-completa`, `exp-mun-completa`, `imp-mun-completa` |
| Validação | `exp-validacao`, `imp-validacao`, `exp-mun-validacao`, `imp-mun-validacao` |
| REPETRO | `exp-repetro`, `imp-repetro` |
| Tabelas auxiliares | `ncm`, `sh`, `cuci`, `cgce`, `isic`, `siit`, `fat-agreg`, `unidade`, `ppi`, `ppe`, `grupo`, `pais`, `pais-bloco`, `uf`, `uf-mun`, `via`, `urf`, `isic-cuci`, `nbm`, `ncm-nbm` |

## Migração de comexdown

Se você usava o pacote `comexdown`, atualize a instalação e os imports:

```bash
pip uninstall comexdown
pip install git+https://github.com/Quantilica/comex-fetcher.git
```

```python
# Antes
import comexdown
comexdown.get_year(data_dir, year=2023)

# Depois
import comex_fetcher
comex_fetcher.get_year(data_dir, year=2023)
```

## Desenvolvimento

```bash
git clone https://github.com/Quantilica/comex-fetcher.git
cd comex-fetcher
uv sync --dev
uv run pytest
```

## Licença

MIT — veja [LICENSE](LICENSE).

[1]: https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
