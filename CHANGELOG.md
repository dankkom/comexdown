# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.1.0] - 2026-07-30

### Adicionado

- Novas opções no comando `sync` do CLI e plugin Typer: `--repetro`, `--validation` e `--other-tables` para permitir baixar dados do REPETRO, totais para validação e tabelas auxiliares em Excel.

### Alterado

- Atualizado `pyproject.toml` para o padrão PEP 639 de licenças, utilizando `license = "MIT"` e especificando a dependência do `hatchling>=1.27`.

## [2.0.0] - 2026-05-19

Primeira entrada em formato Keep a Changelog. O pacote foi renomeado de
`comexdown` para `comex-fetcher` e integrado ao ecossistema Quantilica.

### Alterado

- Renomeado de `comexdown` para `comex-fetcher` (ver guia de migração no README).

### Adicionado

- CLI standalone (`comex-fetcher`, argparse) e plugin Typer para o `quantilica-cli`
  (`quantilica comex`), com o comando `sync`.
- Manifestos de proveniência (`DownloadManifest`) via `quantilica-core`.
- Download de exportações, importações, dados municipais, série histórica NBM e
  tabelas auxiliares de códigos (NCM, países, UF, via).

### Histórico anterior

Versões até a 2.0.0 antecedem a adoção deste changelog e estão registradas nas
tags do repositório: 1.5.2 (2025-12-24), 1.4.1 (2024-03-08), 1.4.0 (2022-07-07),
1.3.3 (2021-04-23), 1.0 (2020-05-25), 0.9 (2020-04-30) — as anteriores à 2.0.0
ainda sob o nome `comexdown`.
