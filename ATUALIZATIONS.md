# ATUALIZATIONS.md

Histórico técnico e transparente de atualizações do Memory System, com foco na camada RAG integrada ao Dual Brain.

> Público-alvo: mantenedores, contribuidores e usuários avançados. Este documento resume mudanças relevantes, como usar, ganhos e pontos de atenção.

---

## Visão geral

Implementamos um pipeline “Dual Brain + RAG” totalmente automatizado e validado no Windows. O fluxo padrão é:

1. Dual Brain (one-shot) via `memory-dual-brain-sync-oneshot.js`
   - Carrega `memory-rules.mdc` (Execution) e `memory-rating.mdc` (Quality)
   - Faz análise de diffs (auto-modificação desativada por design para evitar loops)
   - Registra métricas em `./memory-sync-metrics.json`

2. RAG Bootstrap (opcional, habilitado por variável de ambiente)
   - Cria/usa `.venv`
   - Instala dependências de `requirements-rag.txt`
   - Constrói índice em `.rag/index.<profile>` (FAISS; fallback Chroma)
   - Executa harness de testes (opcional)
   - Inicia watch para rebuild incremental (opcional)

Tudo isso é orquestrado por `run-sync.bat` (Windows) e `run-sync.sh` (Unix/Linux).

---

## O que foi adicionado

- CLI RAG (Python) em `tools/rag_indexer.py`
  - build/query/watch
  - Splitting de Markdown: MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter
  - Retriever com MMR (`as_retriever(search_type="mmr")`)
  - Metadados automáticos por arquivo (step/rule_type/priority) e filtros de consulta
  - Ignora padrões via globs (lê .copilotignore/.cursorignore quando presentes)
  - Perfis: `vscode` (prioriza `.github/copilot-rules/*.md`), `cursor` (prioriza `.cursor/rules/*.mdc`) e `auto` (preferência VS Code quando ambos existem)
  - Contextual Compression opcional (EmbeddingsFilter)
  - Reranking opcional (Gemini) via `langchain-google-genai`
  - Exportação de contexto agregado via `--out-file`
  - Métricas JSONL em `.rag/metrics.jsonl` (build, query, watch)

- Vetorização/Embeddings
  - `langchain-huggingface` com `sentence-transformers/all-MiniLM-L6-v2`
  - Vectorstores: FAISS (preferencial) com fallback automático para Chroma

- Observabilidade
  - RAG: `.rag/metrics.jsonl`
  - Dual Brain: `memory-sync-metrics.json`

- Testes e qualidade
  - Harness simples `tools/rag_eval.py` + `tests/rag-cases.yaml`
  - Casos cobrindo: step3 (todo2) e compressão de contexto em step1

- Automação
  - `run-sync.bat`: ASCII-only, robusto no CMD, cria `.rag/index.<profile>` automaticamente, aceita env vars e inicia watch em background
  - `run-sync.sh`: equivalente Unix
  - Tasks VS Code (build/query/watch/eval/bootstrap) – visam experiência 1-clique

---

## Como usar (rápido)

### Via scripts (recomendado)

Windows (CMD):

```
RAG_ENABLE=1 RAG_WATCH=0 RAG_EVAL=1 RAG_PROFILE=vscode run-sync.bat
```

Unix/Linux:

```
RAG_ENABLE=1 RAG_WATCH=1 RAG_EVAL=0 RAG_PROFILE=auto ./run-sync.sh
```

Variáveis suportadas:

- `RAG_ENABLE` = 1|true|yes|on (habilita RAG) – default: 1
- `RAG_PROFILE` = vscode|cursor|auto – default: vscode
- `RAG_WATCH` = 1 (watch em background) – default: 1
- `RAG_EVAL` = 1 (roda harness, se existir `tests/rag-cases.yaml`) – default: 1

Artefatos:

- Índice: `.rag/index.<profile>` (FAISS) – ex.: `.rag/index.vscode`
- Métricas: `.rag/metrics.jsonl` (RAG) e `./memory-sync-metrics.json` (Dual Brain)

### Via CLI RAG diretamente

Build (VS Code rules):

```
.venv/Scripts/python.exe tools/rag_indexer.py build --root . --index-path .rag/index.vscode --profile vscode
```

Query (filtro por step3):

```
.venv/Scripts/python.exe tools/rag_indexer.py query --index-path .rag/index.vscode --profile vscode --q "Quando devo aplicar as regras do passo 3 relacionadas a 'todo2'?" --filter-step step3 --k 6 --fetch-k 24 --lambda-mult 0.5
```

Watch (rebuild incremental):

```
.venv/Scripts/python.exe tools/rag_indexer.py watch --root . --index-path .rag/index.vscode --profile vscode --interval 2 --quiet
```

Reranking (opcional, requer credenciais do Google no ambiente):

```
.venv/Scripts/python.exe tools/rag_indexer.py query --index-path .rag/index.vscode --profile vscode --q "..." --rerank-llm google --rerank-top-n 5
```

Exportar contexto agregado de resultados:

```
.venv/Scripts/python.exe tools/rag_indexer.py query --index-path .rag/index.vscode --profile vscode --q "..." --out-file .rag/context_export.md
```

---

## Ganhos e melhorias

- Contexto mais relevante e focado (MMR + metadados por step/regra)
- Robustez no Windows (batch sanitizado, diretórios criados antes do FAISS)
- Produtividade via watch e tasks VS Code
- Observabilidade ponta a ponta (JSONL + métricas do Dual Brain)
- Extensibilidade: compressão de contexto e reranking por LLM opcionais

---

## Detalhes de arquitetura

- Split de Markdown em 2 fases: cabeçalhos (preserva semântica) e caracteres (normaliza tamanhos)
- Heurísticas de metadados (ex.: behavioral-rules → step1/always-apply/high)
- Roteamento por perfil (vscode/cursor/auto) priorizando contexto mais relevante do repositório
- Filtros de consulta: por step, rule_type, prioridade, diretórios e extensões
- Backends: FAISS local em `.rag/index.<profile>`; fallback Chroma se FAISS indisponível

---

## Solução de problemas (FAQ)

- “FAISS: could not open .../index.faiss”: garanta que `.rag` e `.rag/index.<profile>` existam. O `run-sync.bat` já cria automaticamente.
- “RAG_PROFILE inválido”: no Windows, evite espaços acidentais. O batch sanitize o valor, mas prefira `vscode`/`cursor`/`auto` exatos.
- “Batch não roda no VS Code Terminal (bash)”: execute via CMD/PowerShell ou use `cmd.exe /c run-sync.bat`.
- “Chroma InternalError: unable to open database file”: verifique permissões da pasta do projeto; rode como usuário com acesso de escrita.

---

## Roadmap (próximos passos)

- Mais casos no harness (step2/project-rules; cenários de compressão)
- Dashboard leve para `.rag/metrics.jsonl`
- Modo watch opcional do Dual Brain em background (sem loops)
- Exportadores adicionais (JSON/CSV) do contexto recuperado

---

## Referências

- Código: `tools/rag_indexer.py`, `tools/rag_eval.py`, `run-sync.bat`, `run-sync.sh`
- Regras: `.github/copilot-rules/*.md`, `.cursorrules`, `memory-*.mdc`
- Políticas: `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`
- Como contribuir: `CONTRIBUTING.md`
