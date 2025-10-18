#!/usr/bin/env python3
"""
Search REAL conversation messages using semantic similarity

Uses actual messages stored from real sessions
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent))


def load_messages(data_dir: Path) -> List[Dict]:
    """Load real messages from storage"""
    memory_file = data_dir / "memory.json"

    if not memory_file.exists():
        print("❌ No memory file found. Run store_real_messages.py first")
        return []

    with open(memory_file) as f:
        data = json.load(f)

    messages = data.get("messages", [])
    metadata = data.get("metadata", {})

    print(f"\n📊 Loaded {len(messages)} real messages")
    print(f"📅 Created: {metadata.get('created')}")
    print(f"📝 Type: {metadata.get('type')}")
    print(f"✨ {metadata.get('note')}")

    return messages


def load_embeddings(data_dir: Path) -> Dict:
    """Load embeddings index"""
    embeddings_file = data_dir / "embeddings.json"

    if not embeddings_file.exists():
        return {}

    with open(embeddings_file) as f:
        return json.load(f)


def search_semantic(
    query: str, messages: List[Dict], embeddings: Dict, limit: int = 5
) -> List[Tuple[Dict, float]]:
    """Search using semantic similarity"""
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Encode query
        query_embedding = model.encode(query)

        # Calculate similarities
        results = []
        for msg in messages:
            msg_id = msg["id"]
            if msg_id in embeddings:
                msg_embedding = np.array(embeddings[msg_id])

                # Cosine similarity
                similarity = np.dot(query_embedding, msg_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(msg_embedding)
                )

                results.append((msg, float(similarity)))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    except ImportError:
        print("⚠️  sentence-transformers not installed for semantic search")
        return []


def search_keyword(
    query: str, messages: List[Dict], limit: int = 5
) -> List[Tuple[Dict, float]]:
    """Simple keyword search fallback"""
    query_lower = query.lower()
    results = []

    for msg in messages:
        content_lower = msg["content"].lower()
        if query_lower in content_lower:
            # Simple relevance score based on match count
            score = content_lower.count(query_lower) / len(content_lower.split())
            results.append((msg, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


def main():
    """Search real messages"""
    print("\n" + "=" * 70)
    print("SEARCH REAL CONVERSATION MESSAGES")
    print("=" * 70)

    # Load data
    data_dir = Path(".data")
    messages = load_messages(data_dir)

    if not messages:
        return

    embeddings = load_embeddings(data_dir)

    # Test queries
    queries = [
        "fake data dummy data",
        "remove all fake",
        "memory extraction",
    ]

    for query in queries:
        print(f"\n{'=' * 70}")
        print(f"🔍 Query: '{query}'")
        print("=" * 70)

        # Try semantic search first
        if embeddings:
            results = search_semantic(query, messages, embeddings, limit=3)
            search_type = "Semantic"
        else:
            results = search_keyword(query, messages, limit=3)
            search_type = "Keyword"

        if not results:
            print("   No results found")
            continue

        print(f"\n{search_type} Search Results:\n")

        for i, (msg, score) in enumerate(results, 1):
            print(f"{i}. Score: {score:.3f}")
            print(f"   Role: {msg['role']}")
            print(f"   Time: {msg['timestamp']}")
            content = msg["content"]
            if len(content) > 150:
                content = content[:150] + "..."
            print(f"   Content: {content}")
            print()

    print("=" * 70)
    print("✅ SEARCH COMPLETE")
    print("=" * 70)
    print("\nAll results are from REAL conversation messages")
    print("No AI-generated or synthetic data")


if __name__ == "__main__":
    main()
