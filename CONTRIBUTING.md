# 🚀 Contributing to Memory System

> **Welcome!** Thank you for your interest in contributing to the Memory System project. Together, we're building the future of persistent AI memory.

---

## 💖 **Welcome to Our Community**

Memory System is more than just code—it's a **movement toward persistent AI intelligence**. Whether you're fixing a bug, adding a feature, or improving documentation, every contribution helps build a more intelligent future.

### 🌟 **Our Vision**

We're creating a world where AI systems never forget, continuously learn, and provide increasingly valuable assistance to humans.

---

## 🤝 **How to Contribute**

### � **Reporting Bugs**

Found an issue? Help us fix it:

1. **Check existing issues** to avoid duplicates
2. **Use our bug report template**:
   ```
   **Bug Description**: Clear, concise description
   **Steps to Reproduce**: 1. Step one, 2. Step two...
   **Expected Behavior**: What should happen
   **Actual Behavior**: What actually happens
   **Environment**: OS, Cursor version, MCP versions
   **Memory System Version**: Current version
   ```
3. **Include logs** from `.cursor/rules/` if relevant
4. **Add labels**: bug, needs-triage

### 💡 **Suggesting Features**

Have an idea? We'd love to hear it:

1. **Open a feature request** with our template:
   ```
   **Feature Request**: Descriptive title
   **Problem Statement**: What problem does this solve?
   **Proposed Solution**: Your suggested approach
   **Alternatives Considered**: Other options you've thought about
   **Impact**: How will this benefit users?
   ```
2. **Add labels**: enhancement, needs-discussion
3. **Join the discussion** in the issue comments

### 🔧 **Your First Pull Request**

Ready to code? Here's how:

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/memory-system.git
   cd memory-system
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following our style guide
5. **Test thoroughly** (see testing requirements below)
6. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add semantic memory clustering"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request** with our template

### � **Improving Documentation**

Documentation is crucial for adoption:

- **Fix typos** and improve clarity
- **Add examples** for complex concepts
- **Update outdated information**
- **Translate content** (especially English ↔ Portuguese)
- **Create tutorials** for advanced use cases

---

## ⚡ **Technical Standards**

### 🧠 **AI/MCP Specific Requirements**

**Performance Benchmarks:**

- ⚡ Embedding Speed: <50ms
- 🎯 Reliability: >99.9%
- 🧠 Memory Retrieval: <200ms
- 💾 Storage Efficiency: <75ms neural processing

**Workflow Compliance:**

- ✅ 9-Phase Workflow: `RETRIEVE→ENRICH→EXECUTE→STORE→UPDATE→OPTIMIZE→VALIDATE→EVOLVE→SCALE`
- ✅ Dual-Brain Integration: `memory-rules.mdc` ↔ `memory-rating.mdc`
- ✅ Triple MCP Validation: [Byterover](https://www.byterover.dev/) + [Supermemory](https://mcp.supermemory.ai/) + [Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)

### 📋 **Code Style**

**Documentation Standards:**

- Portuguese for user-facing docs with international technical quality
- English for developer comments and technical specs
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) compliance

**Commit Conventions:**

```
feat: add new memory clustering algorithm
fix: resolve embedding timeout issues
docs: update installation guide
test: add memory retention test cases
refactor: optimize dual-brain coordination
```

**File Organization:**

```
memory-system/
├── memory-rules.mdc         # Execution brain (HOW)
├── memory-rating.mdc        # Quality brain (WHEN/QUALITY)
├── .cursorrules            # Router configuration
└── .cursor/rules/          # Rule storage (gitignored)
```

---

## 🧪 **Testing Requirements**

### **Memory System Tests**

Before submitting PRs, run these validation prompts:

**Test 1 - Initial Memory Creation:**

```yaml
'Analyze .cursorrules, memory-rules.mdc, and memory-rating.mdc.
Explain their interconnection and save memories of what you understood.'
```

**Test 2 - Memory Evolution:**

```yaml
'Analyze this project structure. What patterns do you see?
Store insights and update your understanding.'
```

**Test 3 - Continuous Flow:**

```yaml
'Demonstrate continuous memory workflow by retrieving previous insights,
analyzing this request, and storing new knowledge.'
```

**Expected Results:**

- ✅ All 3 MCPs active and responding
- ✅ Memory creation and retrieval working
- ✅ Dual-brain coordination functioning
- ✅ Performance within benchmarks

---

## 🎯 **Pull Request Checklist**

Before submitting your PR:

- [ ] **Code follows style guidelines**
- [ ] **All tests pass** (run the 3 validation prompts)
- [ ] **Performance benchmarks met** (<50ms, >99.9% reliability)
- [ ] **Documentation updated** if needed
- [ ] **Commit messages follow convention**
- [ ] **No breaking changes** without discussion
- [ ] **Memory system integration tested**
- [ ] **Triple MCP compatibility verified**

---

## 🌟 **Recognition & Community**

### 🏆 **Contributors Hall of Fame**

We celebrate our contributors! Outstanding contributions are recognized through:

- **GitHub profile mentions** in releases
- **Contributor badges** in documentation
- **Special thanks** in community updates
- **Priority support** for future contributions

### 📞 **Get Help**

Need assistance?

- 💬 **GitHub Discussions**: Ask questions and share ideas
- 🐛 **Issues**: Report bugs and request features
- 📧 **Email**: viniciusuchita@gmail.com for sensitive matters
- 💼 **LinkedIn**: [Vinícius Uchita](https://www.linkedin.com/in/viniciusuchita/)

---

## 📄 **Code of Conduct**

We are committed to providing a welcoming and inclusive environment. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

**In summary:**

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers and help them learn
- ✅ Focus on what's best for the community
- ✅ Show empathy toward other community members

---

## 🎉 **Thank You!**

Every contribution, no matter how small, makes Memory System better. Thank you for being part of this journey toward more intelligent AI systems.

**Ready to contribute?** 🚀 [Open your first issue](https://github.com/devviniuchita/memory-system/issues/new) or [submit a pull request](https://github.com/devviniuchita/memory-system/compare)!

---

**Memory System Community** | Built with ❤️ by contributors worldwide

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

MIT License
Copyright (c) 2025 Vinícius Uchita (Memory System Team)

```text
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

## Memory System - AI Agent Evolution Layer

> Contribuindo para o futuro da memória inteligente em português.
