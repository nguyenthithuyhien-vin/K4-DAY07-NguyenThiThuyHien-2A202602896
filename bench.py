#!/usr/bin/env python3
"""Benchmark retrieval on the Shopee e-commerce policy corpus.

Usage:
    python bench.py --strategy heading
    python bench.py --strategy recursive
    python bench.py --strategy both --ab-filter
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

from src import (
    ChunkingStrategyComparator,
    Document,
    EmbeddingStore,
    HeadingSectionChunker,
    KnowledgeBaseAgent,
    LocalEmbedder,
    RecursiveChunker,
    _mock_embed,
)

DATA_DIR = Path("data/ecommerce")
QUERIES_PATH = Path("data/benchmark_queries.json")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
# Full legal dumps drown semantic search; focused extracts stay in the bench set.
SKIP_DOC_IDS = {"shopee-terms-of-service", "shopee-quy-che-bao-hanh"}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Strip inline YAML comments like: buyer  # note
        if " #" in value:
            value = value.split(" #", 1)[0].strip()
        meta[key] = value
    return meta, match.group(2).strip()


def load_corpus(data_dir: Path) -> list[tuple[dict[str, str], str, Path]]:
    docs: list[tuple[dict[str, str], str, Path]] = []
    for path in sorted(data_dir.glob("*.md")):
        if path.name.startswith("."):
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not meta.get("doc_id") or not meta.get("audience"):
            print(f"Skipping {path}: missing doc_id/audience frontmatter", file=sys.stderr)
            continue
        if meta["doc_id"] in SKIP_DOC_IDS:
            print(f"Skipping oversized dump {path.name} (use focused extracts in bench)", file=sys.stderr)
            continue
        docs.append((meta, body, path))
    return docs


def make_chunker(strategy: str) -> Callable[[str], list[str]]:
    if strategy == "heading":
        chunker = HeadingSectionChunker(max_chars=800)
        return chunker.chunk
    if strategy == "recursive":
        chunker = RecursiveChunker(chunk_size=400, separators=["\n\n", "\n", ". ", " ", ""])
        return chunker.chunk
    raise ValueError(f"Unknown strategy: {strategy}")


def build_store(
    corpus: list[tuple[dict[str, str], str, Path]],
    strategy: str,
    embedding_fn: Callable[[str], list[float]],
) -> EmbeddingStore:
    chunk_fn = make_chunker(strategy)
    store = EmbeddingStore(collection_name=f"bench_{strategy}", embedding_fn=embedding_fn)
    documents: list[Document] = []
    for meta, body, path in corpus:
        chunks = chunk_fn(body)
        stem = meta["doc_id"]
        for index, chunk in enumerate(chunks):
            metadata = {**meta, "doc_id": stem, "source": str(path), "chunk_index": str(index)}
            documents.append(Document(id=f"{stem}#{index}", content=chunk, metadata=metadata))
    store.add_documents(documents)
    return store


def resolve_embedder(prefer_local: bool) -> tuple[Callable[[str], list[float]], str]:
    if prefer_local:
        try:
            embedder = LocalEmbedder()
            return embedder, getattr(embedder, "_backend_name", "local")
        except Exception as error:  # pragma: no cover - environment dependent
            print(f"LocalEmbedder unavailable ({error}); falling back to mock.", file=sys.stderr)
    return _mock_embed, "mock"


def default_queries() -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "query": "Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền sau khi giao thành công?",
            "gold": "15 ngày kể từ lúc đơn hàng được cập nhật giao hàng thành công; thực phẩm tươi sống và đông lạnh: 24 giờ.",
            "gold_marker": "15 (mười lăm) ngày",
            "metadata_filter": None,
            "expected_doc_id": "shopee-return-refund-policy",
        },
        {
            "id": 2,
            "query": "Shopee Đảm Bảo cho phép trả hàng hoàn tiền trong bao nhiêu ngày và xử lý khi chưa nhận được hàng?",
            "gold": "Shopee Đảm Bảo bảo vệ người mua bằng Trả hàng/Hoàn tiền trong vòng 15 ngày; nếu chưa nhận hàng có thể yêu cầu với lý do Chưa nhận được hàng.",
            "gold_marker": "Shopee Đảm Bảo",
            "metadata_filter": None,
            "expected_doc_id": "shopee-dam-bao",
        },
        {
            "id": 3,
            "query": "Trong bao lâu cần phản hồi hoặc khiếu nại quyết định hoàn tiền của Shopee?",
            "gold": "Người bán cần phản hồi/khiếu nại trong vòng 2 ngày (02 ngày lịch) kể từ khi nhận thông báo của Shopee.",
            "gold_marker": "2 ngày",
            "metadata_filter": {"audience": "seller"},
            "expected_doc_id": "shopee-seller-return-faq",
        },
        {
            "id": 4,
            "query": "Shopee có phải là bên thực hiện nghĩa vụ bảo hành sản phẩm trên sàn không?",
            "gold": "Shopee không chịu trách nhiệm bảo hành bất kỳ sản phẩm nào và không phải bên thực hiện nghĩa vụ bảo hành, trừ sản phẩm do chính Shopee đăng bán.",
            "gold_marker": "không phải là bên thực hiện nghĩa vụ bảo hành",
            "metadata_filter": None,
            "expected_doc_id": "shopee-warranty-policy",
        },
        {
            "id": 5,
            "query": "Người bán vào đâu trên Kênh Người Bán để quản lý đơn Trả hàng/Hoàn tiền/Hủy?",
            "gold": "Kênh người bán > Quản lý đơn hàng > mục Trả hàng/Hoàn tiền/Hủy.",
            "gold_marker": "Trả hàng/Hoàn tiền/Hủy",
            "metadata_filter": None,
            "expected_doc_id": "shopee-seller-return-overview",
        },
    ]


def load_queries(path: Path) -> list[dict[str, Any]]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    queries = default_queries()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queries, ensure_ascii=False, indent=2), encoding="utf-8")
    return queries


def run_baseline(corpus: list[tuple[dict[str, str], str, Path]]) -> dict[str, Any]:
    comparator = ChunkingStrategyComparator()
    report: dict[str, Any] = {}
    for meta, body, _ in corpus[:3]:
        report[meta["doc_id"]] = comparator.compare(body, chunk_size=400)
    return report


def evaluate_query(
    store: EmbeddingStore,
    agent: KnowledgeBaseAgent,
    item: dict[str, Any],
    use_filter: bool,
) -> dict[str, Any]:
    metadata_filter = item.get("metadata_filter") if use_filter else None
    if metadata_filter:
        results = store.search_with_filter(item["query"], top_k=3, metadata_filter=metadata_filter)
    else:
        results = store.search(item["query"], top_k=3)
    marker = item.get("gold_marker", "")
    relevant = any(marker.lower() in r["content"].lower() for r in results) if marker else False
    expected = item.get("expected_doc_id")
    doc_hit = any(r.get("metadata", {}).get("doc_id") == expected for r in results) if expected else False
    answer = agent.answer(item["query"], top_k=3)
    return {
        "query_id": item["id"],
        "query": item["query"],
        "filter_used": metadata_filter,
        "top3": [
            {
                "score": round(float(r["score"]), 4),
                "doc_id": r.get("metadata", {}).get("doc_id"),
                "audience": r.get("metadata", {}).get("audience"),
                "preview": r["content"][:180].replace("\n", " "),
            }
            for r in results
        ],
        "marker_in_top3": relevant,
        "expected_doc_in_top3": doc_hit,
        "agent_answer_preview": answer[:300].replace("\n", " "),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Shopee corpus retrieval benchmark")
    parser.add_argument("--strategy", choices=["heading", "recursive", "both"], default="both")
    parser.add_argument("--mock", action="store_true", help="Force mock embedder")
    parser.add_argument("--ab-filter", action="store_true", help="Also run query #3 without filter")
    parser.add_argument("--baseline", action="store_true", help="Print baseline comparator stats")
    parser.add_argument("--output", type=Path, default=Path("ket_qua_benchmark.txt"))
    args = parser.parse_args()

    corpus = load_corpus(DATA_DIR)
    if len(corpus) < 5:
        print(f"Need at least 5 corpus docs, found {len(corpus)}", file=sys.stderr)
        return 1

    queries = load_queries(QUERIES_PATH)
    embedding_fn, backend = resolve_embedder(prefer_local=not args.mock)
    strategies = ["heading", "recursive"] if args.strategy == "both" else [args.strategy]

    lines: list[str] = []
    lines.append(f"Embedding backend: {backend}")
    lines.append(f"Corpus size: {len(corpus)} documents")
    print(lines[-2])
    print(lines[-1])

    if args.baseline:
        baseline = run_baseline(corpus)
        lines.append("\n=== Baseline ChunkingStrategyComparator ===")
        for doc_id, stats in baseline.items():
            lines.append(f"\n[{doc_id}]")
            for name, info in stats.items():
                lines.append(f"  {name}: count={info['count']} avg_length={info['avg_length']:.1f}")
        print("\n".join(lines[-len(baseline) * 4 - 1 :]))

    all_results: dict[str, Any] = {"backend": backend, "strategies": {}}

    for strategy in strategies:
        store = build_store(corpus, strategy, embedding_fn)
        agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: f"[BENCH] {prompt[:240]}...")
        lines.append(f"\n=== Strategy: {strategy} | chunks={store.get_collection_size()} ===")
        print(lines[-1])
        strategy_results = []
        for item in queries:
            result = evaluate_query(store, agent, item, use_filter=True)
            strategy_results.append(result)
            lines.append(
                f"Q{item['id']} filter={result['filter_used']} "
                f"marker={result['marker_in_top3']} doc_hit={result['expected_doc_in_top3']}"
            )
            for rank, hit in enumerate(result["top3"], start=1):
                lines.append(
                    f"  {rank}. score={hit['score']} doc={hit['doc_id']} aud={hit['audience']} | {hit['preview']}"
                )
            print("\n".join(lines[-4:]))

            if args.ab_filter and item.get("metadata_filter"):
                ab = evaluate_query(store, agent, item, use_filter=False)
                strategy_results.append({**ab, "ab_no_filter": True})
                lines.append(
                    f"Q{item['id']} A/B no-filter marker={ab['marker_in_top3']} "
                    f"doc_hit={ab['expected_doc_in_top3']} top1_aud={ab['top3'][0]['audience'] if ab['top3'] else None}"
                )
                for rank, hit in enumerate(ab["top3"], start=1):
                    lines.append(
                        f"  {rank}. score={hit['score']} doc={hit['doc_id']} aud={hit['audience']} | {hit['preview']}"
                    )
                print("\n".join(lines[-4:]))

        all_results["strategies"][strategy] = strategy_results

    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path("ket_qua_benchmark.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote {args.output} and ket_qua_benchmark.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
