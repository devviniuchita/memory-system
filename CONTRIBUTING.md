# 🤝 CONTRIBUTING - MEMORY SYSTEM

> Guia de Contribuição para Sistema de Memória Dual-Brain com Triple MCP Integration

---

## 🚀 **VISÃO GERAL**

O **Memory System** estabelece critérios específicos para contribuições em sistemas de memória para LLMs, focando em **arquitetura dual-brain** e **integração MCP**.

### 💎 **CRITÉRIOS AI/MCP ESPECÍFICOS**

**Validação Obrigatória:**

- Performance: <50ms embedding, >99.9% reliability
- Compliance com 9-phase workflow (RETRIEVE→ENRICH→EXECUTE→STORE→UPDATE→OPTIMIZE→VALIDATE→EVOLVE→SCALE)
- Integração dual-brain: `memory-rules.mdc` ↔ `memory-rating.mdc`
- Triple MCP validation: [Byterover](https://www.byterover.dev/) + [Supermemory](https://mcp.supermemory.ai/) + [Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)

**Padrões Técnicos:**

- Documentação em português com qualidade técnica internacional
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) compliance
- Testes específicos para algoritmos de memória e retenção

---

## ⚙️ **AMBIENTE DE DESENVOLVIMENTO**

### Configuração Rápida (5 minutos)

```bash
# 1. Clone e configure
git clone https://github.com/devviniuchita/memory-system.git
cd memory-system

# 2. Instale MCPs essenciais
npm install -g @modelcontextprotocol/server-memory
npm install -g @byterover/mcp-server
npm install -g supergateway

# 3. Configure Cursor com MCP (consulte README para detalhes)
```

### Dependências

- **Cursor IDE** + **MCP Integration**
- **Node.js 18+** para MCP servers
- **Conhecimento**: Python/TypeScript, sistemas de memória

---

## 🎯 **TIPOS DE CONTRIBUIÇÃO**

### 🧠 **Algoritmos de Memória (Prioridade Alta)**

- Otimização de RAG (Retrieval-Augmented Generation)
- Algoritmos de retenção e decay inteligente
- Compressão semântica de contexto
- Estratégias de fallback para MCPs

### ⚡ **Integração MCP (Prioridade Alta)**

- Novos MCP servers para diferentes fontes
- Melhorias na comunicação entre MCPs
- Protocolos de sincronização dual-brain
- Segurança e autenticação MCP

### 📚 **Documentação (Prioridade Média)**

- Guias de configuração para diferentes ambientes
- Tutoriais de otimização de memória
- Exemplos práticos de uso
- Documentação técnica de APIs

---

## ✅ **PROCESSO DE REVIEW - CRITÉRIOS AI-SPECIFIC**

### Checklist Obrigatório

- [ ] **Algoritmos de Memória**: Performance testada (benchmarks incluídos)
- [ ] **MCP Integration**: Servidores testados e compatíveis
- [ ] **Dual-Brain Compliance**: Validação `memory-rules.mdc` ↔ `memory-rating.mdc`
- [ ] **9-Phase Workflow**: Testes para todas as fases do ciclo
- [ ] **Documentação**: Exemplos de uso incluídos
- [ ] **Testes de Prompts**: 3 prompts padrão executados com sucesso
- [ ] **Performance**: Não degrada métricas (<50ms, >99.9%)
- [ ] **Segurança**: Validação de dados e tratamento de erros

### Critérios de Aprovação

1. **Funcionalidade AI**: Algoritmos corretamente implementados
2. **Qualidade de Memória**: Compressão semântica preservada
3. **Integração MCP**: Protocolos MCP seguidos
4. **Performance**: Benchmarks comparativos incluídos
5. **Testes AI**: Casos edge de IA cobertos
6. **Documentação**: Exemplos práticos incluídos

---

## 🧪 **COMPLIANCE DUAL-BRAIN E 9 FASES**

### Diretrizes Arquiteturais

**memory-rules.mdc (Execution Brain):**

- Define políticas de execução, recuperação e armazenamento
- Implementa fallback strategies e orquestração MCP
- Gere fluxo entre as 9 fases do workflow

**memory-rating.mdc (Quality Brain):**

- Define critérios de qualidade, retenção e decay
- Implementa scoring e pruning de memórias
- Guia evolução contínua do sistema

### Validação Requerida

```yaml
# Teste obrigatório para contribuições
test_scenario:
  input: 'Prompt complexo com contexto multi-sessão'
  expected:
    - retrieval_time: '<200ms'
    - storage_decision: 'baseado em scoring'
    - dual_brain_sync: 'bidirectional'
    - phase_compliance: '1-9 executadas'
```

---

## 📋 **CHECKLIST ESPECÍFICO PRD**

### Performance Requirements

| Métrica                  | Valor Mínimo | Como Testar                 |
| ------------------------ | ------------ | --------------------------- |
| Embedding Speed          | <50ms        | Benchmark incluído no PR    |
| Reliability              | >99.9%       | Testes de stress 1000+ ops  |
| Retrieval Speed          | <200ms       | Testes com datasets grandes |
| Cross-Session Continuity | Seamless     | Validação multi-sessão      |

### Documentação Requirements

- [ ] Algoritmos explicados com exemplos
- [ ] Diagramas de arquitetura (quando aplicável)
- [ ] Configuração paso a paso
- [ ] Casos de uso práticos
- [ ] Troubleshooting common issues

---

## 🧪 **PROMPTS DE TESTE EM PRS**

### Orientação Obrigatória

Toda contribuição que afeta algoritmos de memória deve incluir:

1. **Resultado dos 3 Prompts Padrão** (conforme README):

   ```yaml
   Prompt 1: 'Analise .cursorrules, memory-rules.mdc e memory-rating.mdc...'
   Prompt 2: 'Agora analise todo o meu projeto...'
   Prompt 3: 'A partir de agora, siga o fluxo 9 fases...'
   ```

2. **Performance Before/After**: Métricas comparativas
3. **Memory Usage**: Análise de consumo de recursos
4. **Fallback Testing**: Validação com MCPs indisponíveis

### Formato no PR

```markdown
## 🧪 Validação Memory System

**Prompts Executados:**

- [ ] Prompt 1: ✅ Gravação inicial ok (tempo: X ms)
- [ ] Prompt 2: ✅ Análise projeto ok (memórias: Y)
- [ ] Prompt 3: ✅ Ativação permanente ok

**Performance:**

- Embedding: Xms (target: <50ms)
- Reliability: X% (target: >99.9%)
```

---

## 📞 **CONTATO & SUPORTE**

### Canais de Comunicação

- **📧 Technical Issues**: [viniciusuchita@gmail.com](mailto:viniciusuchita@gmail.com)
- **💬 GitHub Discussions**: Para questões técnicas e ideias
- **🐛 Bug Reports**: GitHub Issues com reprodução detalhada
- **💼 Professional Network**: [LinkedIn](https://www.linkedin.com/in/viniciusuchita/)

### Processo de Resolução

1. **GitHub Issues**: Para bugs e solicitações de features
2. **Discussions**: Para perguntas gerais e brainstorming
3. **Email**: Apenas para questões críticas ou sensíveis

---

## 🏆 **RECONHECIMENTO**

### Sistema de Contribuições

- **🌟 Contributors**: Listados no README principal
- **💎 Memory Champions**: Algoritmos significativos implementados
- **⚡ MCP Integrators**: Novas integrações MCP
- **📚 Documentation Heroes**: Melhorias substanciais na documentação

### Oportunidades de Crescimento

- **Maintainer Status**: Para contribuições consistentes
- **Tech Lead Roles**: Liderança em áreas específicas (algoritmos, MCPs, docs)
- **Community Building**: Mentorship e suporte a novos contribuidores

---

## 📄 **LICENÇA**

Este projeto está licenciado sob **MIT License**. Ao contribuir, você concorda que suas contribuições serão licenciadas sob os mesmos termos.

```
MIT License
Copyright (c) 2025 Vinícius Uchita (Memory System Team)
```

### Contributor License Agreement

- Suas contribuições são trabalho original
- Você concede direitos de licença MIT
- Apoia excelência técnica em português
- Código atende padrões de performance especificados

---

## 👨‍💻 **MAINTAINER**

**Vinícius Uchita** - Creator & Lead Maintainer

- 🐙 **GitHub**: [@devviniuchita](https://github.com/devviniuchita)
- 💼 **LinkedIn**: [linkedin.com/in/viniciusuchita](https://www.linkedin.com/in/viniciusuchita/)
- 📧 **Email**: [viniciusuchita@gmail.com](mailto:viniciusuchita@gmail.com)
- 🎯 **Expertise**: Full-Stack Development | AI Integration (RAG, Spring AI) | Context Engineering

---

**Memory System - AI Agent Evolution Layer**

> Contribuindo para o futuro da memória inteligente em português.
