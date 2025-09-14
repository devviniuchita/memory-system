"""
Simple harness to evaluate RAG retrieval against YAML cases.

Usage:
  ${workspaceFolder}/.venv/Scripts/python.exe tools/rag_eval.py --index-path .rag/index.vscode --profile vscode --cases tests/rag-cases.yaml

It will:
- Load test cases from YAML
- Run queries through tools/rag_indexer.py (importing its functions)
- Check expectations (min_results, step filter expectation, contains substrings)
- Print a compact report and write metrics via rag_indexer _write_metrics
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import yaml

# Allow importing sibling module
sys.path.append(str(Path(__file__).resolve().parent))
from rag_indexer import query_index  # type: ignore


def load_cases(path: Path) -> List[Dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("YAML must be a list of cases")
    return data


def run_case(case: Dict[str, Any], common: Dict[str, Any]) -> Dict[str, Any]:
    name = case.get("name") or case.get("id") or "case"
    q = case["q"]
    k = case.get("k", common.get("k", 6))
    fetch_k = case.get("fetch_k", common.get("fetch_k", 20))
    lambda_mult = case.get("lambda_mult", common.get("lambda_mult", 0.5))
    filters = {
        "filter_step": case.get("filter_step", common.get("filter_step")),
        "filter_rule_type": case.get("filter_rule_type", common.get("filter_rule_type")),
        "filter_priority": case.get("filter_priority", common.get("filter_priority")),
    }
    compress = case.get("compress", common.get("compress", False))
    sim_th = case.get("similarity_threshold", common.get("similarity_threshold", 0.25))
    rerank_llm = case.get("rerank_llm", common.get("rerank_llm"))
    rerank_top_n = case.get("rerank_top_n", common.get("rerank_top_n"))

    root = Path(common.get("root", "."))
    include_dirs = [Path(p) for p in common.get("include_dirs", [])]
    exclude_dirs = set(common.get("exclude_dirs", []))
    include_exts = set(common.get("include_exts", [])) if common.get("include_exts") else None
    ignore_files = [Path(p) for p in common.get("ignore_files", [])]

    from rag_indexer import DEFAULT_MODEL  # type: ignore
    docs = query_index(
        index_path=Path(common["index_path"]),
        q=q,
        k=k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
        filter_step=filters["filter_step"],
        filter_rule_type=filters["filter_rule_type"],
        filter_priority=filters["filter_priority"],
        compress=compress,
        similarity_threshold=sim_th,
    model_name=common.get("model") or DEFAULT_MODEL,
        root=root,
        include_dirs=include_dirs,
        exclude_dirs=exclude_dirs,
        include_exts=include_exts,
        ignore_files=ignore_files,
        out_file=Path(case["out_file"]) if case.get("out_file") else None,
        rerank_llm=rerank_llm,
        rerank_top_n=rerank_top_n,
    )

    # Assertions
    min_results = case.get("min_results")
    contains = case.get("contains") or []
    ok = True
    reasons: List[str] = []
    if isinstance(min_results, int) and len(docs) < min_results:
        ok = False
        reasons.append(f"got {len(docs)} < min_results {min_results}")
    for expect in contains:
        found = any(expect.lower() in (d.page_content or "").lower() for d in docs)
        if not found:
            ok = False
            reasons.append(f"missing substring: {expect}")

    return {
        "name": name,
        "pass": ok,
        "reasons": reasons,
        "count": len(docs),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="RAG evaluation harness")
    ap.add_argument("--index-path", type=str, required=True)
    ap.add_argument("--profile", type=str, choices=["auto", "vscode", "cursor"], default="auto")
    ap.add_argument("--cases", type=str, required=True)
    ap.add_argument("--model", type=str, default=None)
    ap.add_argument("--root", type=str, default=".")
    args = ap.parse_args()

    # Profile defaults for include dirs/exts/ignore
    root = Path(args.root)
    include_dirs = None
    include_exts = None
    ignore_files = []
    if args.profile == "vscode":
        include_dirs = [Path(".github") / "copilot-rules"]
        include_exts = {".md"}
        p = root / ".copilotignore"
        if p.exists():
            ignore_files = [p]
    elif args.profile == "cursor":
        include_dirs = [Path(".cursor") / "rules"]
        include_exts = {".mdc"}
        p = root / ".cursorignore"
        if p.exists():
            ignore_files = [p]

    common: Dict[str, Any] = {
        "index_path": args.index_path,
        "root": str(root),
        "model": args.model,
    }
    if include_dirs:
        common["include_dirs"] = [str(p) for p in include_dirs]
    if include_exts:
        common["include_exts"] = list(include_exts)
    if ignore_files:
        common["ignore_files"] = [str(p) for p in ignore_files]

    cases = load_cases(Path(args.cases))
    results = [run_case(c, common) for c in cases]

    passed = sum(1 for r in results if r["pass"])
    print(f"RAG Eval: {passed}/{len(results)} cases passed")
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        msg = "; ".join(r["reasons"]) if r["reasons"] else ""
        print(f"- {status} {r['name']} (count={r['count']}) {msg}")


if __name__ == "__main__":
    main()
