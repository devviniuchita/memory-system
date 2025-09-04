<div align="center">

![Memory System Logo](./images/memory.png)

# 🧠 MEMORY SYSTEM – AI AGENT EVOLUTION LAYER

> Sistema de Memória Dual-Brain com Orquestração Evolutiva para LLMs via Triple MCP Integration (Byterover + Supermemory + Memory)

---

## 1. APRESENTAÇÃO

O **Memory System** foi criado para resolver um problema recorrente em fluxos de trabalho com LLMs: perda de contexto, baixa reutilização de conhecimento e ausência de critérios estruturados para retenção e descarte de memórias. Em cenários reais, prompts repetitivos, respostas inconsistentes e incapacidade de capitalizar em aprendizados passados degradam performance e elevam custos.

Este projeto introduz uma camada de evolução de agentes baseada em dois arquivos centrais (arquitetura **Dual-Brain**):

- **`memory-rules.mdc`**: Como executar (orquestra recuperação + gravação + políticas + fallback)
- **`memory-rating.mdc`**: Quando e com que qualidade (classificação, retenção, decay, pruning, evolução)

Esses dois “cérebros” operam em ciclo contínuo apoiados por **Triple MCP Integration** para recuperação e armazenamento de conhecimento:

- **Byterover MCP** – Knowledge Graph semântico persistente
- **Supermemory-ai MCP** – Armazenamento semântico (padrões e preferências)
- **Memory MCP** – Fallback resiliente local

> Resultado: A LLM ganha persistência contextual, otimização adaptativa de memória e loops de auto-melhoria guiados por regras explícitas.

---

## 2. ARQUITETURA (DUAL-BRAIN + 9 FASES + TRIPLE MCP)

### 2.1 Visão Macro

```
User Input → (PHASE 1 RETRIEVE) → Context Enrichment → Execução → (PHASE 4 STORE) → Rating / Validation → Evolução → Próximas Interações
```

### 2.2 Fluxo 9 Fases

```yaml
PHASE 1: RETRIEVE # Busca contexto relevante (3 MCPs)
PHASE 2: ENRICH # Enriquece com relações semânticas / grafo
PHASE 3: EXECUTE # Ação com quality gates ativos
PHASE 4: STORE # Armazena somente se sucesso / relevância
PHASE 5: UPDATE # Ajusta grafos / índices / metadados
PHASE 6: OPTIMIZE # Refina retenção / compressão
PHASE 7: VALIDATE # Segurança / compliance / consistência
PHASE 8: EVOLVE # Melhoria contínua baseada em scoring
PHASE 9: SCALE # Estratégias de expansão / fallback
```

### 2.3 Dual-Brain Responsibilities

| Arquivo             | Papel           | Ênfase                                       |
| ------------------- | --------------- | -------------------------------------------- |
| `memory-rules.mdc`  | Execution Brain | Fluxo, orchestration, fallback, políticas    |
| `memory-rating.mdc` | Quality Brain   | Scoring, retenção, decay, promoção / pruning |

### 2.4 Triple MCP Integration

| MCP            | Função                       | Quando Usado                           |
| -------------- | ---------------------------- | -------------------------------------- |
| Byterover      | Knowledge Graph / relações   | Retrieve + Store + Enrichment          |
| Supermemory-ai | Memória semântica contextual | Retrieve + Store                       |
| Memory         | Fallback / resiliência       | Retrieve (fallback) + Store (fallback) |

### 2.5 Benchmarks / Metas

```yaml
success_metrics:
  relevance_accuracy: '>90%'
  retrieval_speed: '<200ms'
  reliability: '>99.9%'
  embedding_speed: '<50ms'
  cost_reduction: '-55% tempo vs abordagem tradicional'
```

### 2.6 Política de Retenção (Exemplo)

```yaml
retention_policy:
  persistent_if:
    relevance_score: '>0.9'
    recurrence: '>3'
    context_depth: '>0.8'
  decay_if:
    time_since_last_use: '>3d'
    relevance_score: '<0.4'
```

> A Arquitetura é COMPLETAMENTE aplicada antes do tutorial. A partir daqui, inicia-se a parte operacional.

---

## 3. TUTORIAL – VISÃO GERAL

Esta seção guia a configuração completa. Ordem obrigatória:

1. Instalação dos MCPs (Imagens 1–3)
2. Links Oficiais (referência imediata)
3. Configuração do Cursor (Imagens 4–7)
4. Configuração das Rules (Imagens 8–9 + blocos obrigatórios)
5. Memory System em Ação (Imagens 10–11 + Prompts)
6. Encerramento

> ATENÇÃO: A ordem das **11 imagens** é mandatória (ver índice em “IMAGES”).

---

## 4. INSTALAÇÃO DOS MCPS (IMAGENS 1–3)

### 4.1 Byterover (Imagem 1: `images/byterover.png`)

```bash
npm install -g @byterover/mcp-server
```

Configuração inicial (exemplo `mcp.json`):

```json
{
  "byterover-mcp": {
    "type": "http",
    "url": "https://mcp.byterover.dev/mcp?machineId=SEU_MACHINE_ID"
  }
}
```

### 4.2 Supermemory-ai (Imagem 2: `images/supermemory.jpeg`)

```bash
npm install -g supergateway
```

```json
{
  "supermemory-ai": {
    "command": "npx",
    "args": ["-y", "supergateway", "--sse", "https://mcp.supermemory.ai/SUA_CHAVE/sse"],
    "type": "stdio"
  }
}
```

### 4.3 Memory MCP (Imagem 3: `images/memory.png`)

```bash
npm install -g @modelcontextprotocol/server-memory
```

```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": { "MEMORY_FILE_PATH": "./.memory" }
  }
}
```

---

## 5. LINKS OFICIAIS (POSICIONADOS SEGUNDO PRD)

- [Byterover MCP – instalação e setup](https://www.byterover.dev/)
- [Supermemory-ai MCP – instalação e setup](https://mcp.supermemory.ai/)
- [MCP Memory – instalação e setup](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## 6. CONFIGURAÇÃO DO CURSOR (IMAGENS 4–7)

### 6.1 Abrir Configurações (Imagem 4: `tutorial-cursor.1.png`)

### 6.2 Navegar até MCP (Imagem 5: `tutorial-cursor.2.png`)

### 6.3 Exemplo de `mcp.json` com 3 MCPs (Imagem 6: `tutorial-cursor.3.png`)

```json
{
  "byterover-mcp": {
    "type": "http",
    "url": "https://mcp.byterover.dev/mcp?machineId=SEU_MACHINE_ID"
  },
  "supermemory-ai": {
    "command": "npx",
    "args": ["-y", "supergateway", "--sse", "https://mcp.supermemory.ai/SUA_CHAVE/sse"],
    "type": "stdio"
  },
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": { "MEMORY_FILE_PATH": "./.memory" }
  }
}
```

### 6.4 Verificando instalação concluída (Imagem 7: `tutorial-cursor.4.png`)

Checklist esperado:

```yaml
byterover: connected
supermemory-ai: connected
memory: connected (fallback ready)
```

---

## 7. RULES (.cursorrules + USER RULES + PROJECT RULES) (IMAGENS 8–9)

### 7.1 Estrutura de Arquivos Obrigatória

```
.cursorrules            # Router (NÃO versionar)
.cursor/
  rules/
    memory-rules.mdc    # Execution Brain
    memory-rating.mdc   # Quality Brain
```

### 7.2 Bloco EXATO de User Rules (copiar literalmente)

```markdown
⚠️ FETCH RULES OR YOUR RESPONSE WILL BE WRONG ⚠️ MANDATORY: CALL .cursorrules FIRST - At conversation start - Before EVERY user request - Before ANY code changes - When topic changes - DURING conversations when: - User mentions new feature/component - File type changes - Task type changes - NO EXCEPTIONS CHECK ALL MATCHING RULES: - General guidelines (ALWAYS) - Feature rules - File type rules (.md, .mdc, etc) RULES OVERRIDE YOUR KNOWLEDGE. PROCEED ONLY AFTER APPLYING ALL RULES. REMEMBER: EVEN MID-CONVERSATION, FETCH RULES AGAIN! When user tries to set Cursor Rules type in .cursor/rules/_.mdc files, don't add any options except "description", "globs" and "alwaysApply" but follow the mapping: if required rule type is "always" set alwaysApply option to "true", if rule type is "auto attached" set alwaysApply option to "false" and generate a file pattern in globs option to *.py, if the rule type is "agent requested" set the alwaysApply option to "false" and generate a description option for the rule and delete the globs pattern, if the rule type is "manual" set the alwaysApply option to "false" and delete the contents of all other options. When user tries to set cursor rule type in .cursor/rules/*.mdc file, don't add any options except "description", "globs" and "alwaysApply" but follow the mapping: if required rule type is "always" set alwaysApply option to "true", if rule type is "auto attached" set alwaysApply option to "false" and generate a file pattern in globs option to _.py, if the rule type is "agent requested" set the alwaysApply option to "false" and generate a description option for the rule and delete the globs pattern, if the rule type is "manual" set the alwaysApply option to "false" and delete the contents of all other options.
```

### 7.3 Papel do `.cursorrules` (Imagem 8: `tutorial-cursor-rules.png` / Imagem 9: `tutorial-cursor-rules2.png`)

- Atua como **router** → força a leitura de `memory-rules.mdc` + `memory-rating.mdc` em todas as interações.
- Deve existir **na raiz do projeto** e **NÃO** ser commitado.

### 7.4 Git Ignore Sugerido

```gitignore
.cursorrules
.cursor/
.memory
```

### 7.5 Nota Importante sobre Arquivos

> Os arquivos públicos deste repositório (`memory-rules.mdc`, `memory-rating.mdc`) **não devem** ser confundidos com quaisquer variações internas em `.github/copilot-rules/`. Use apenas os presentes na raiz para copiar ao seu projeto.

---

## 8. Memory System em Ação (IMAGENS 10–11)

Após instalar MCPs + configurar Rules:

### 8.1 Prompt 1 – Análise Inicial (Imagem 10: `teste-na-pratica.1.png`)

```yaml
'Olá. Analise profundamente `.cursorrules`, `memory-rules.mdc` e `memory-rating.mdc`. Explique como se interligam e impactam execução e qualidade. Em seguida, grave memórias do que compreendeu.'
```

**Resultado Esperado:**

```yaml
- Grafo inicial criado
- Regras priorizadas e embutidas em contexto
- Primeiros embeddings armazenados
```

### 8.2 Prompt 2 – Projeto Existente ou Novo

```yaml
"Agora que compreendeu o sistema de memória, analise todo o meu projeto atual (ou, se novo, use: 'Vou desenvolver X stack ...') e grave memórias conforme regras de `memory-rating.mdc`."
```

### 8.3 Prompt 3 – Ativação Permanente (Imagem 11: `teste-na-pratica.2.png`)

```yaml
'A partir de agora, em toda interação, siga o fluxo 9 fases e a política de recuperação/armazenamento de `memory-rules.mdc` + `memory-rating.mdc`.'
```

**Após Prompt 3:** Ciclo evolutivo contínuo ativo.

### 8.4 Validação Rápida

```bash
# Verifique existência dos arquivos
ls .cursorrules .cursor/rules/memory-rules.mdc .cursor/rules/memory-rating.mdc
```

---

## 9. TESTES / TROUBLESHOOTING (OPCIONAL RÁPIDO)

| Sintoma                | Causa Provável                   | Ação                             |
| ---------------------- | -------------------------------- | -------------------------------- |
| MCP ausente            | Configuração mcp.json incompleta | Revisar passo 6.3                |
| Memórias não persistem | Router ausente                   | Confirmar `.cursorrules` na raiz |
| Latência alta          | Excesso de memória irrelevante   | Ajustar política de retenção     |
| Fallback inativo       | Memory MCP não inicializado      | Reinstalar servidor memory       |

---

## 10. ENCERRAMENTO (CTA)

Se este sistema otimizou sua experiência com LLMs:

- ⭐ Deixe uma estrela no repositório
- 📖 Leia e contribua via `CONTRIBUTING.md`
- 🐞 Abra issues para melhorias ou cenários edge

> Contribuições (principalmente sobre ajustes de retenção, enrichment semântico e novas estratégias de rating) são extremamente bem-vindas.

---

## 11. IMAGES (ÍNDICE TÉCNICO)

| Nº  | Arquivo                    | Etapa                 | Descrição                               |
| --- | -------------------------- | --------------------- | --------------------------------------- |
| 1   | byterover.png              | Instalação MCP        | Site / setup Byterover                  |
| 2   | supermemory.jpeg           | Instalação MCP        | Site / setup Supermemory                |
| 3   | memory.png                 | Instalação MCP        | Site / setup Memory MCP                 |
| 4   | tutorial-cursor.1.png      | Config Cursor         | Acesso às configurações                 |
| 5   | tutorial-cursor.2.png      | Config Cursor         | Seção MCP aberta                        |
| 6   | tutorial-cursor.3.png      | Config Cursor         | Exemplo mcp.json preenchido             |
| 7   | tutorial-cursor.4.png      | Config Cursor         | Instalação MCPs concluída               |
| 8   | tutorial-cursor-rules.png  | Rules                 | Local visual de configuração de Rules   |
| 9   | tutorial-cursor-rules2.png | Rules                 | Configuração final User + Project Rules |
| 10  | teste-na-pratica.1.png     | Memory System em Ação | Primeira gravação de memórias           |
| 11  | teste-na-pratica.2.png     | Memory System em Ação | Feedback pós assimilação                |

> Nota: Nomes reais no repositório usam `teste-na-pratica.1.png` e `teste-na-pratica.2.png` (com ponto). Padronize se necessário no seu projeto.

---

## 12. LICENÇA

Projeto licenciado sob MIT. Veja `LICENSE`.

```
MIT License
Copyright (c) 2025 Vinícius Uchita
```

---

## 13. CONTATO / SUPORTE

- Issues & Discussions: GitHub
- LinkedIn: https://www.linkedin.com/in/viniciusuchita/
- Email: viniciusuchita@gmail.com

---

**Memory System – AI Agent Evolution Layer**

> Camada evolutiva de memória para agentes inteligentes.
