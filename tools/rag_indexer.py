"""
RAG Indexer & Query CLI for Markdown/MDC rules

Purpose:
- Index .md/.mdc files with header-first + character split
- Attach governance metadata (step/rule_type/priority) inferred from file names
- Persist vector store locally (FAISS preferred; fallback to Chroma)
- Query with MMR and optional contextual compression

Usage (examples):
  # Build index from repository root
  python tools/rag_indexer.py build --root . --index-path .rag/index

  # Query with MMR
  python tools/rag_indexer.py query --index-path .rag/index \
      --q "Quando devo aplicar as regras do passo 3 relacionadas a 'todo2'?" \
      --k 6 --fetch-k 24 --lambda-mult 0.5

  # Query filtering by metadata and compression
  python tools/rag_indexer.py query --index-path .rag/index \
      --q "Azure tools obrigatórios" \
      --filter-step step1 --compress --similarity-threshold 0.25

Notes:
- FAISS on Windows might require specific Python versions. If FAISS is unavailable, the script
  will automatically use Chroma as a fallback (persistent directory backend).
- SentenceTransformers will download the model on first run.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import time
import json
from fnmatch import fnmatch
from typing import Dict, Iterable, List, Optional, Tuple, Set, Any

# LangChain core deps
from langchain.schema import Document # type: ignore
from langchain_text_splitters import ( # type: ignore
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings # type: ignore

# Vector stores (FAISS preferred; Chroma fallback)
from langchain_community.vectorstores import FAISS # pyright: ignore[reportMissingImports]

try:
    # Chroma is optional; used as fallback
    from langchain_community.vectorstores import Chroma  # type: ignore
    CHROMA_AVAILABLE = True
except Exception:  # pragma: no cover - best effort import
    CHROMA_AVAILABLE = False

# Retrieval & compression
from langchain.retrievers import ContextualCompressionRetriever # pyright: ignore[reportMissingImports]
from langchain.retrievers.document_compressors import EmbeddingsFilter # type: ignore


# ---------------------------- Configuration ---------------------------- #
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_INDEX_PATH = ".rag/index"
EXCLUDE_DIRS = {".git", "node_modules", "dist", "build", "images", ".rag", ".venv"}
INCLUDE_EXTS = {".md", ".mdc"}


def debug(msg: str) -> None:
    print(f"[rag] {msg}")


def _is_under(child: Path, base: Path) -> bool:
    try:
        child.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def _parse_ignore_files(ignore_files: List[Path]) -> Set[str]:
    """Retorna padrões de ignore (com suporte a globs) a partir de arquivos como .copilotignore/.cursorignore.

    - Ignora linhas vazias e que começam com '#'
    - Remove barra final para normalizar, mas mantém o padrão para matching por caminho
    - Mantém curingas (*, ?, []) quando presentes
    """
    entries: Set[str] = set()
    for f in ignore_files:
        try:
            if not f.exists():
                continue
            for line in f.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                s = s.rstrip("/\\")
                if s:
                    entries.add(s)
        except Exception as e:
            debug(f"Aviso: falha ao ler ignore '{f}': {e}")
    return entries


def iter_files(
    root: Path,
    include_dirs: Optional[List[Path]] = None,
    exclude_dirs: Optional[Set[str]] = None,
    include_exts: Optional[Set[str]] = None,
) -> Iterable[Path]:
    base_exclude = set(EXCLUDE_DIRS)
    if exclude_dirs:
        base_exclude |= {d.strip() for d in exclude_dirs if d}

    exts = set(INCLUDE_EXTS)
    if include_exts:
        exts = {e if e.startswith('.') else f'.{e}' for e in include_exts}

    # Se include_dirs fornecido, iterar somente nelas; caso contrário, varrer root inteiro
    scan_roots = [root]
    if include_dirs:
        scan_roots = [d if d.is_absolute() else (root / d) for d in include_dirs]

    for sr in scan_roots:
        if not sr.exists():
            debug(f"Aviso: include-dir não encontrado: {sr}")
            continue
        for p in sr.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in exts:
                continue
            parts = set(p.parts)
            if parts & base_exclude:
                continue
            # Excludes via patterns (globs) vindos de ignore/exclude_dirs
            if exclude_dirs:
                rel = str(p.relative_to(root)).replace("\\", "/")
                blocked = False
                for pat in exclude_dirs:
                    if any(ch in pat for ch in ("*", "?", "[")):
                        if fnmatch(rel, pat):
                            blocked = True
                            break
                    else:
                        if pat in parts:
                            blocked = True
                            break
                if blocked:
                    continue
            # Se include_dirs foi usado explicitamente, garanta que o arquivo esteja dentro de sr
            if include_dirs and not _is_under(p, sr):
                continue
            yield p
        # bloco legado removido (evita yields duplicados)


def load_documents(paths: Iterable[Path]) -> List[Document]:
    from langchain_community.document_loaders import TextLoader # type: ignore

    docs: List[Document] = []
    for p in paths:
        try:
            loader = TextLoader(str(p), encoding="utf-8")
            docs.extend(loader.load())
            debug(f"Carregado: {p}")
        except Exception as e:  # robust to encoding or transient errors
            debug(f"Erro ao carregar {p}: {e}")
    debug(f"Total de documentos base: {len(docs)}")
    return docs


def split_markdown(docs: List[Document]) -> List[Document]:
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    header_chunks: List[Document] = []
    for d in docs:
        try:
            parts = md_splitter.split_text(d.page_content)
            for part in parts:
                part.metadata = {**d.metadata}
            header_chunks.extend(parts)
        except Exception:
            header_chunks.append(d)
    debug(f"Chunks por cabeçalho: {len(header_chunks)}")
    return header_chunks


def split_char(chunks: List[Document], chunk_size: int = 800, chunk_overlap: int = 120) -> List[Document]:
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    final_chunks: List[Document] = []
    for h in chunks:
        parts = char_splitter.split_text(h.page_content)
        for content in parts:
            final_chunks.append(Document(page_content=content, metadata=h.metadata))
    debug(f"Chunks finais após split recursivo: {len(final_chunks)}")
    return final_chunks


def classify_rule(file_path: str) -> Dict[str, str]:
    name = file_path.lower()
    step = "unknown"
    priority = "normal"
    rule_type = "unknown"

    if "behavioral-rules" in name:
        step, rule_type, priority = "step1", "always-apply", "high"
    elif "methodology-rules" in name:
        step, rule_type, priority = "step1", "always-apply", "high"
    elif "tools-rules" in name:
        step, rule_type, priority = "step1", "always-apply", "high"
    elif "mcp-rules" in name:
        step, rule_type, priority = "step1", "always-apply", "high"
    elif "project-rules" in name or "project-codification" in name:
        step, rule_type, priority = "step2", "apply-manually", "normal"
    elif "todo2" in name:
        step, rule_type, priority = "step3", "specific-files", "normal"
    elif "memory-rules" in name or "memory-rating" in name:
        step, rule_type, priority = "step5", "continuous-learning", "high"

    return {"step": step, "rule_type": rule_type, "priority": priority}


def attach_metadata(chunks: List[Document]) -> None:
    for c in chunks:
        file_path = c.metadata.get("source") or c.metadata.get("file_path") or ""
        meta = classify_rule(str(file_path))
        c.metadata.update(meta)
        c.metadata["file_path"] = str(file_path)


def build_index(
    root: Path,
    index_path: Path,
    model_name: str = DEFAULT_MODEL,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    include_dirs: Optional[List[Path]] = None,
    exclude_dirs: Optional[Set[str]] = None,
    include_exts: Optional[Set[str]] = None,
    ignore_files: Optional[List[Path]] = None,
) -> Tuple[str, int]:
    # Ignora via arquivos (ex.: .copilotignore, .cursorignore)
    ignore_entries: Set[str] = set()
    if ignore_files:
        ignore_entries = _parse_ignore_files(ignore_files)

    eff_exclude = set(exclude_dirs or set()) | ignore_entries

    t0 = time.perf_counter()
    paths = list(iter_files(root, include_dirs=include_dirs, exclude_dirs=eff_exclude, include_exts=include_exts))
    docs = load_documents(paths)
    header_chunks = split_markdown(docs)
    final_chunks = split_char(header_chunks, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    attach_metadata(final_chunks)

    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Try FAISS first
    try:
        vs = FAISS.from_documents(final_chunks, embeddings)
        vs.save_local(str(index_path))
        backend = "faiss"
        debug(f"Índice FAISS salvo em: {index_path}")
    except Exception as e:
        if not CHROMA_AVAILABLE:
            raise RuntimeError(
                f"Falha ao criar índice FAISS e Chroma não disponível: {e}"
            )
        # Fallback to Chroma persistent store
        debug(f"FAISS indisponível ({e}). Usando Chroma como fallback.")
        vs = Chroma.from_documents(
            final_chunks,
            embedding=embeddings,
            persist_directory=str(index_path),
        )
        vs.persist()
        backend = "chroma"
        debug(f"Índice Chroma persistido em: {index_path}")

    # métricas
    try:
        _write_metrics({
            "type": "build",
            "index_path": str(index_path),
            "backend": backend,
            "docs": len(docs),
            "chunks": len(final_chunks),
            "duration_s": round(time.perf_counter() - t0, 4),
            "timestamp": time.time(),
        })
    except Exception:
        pass
    return backend, len(final_chunks)


def load_index(index_path: Path, model_name: str = DEFAULT_MODEL):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # Try to load FAISS
    try:
        vs = FAISS.load_local(
            str(index_path), embeddings, allow_dangerous_deserialization=True
        )
        return vs, "faiss", embeddings
    except Exception:
        pass

    if CHROMA_AVAILABLE:
        try:
            vs = Chroma(
                embedding_function=embeddings,
                persist_directory=str(index_path),
            )
            return vs, "chroma", embeddings
        except Exception:
            pass

    raise RuntimeError(
        f"Não foi possível carregar o índice em {index_path}. Verifique o backend e o caminho."
    )


def query_index(
    index_path: Path,
    q: str,
    k: int = 6,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
    filter_step: Optional[str] = None,
    filter_rule_type: Optional[str] = None,
    filter_priority: Optional[str] = None,
    compress: bool = False,
    similarity_threshold: float = 0.25,
    model_name: str = DEFAULT_MODEL,
    root: Optional[Path] = None,
    include_dirs: Optional[List[Path]] = None,
    exclude_dirs: Optional[Set[str]] = None,
    include_exts: Optional[Set[str]] = None,
    ignore_files: Optional[List[Path]] = None,
    # pós-processamento
    out_file: Optional[Path] = None,
    rerank_llm: Optional[str] = None,
    rerank_top_n: Optional[int] = None,
) -> List[Document]:
    vs, backend, embeddings = load_index(index_path, model_name=model_name)
    q_start = time.perf_counter()

    # Build base retriever with MMR
    retriever = vs.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult},
    )

    # Metadata pre-filtering by re-ranking (client-side filter after retrieval)
    def metadata_filter(docs: List[Document]) -> List[Document]:
        def ok(d: Document) -> bool:
            if filter_step and d.metadata.get("step") != filter_step:
                return False
            if filter_rule_type and d.metadata.get("rule_type") != filter_rule_type:
                return False
            if filter_priority and d.metadata.get("priority") != filter_priority:
                return False
            return True

        return [d for d in docs if ok(d)]

    # Optional compression
    if compress:
        compressor = EmbeddingsFilter(
            embeddings=embeddings, similarity_threshold=similarity_threshold
        )
        c_retriever: ContextualCompressionRetriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )
        raw_docs = c_retriever.invoke(q)
    else:
        raw_docs = retriever.invoke(q)

    docs = metadata_filter(raw_docs)

    # Optional path/extension/ignore filtering (client-side)
    if any([include_dirs, exclude_dirs, include_exts, ignore_files]):
        base_root = root or Path(".")
        ignore_entries: Set[str] = set()
        if ignore_files:
            ignore_entries = _parse_ignore_files(ignore_files)
        eff_exclude = set(exclude_dirs or set()) | ignore_entries

        def path_ok(fp: Optional[str]) -> bool:
            if not fp:
                return False
            p = Path(fp)
            if not p.is_absolute():
                p = (base_root / p).resolve()
            # include_dirs: manter apenas dentro de algum include dir
            inside_any = True
            if include_dirs:
                inside_any = False
                for d in include_dirs:
                    d_abs = d if d.is_absolute() else (base_root / d)
                    try:
                        p.resolve().relative_to(d_abs.resolve())
                        inside_any = True
                        break
                    except Exception:
                        pass
                if not inside_any:
                    return False
            # exclude/ignore dirs NÃO sobrepõem include_dirs (se inside_any True, só verificamos exts)
            if not include_dirs:
                parts = set(p.parts)
                if parts & eff_exclude:
                    return False
            # include_exts
            if include_exts:
                exts = {e if e.startswith('.') else f'.{e}' for e in include_exts}
                if p.suffix.lower() not in exts:
                    return False
            return True

        docs = [d for d in docs if path_ok(d.metadata.get("file_path"))]

    # Optional LLM-based reranking (best-effort)
    if rerank_llm and rerank_llm.lower() == "google" and docs:
        try:
            ranked = _google_rerank(q, docs, top_n=rerank_top_n or len(docs))
            if ranked:
                docs = ranked
        except Exception as e:
            debug(f"Rerank (google) falhou: {e}")

    # Optional aggregated output file
    if out_file:
        try:
            _write_aggregated_output(out_file, q, docs)
        except Exception as e:
            debug(f"Falha ao escrever out-file: {e}")
    # métricas de query
    try:
        by_step: Dict[str, int] = {}
        for d in docs:
            s = d.metadata.get("step", "unknown")
            by_step[s] = by_step.get(s, 0) + 1
        _write_metrics({
            "type": "query",
            "index_path": str(index_path),
            "backend": backend,
            "k": k,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult,
            "filter_step": filter_step,
            "filter_rule_type": filter_rule_type,
            "filter_priority": filter_priority,
            "compress": compress,
            "similarity_threshold": similarity_threshold,
            "duration_s": round(time.perf_counter() - q_start, 4),
            "result_count": len(docs),
            "by_step": by_step,
            "timestamp": time.time(),
        })
    except Exception:
        pass
    return docs


def print_results(docs: List[Document], limit_chars: int = 500) -> None:
    print("\n=== RESULTADOS ===")
    if not docs:
        print("(vazio)")
        return
    for i, r in enumerate(docs, 1):
        fp = r.metadata.get("file_path")
        step = r.metadata.get("step")
        rtype = r.metadata.get("rule_type")
        pri = r.metadata.get("priority")
        print(f"[{i}] {fp} | step={step} | type={rtype} | priority={pri}")
        print((r.page_content or "").strip()[:limit_chars], "\n")


# ------------------------------- CLI ---------------------------------- #
def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="RAG Indexer & Query for Markdown/MDC rules")
    sub = p.add_subparsers(dest="cmd", required=True)

    # build
    pb = sub.add_parser("build", help="Construir índice vetorial")
    pb.add_argument("--root", type=str, default=".", help="Diretório raiz para varredura")
    pb.add_argument("--index-path", type=str, default=DEFAULT_INDEX_PATH, help="Caminho do índice (pasta)")
    pb.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Modelo de embeddings")
    pb.add_argument("--chunk-size", type=int, default=800, help="Tamanho do chunk de caracteres")
    pb.add_argument("--chunk-overlap", type=int, default=120, help="Overlap entre chunks")
    pb.add_argument("--profile", type=str, choices=["auto", "vscode", "cursor"], default="auto", help="Perfil de IDE para varredura (auto/vscode/cursor)")
    pb.add_argument("--include-dirs", type=str, nargs="*", default=None, help="Pastas (relativas ao root) a incluir na varredura")
    pb.add_argument("--exclude-dirs", type=str, nargs="*", default=None, help="Pastas a excluir (nomes ou caminhos)")
    pb.add_argument("--ignore-files", type=str, nargs="*", default=None, help="Arquivos de ignore a considerar (ex.: .copilotignore, .cursorignore)")
    pb.add_argument("--include-exts", type=str, nargs="*", default=None, help="Extensões a incluir (ex.: .md .mdc)")

    # query
    pq = sub.add_parser("query", help="Consultar índice vetorial")
    pq.add_argument("--index-path", type=str, default=DEFAULT_INDEX_PATH, help="Caminho do índice (pasta)")
    pq.add_argument("--q", type=str, required=True, help="Consulta (query)")
    pq.add_argument("--k", type=int, default=6, help="Top-k (MMR)")
    pq.add_argument("--fetch-k", type=int, default=20, help="Fetch_k (MMR)")
    pq.add_argument("--lambda-mult", type=float, default=0.5, help="Lambda MMR (0..1)")
    pq.add_argument("--filter-step", type=str, default=None, help="Filtrar por step (ex.: step1, step2, step3, step5)")
    pq.add_argument("--filter-rule-type", type=str, default=None, help="Filtrar por rule_type (ex.: always-apply)")
    pq.add_argument("--filter-priority", type=str, default=None, help="Filtrar por priority (ex.: high, normal)")
    pq.add_argument("--compress", action="store_true", help="Ativar compressão contextual (EmbeddingsFilter)")
    pq.add_argument("--similarity-threshold", type=float, default=0.25, help="Threshold para compressor")
    pq.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Modelo de embeddings")
    pq.add_argument("--root", type=str, default=".", help="Diretório raiz para resolução de caminhos")
    pq.add_argument("--profile", type=str, choices=["auto", "vscode", "cursor"], default="auto", help="Perfil de IDE para filtros (auto/vscode/cursor)")
    pq.add_argument("--include-dirs", type=str, nargs="*", default=None, help="Pastas (relativas ao root) a restringir resultados")
    pq.add_argument("--exclude-dirs", type=str, nargs="*", default=None, help="Pastas a excluir (nomes ou caminhos)")
    pq.add_argument("--ignore-files", type=str, nargs="*", default=None, help="Arquivos de ignore a considerar (ex.: .copilotignore, .cursorignore)")
    pq.add_argument("--include-exts", type=str, nargs="*", default=None, help="Extensões a permitir (ex.: .md .mdc)")
    # pós-processamento
    pq.add_argument("--out-file", type=str, default=None, help="Arquivo para salvar o contexto agregado dos resultados")
    pq.add_argument("--rerank-llm", type=str, choices=["google"], default=None, help="LLM para reranking opcional")
    pq.add_argument("--rerank-top-n", type=int, default=None, help="Limitar top-N após reranking")

    # watch (subcomando)
    pw = sub.add_parser("watch", help="Monitorar alterações e reconstruir índice (polling por mtime)")
    pw.add_argument("--root", type=str, default=".", help="Diretório raiz para varredura")
    pw.add_argument("--index-path", type=str, default=DEFAULT_INDEX_PATH, help="Caminho do índice (pasta)")
    pw.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Modelo de embeddings")
    pw.add_argument("--chunk-size", type=int, default=800, help="Tamanho do chunk de caracteres")
    pw.add_argument("--chunk-overlap", type=int, default=120, help="Overlap entre chunks")
    pw.add_argument("--profile", type=str, choices=["auto", "vscode", "cursor"], default="auto", help="Perfil de IDE para varredura")
    pw.add_argument("--include-dirs", type=str, nargs="*", default=None, help="Pastas (relativas ao root) a incluir na varredura")
    pw.add_argument("--exclude-dirs", type=str, nargs="*", default=None, help="Pastas a excluir (nomes ou caminhos)")
    pw.add_argument("--ignore-files", type=str, nargs="*", default=None, help="Arquivos de ignore a considerar")
    pw.add_argument("--include-exts", type=str, nargs="*", default=None, help="Extensões a incluir (ex.: .md .mdc)")
    pw.add_argument("--interval", type=float, default=2.0, help="Intervalo de polling em segundos")
    pw.add_argument("--quiet", action="store_true", help="Silenciar logs de varredura sem mudanças")

    return p


def main() -> None:
    args = make_parser().parse_args()

    if args.cmd == "build":
        # Resolve perfil
        profile = getattr(args, "profile", "auto")
        include_dirs = args.include_dirs
        include_exts = set(args.include_exts) if args.include_exts else None
        exclude_dirs = set(args.exclude_dirs) if args.exclude_dirs else None
        ignore_files = [Path(f) for f in (args.ignore_files or [])]

        # Smart auto detection
        if profile == "auto":
            root_path = Path(args.root)
            copilot_ign = root_path / ".copilotignore"
            cursor_ign = root_path / ".cursorignore"
            vscode_dir = root_path / ".github" / "copilot-rules"
            cursor_dir = root_path / ".cursor" / "rules"
            chosen = None
            if copilot_ign.exists() and vscode_dir.exists():
                chosen = "vscode"
            elif cursor_ign.exists() and cursor_dir.exists():
                chosen = "cursor"
            # if both exist, prefer vscode by default
            if chosen == "vscode":
                include_dirs = include_dirs or [Path(".github") / "copilot-rules"]
                include_exts = include_exts or {".md"}
                if not ignore_files and copilot_ign.exists():
                    ignore_files = [copilot_ign]
                debug("[auto] Perfil VSCode detectado por .copilotignore e .github/copilot-rules")
            elif chosen == "cursor":
                include_dirs = include_dirs or [Path(".cursor") / "rules"]
                include_exts = include_exts or {".mdc"}
                if not ignore_files and cursor_ign.exists():
                    ignore_files = [cursor_ign]
                debug("[auto] Perfil Cursor detectado por .cursorignore e .cursor/rules")
        elif profile == "vscode":
            # Defaults VSCode: regras em .github/copilot-rules/*.md e ignora .copilotignore
            if include_dirs is None:
                include_dirs = [Path(".github") / "copilot-rules"]
            if not ignore_files:
                p = Path(args.root) / ".copilotignore"
                if p.exists():
                    ignore_files = [p]
            if include_exts is None:
                include_exts = {".md"}
        elif profile == "cursor":
            # Defaults Cursor: regras em .cursor/rules/*.mdc e ignora .cursorignore
            if include_dirs is None:
                include_dirs = [Path(".cursor") / "rules"]
            if not ignore_files:
                p = Path(args.root) / ".cursorignore"
                if p.exists():
                    ignore_files = [p]
            if include_exts is None:
                include_exts = {".mdc"}

        backend, n_chunks = build_index(
            root=Path(args.root),
            index_path=Path(args.index_path),
            model_name=args.model,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
            include_exts=include_exts,
            ignore_files=ignore_files,
        )
        debug(f"Build concluído. Backend: {backend} | Chunks: {n_chunks}")
    elif args.cmd == "query":
        # Resolve perfil e filtros
        profile = getattr(args, "profile", "auto")
        include_dirs = args.include_dirs
        include_exts = set(args.include_exts) if args.include_exts else None
        exclude_dirs = set(args.exclude_dirs) if args.exclude_dirs else None
        ignore_files = [Path(f) for f in (args.ignore_files or [])]

        if profile == "auto":
            root_path = Path(args.root)
            copilot_ign = root_path / ".copilotignore"
            cursor_ign = root_path / ".cursorignore"
            vscode_dir = root_path / ".github" / "copilot-rules"
            cursor_dir = root_path / ".cursor" / "rules"
            chosen = None
            if copilot_ign.exists() and vscode_dir.exists():
                chosen = "vscode"
            elif cursor_ign.exists() and cursor_dir.exists():
                chosen = "cursor"
            if chosen == "vscode":
                include_dirs = include_dirs or [Path(".github") / "copilot-rules"]
                include_exts = include_exts or {".md"}
                if not ignore_files and copilot_ign.exists():
                    ignore_files = [copilot_ign]
                debug("[auto] (query) Perfil VSCode detectado")
            elif chosen == "cursor":
                include_dirs = include_dirs or [Path(".cursor") / "rules"]
                include_exts = include_exts or {".mdc"}
                if not ignore_files and cursor_ign.exists():
                    ignore_files = [cursor_ign]
                debug("[auto] (query) Perfil Cursor detectado")
        elif profile == "vscode":
            if include_dirs is None:
                include_dirs = [Path(".github") / "copilot-rules"]
            if not ignore_files:
                p = Path(args.root) / ".copilotignore"
                if p.exists():
                    ignore_files = [p]
            if include_exts is None:
                include_exts = {".md"}
        elif profile == "cursor":
            if include_dirs is None:
                include_dirs = [Path(".cursor") / "rules"]
            if not ignore_files:
                p = Path(args.root) / ".cursorignore"
                if p.exists():
                    ignore_files = [p]
            if include_exts is None:
                include_exts = {".mdc"}

        results = query_index(
            index_path=Path(args.index_path),
            q=args.q,
            k=args.k,
            fetch_k=args.fetch_k,
            lambda_mult=args.lambda_mult,
            filter_step=args.filter_step,
            filter_rule_type=args.filter_rule_type,
            filter_priority=args.filter_priority,
            compress=args.compress,
            similarity_threshold=args.similarity_threshold,
            model_name=args.model,
            root=Path(args.root),
            include_dirs=[Path(d) for d in (include_dirs or [])],
            exclude_dirs=exclude_dirs,
            include_exts=include_exts,
            ignore_files=ignore_files,
            out_file=Path(args.out_file) if getattr(args, "out_file", None) else None,
            rerank_llm=getattr(args, "rerank_llm", None),
            rerank_top_n=getattr(args, "rerank_top_n", None),
        )
        print_results(results)
    elif args.cmd == "watch":
        # Resolve perfil padrão semelhante ao build
        profile = getattr(args, "profile", "auto")
        include_dirs = args.include_dirs
        include_exts = set(args.include_exts) if args.include_exts else None
        exclude_dirs = set(args.exclude_dirs) if args.exclude_dirs else None
        ignore_files = [Path(f) for f in (args.ignore_files or [])]

        if profile == "auto":
            root_path = Path(args.root)
            copilot_ign = root_path / ".copilotignore"
            cursor_ign = root_path / ".cursorignore"
            vscode_dir = root_path / ".github" / "copilot-rules"
            cursor_dir = root_path / ".cursor" / "rules"
            chosen = None
            if copilot_ign.exists() and vscode_dir.exists():
                chosen = "vscode"
            elif cursor_ign.exists() and cursor_dir.exists():
                chosen = "cursor"
            if chosen == "vscode":
                include_dirs = include_dirs or [Path(".github") / "copilot-rules"]
                include_exts = include_exts or {".md"}
                if not ignore_files and copilot_ign.exists():
                    ignore_files = [copilot_ign]
                debug("[auto] (watch) Perfil VSCode detectado")
            elif chosen == "cursor":
                include_dirs = include_dirs or [Path(".cursor") / "rules"]
                include_exts = include_exts or {".mdc"}
                if not ignore_files and cursor_ign.exists():
                    ignore_files = [cursor_ign]
                debug("[auto] (watch) Perfil Cursor detectado")
        elif profile == "vscode":
            if include_dirs is None:
                include_dirs = [Path(".github") / "copilot-rules"]
            if not ignore_files:
                p = Path(args.root) / ".copilotignore"
                if p.exists():
                    ignore_files = [p]
            if include_exts is None:
                include_exts = {".md"}
        elif profile == "cursor":
            if include_dirs is None:
                include_dirs = [Path(".cursor") / "rules"]
            if not ignore_files:
                p = Path(args.root) / ".cursorignore"
                if p.exists():
                    ignore_files = [p]
            if include_exts is None:
                include_exts = {".mdc"}

        _watch_loop(
            root=Path(args.root),
            index_path=Path(args.index_path),
            model_name=args.model,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            include_dirs=[Path(d) for d in (include_dirs or [])],
            exclude_dirs=set(exclude_dirs or set()),
            include_exts=set(include_exts or set()),
            ignore_files=ignore_files,
            interval=args.interval,
            quiet=args.quiet,
        )
    else:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

# -------------------------- Utilidades internas -------------------------- #
_METRICS_FILE = ".rag/metrics.jsonl"

def _set_metrics_file(path: str) -> None:
    """Define o caminho padrão do arquivo de métricas JSONL."""
    global _METRICS_FILE
    _METRICS_FILE = path or _METRICS_FILE

def _write_metrics(rec: Dict) -> None:
    """Grava uma linha JSON com métricas de build/query em _METRICS_FILE."""
    try:
        p = Path(_METRICS_FILE)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        debug(f"Falha ao escrever métricas: {e}")


# -------------------------- Utilidades complementares -------------------------- #
def _snapshot_files(
    root: Path,
    include_dirs: List[Path],
    exclude_dirs: Set[str],
    include_exts: Set[str],
    ignore_files: Optional[List[Path]] = None,
) -> Dict[str, Tuple[float, int]]:
    """Retorna um snapshot {rel_path: (mtime, size)} dos arquivos relevantes."""
    ignore_entries: Set[str] = set()
    if ignore_files:
        ignore_entries = _parse_ignore_files(ignore_files)
    eff_exclude = set(exclude_dirs or set()) | ignore_entries
    files = iter_files(root, include_dirs=include_dirs, exclude_dirs=eff_exclude, include_exts=include_exts)
    snap: Dict[str, Tuple[float, int]] = {}
    for p in files:
        try:
            st = p.stat()
            rel = str(p.relative_to(root)).replace("\\", "/")
            snap[rel] = (st.st_mtime, st.st_size)
        except Exception:
            continue
    return snap


def _watch_loop(
    root: Path,
    index_path: Path,
    model_name: str,
    chunk_size: int,
    chunk_overlap: int,
    include_dirs: List[Path],
    exclude_dirs: Set[str],
    include_exts: Set[str],
    ignore_files: Optional[List[Path]],
    interval: float,
    quiet: bool,
) -> None:
    debug(f"Watch iniciado em {root} | index={index_path} | interval={interval}s")
    last_snap = _snapshot_files(root, include_dirs, exclude_dirs, include_exts, ignore_files)
    while True:
        time.sleep(max(0.2, interval))
        snap = _snapshot_files(root, include_dirs, exclude_dirs, include_exts, ignore_files)
        if snap != last_snap:
            created = set(snap) - set(last_snap)
            deleted = set(last_snap) - set(snap)
            changed = {
                k for k in (set(snap) & set(last_snap))
                if snap[k] != last_snap[k]
            }
            debug(f"Mudanças detectadas: +{len(created)} ~{len(changed)} -{len(deleted)} → rebuild")
            t0 = time.perf_counter()
            backend, n_chunks = build_index(
                root=root,
                index_path=index_path,
                model_name=model_name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                include_dirs=include_dirs,
                exclude_dirs=exclude_dirs,
                include_exts=include_exts,
                ignore_files=ignore_files,
            )
            _write_metrics({
                "type": "watch_build",
                "index_path": str(index_path),
                "backend": backend,
                "duration_s": round(time.perf_counter() - t0, 4),
                "timestamp": time.time(),
                "created": len(created),
                "changed": len(changed),
                "deleted": len(deleted),
            })
            last_snap = snap
        elif not quiet:
            debug("Nenhuma mudança…")


def _write_aggregated_output(path: Path, query: str, docs: List[Document], limit_chars: int = 2000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# Consulta\n{query}\n\n")
        for i, d in enumerate(docs, 1):
            fp = d.metadata.get("file_path")
            step = d.metadata.get("step")
            rtype = d.metadata.get("rule_type")
            pri = d.metadata.get("priority")
            f.write(f"## [{i}] {fp} | step={step} | type={rtype} | priority={pri}\n")
            f.write((d.page_content or "").strip()[:limit_chars])
            f.write("\n\n")


def _google_rerank(query: str, docs: List[Document], top_n: int) -> List[Document]:
    """Reranking simples com Gemini: pede ao modelo para ordenar trechos por relevância.
    Requer env GOOGLE_API_KEY e langchain-google-genai instalado. Fallback: retorna docs originais."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
    except Exception as e:
        debug(f"langchain-google-genai não disponível: {e}")
        return docs
    import os
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        debug("GOOGLE_API_KEY ausente; ignorando rerank")
        return docs

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

    # Monta prompt compacto
    items = []
    for i, d in enumerate(docs, 1):
        txt = (d.page_content or "").replace("\n", " ")
        items.append(f"[{i}] {txt[:500]}")
    prompt = (
        "Você é um reranker. Ordene por relevância à consulta a lista abaixo e retorne apenas os índices, separados por vírgula.\n"
        f"Consulta: {query}\n"
        "Documentos:\n" + "\n".join(items) + "\n"
        "Responda: 1,5,3...\n"
    )
    try:
        resp = llm.invoke(prompt)
        text = getattr(resp, "content", None) or getattr(resp, "text", "") or str(resp)
        # extrai números
        import re
        idxs = [int(x) for x in re.findall(r"\d+", text)]
        # mantém ordem única e válida
        seen = set()
        order = []
        for i in idxs:
            if 1 <= i <= len(docs) and i not in seen:
                seen.add(i)
                order.append(i)
        if not order:
            return docs
        ordered = [docs[i-1] for i in order]
        if top_n and top_n > 0:
            ordered = ordered[:top_n]
        return ordered
    except Exception as e:
        debug(f"Falha no Gemini rerank: {e}")
        return docs
