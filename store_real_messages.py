#!/usr/bin/env python3
"""
Store REAL conversation messages from Claude Code sessions

NO AI EXTRACTION - stores actual messages as-is
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys

sys.path.insert(0, str(Path(__file__).parent))


def find_session_directory() -> Path:
    """Find the Claude Code session directory"""
    project_dir = (
        Path.home() / ".claude" / "projects" / "-Users-max-Documents-GitHub-amplifier"
    )

    if project_dir.exists():
        return project_dir

    raise FileNotFoundError("Session directory not found")


def load_real_messages(session_dir: Path, limit: int = 100) -> List[Dict]:
    """Load ACTUAL messages from session files - no AI processing"""
    print(f"\n📁 Reading from: {session_dir}")

    jsonl_files = list(session_dir.glob("*.jsonl"))
    print(f"📊 Found {len(jsonl_files)} message files")

    messages = []
    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if "message" in data:
                            msg = data["message"]
                            msg["timestamp"] = data.get("timestamp")
                            msg["session_id"] = data.get("sessionId")
                            messages.append(msg)
        except Exception as e:
            print(f"⚠️  Error reading {jsonl_file.name}: {e}")
            continue

    # Sort by timestamp
    def get_timestamp(msg):
        ts = msg.get("timestamp") or "2000-01-01T00:00:00+00:00"
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                from datetime import timezone

                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, AttributeError):
            from datetime import timezone

            return datetime.min.replace(tzinfo=timezone.utc)

    messages.sort(key=get_timestamp)

    print(f"✅ Loaded {len(messages)} messages total")
    print(f"📅 Using last {limit} messages")

    return messages[-limit:]


def extract_text_from_content(content) -> str:
    """Extract text from structured content"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return " ".join(text_parts)
    return ""


def store_messages(messages: List[Dict], data_dir: Path):
    """Store actual messages in memory.json - NO AI PROCESSING"""
    data_dir.mkdir(parents=True, exist_ok=True)
    memory_file = data_dir / "memory.json"

    print(f"\n💾 Storing {len(messages)} real messages...")

    # Convert to memory format - storing ACTUAL messages, not AI extractions
    memories = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp")

        # Skip system messages
        if role not in ["user", "assistant"]:
            continue

        # Extract text
        text = extract_text_from_content(content)

        # Skip empty messages
        if not text or len(text.strip()) < 10:
            continue

        # Store ACTUAL message
        memory = {
            "id": f"{role}_{timestamp}",
            "content": text,
            "role": role,
            "timestamp": timestamp,
            "source": "real_session_message",
            "session_id": msg.get("session_id"),
        }
        memories.append(memory)

    # Save to file
    data = {
        "messages": memories,
        "metadata": {
            "version": "3.0",
            "type": "raw_messages",
            "created": datetime.now().isoformat(),
            "count": len(memories),
            "note": "Real conversation messages - NO AI extraction/generation",
        },
    }

    with open(memory_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Stored {len(memories)} real messages")
    print(f"📝 File: {memory_file}")

    return memories


def create_embeddings_index(messages: List[Dict], data_dir: Path):
    """Create embeddings from REAL message text"""
    print("\n🧠 Creating embeddings from real messages...")

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Create embeddings for actual message content
        texts = [msg["content"] for msg in messages]
        embeddings = model.encode(texts)

        # Store embeddings
        embeddings_file = data_dir / "embeddings.json"
        embeddings_data = {
            msg["id"]: embedding.tolist()
            for msg, embedding in zip(messages, embeddings)
        }

        with open(embeddings_file, "w") as f:
            json.dump(embeddings_data, f)

        print(f"✅ Created {len(embeddings_data)} embeddings")
        print(f"📝 File: {embeddings_file}")

    except ImportError:
        print("⚠️  sentence-transformers not installed")
        print("   Run: uv add sentence-transformers")


def main():
    """Store real messages and create index"""
    print("\n" + "=" * 70)
    print("STORING REAL CONVERSATION MESSAGES")
    print("=" * 70)
    print("\nNO AI EXTRACTION - Storing actual messages as-is")

    # Find and load real messages
    session_dir = find_session_directory()
    messages = load_real_messages(session_dir, limit=200)

    # Store actual messages
    data_dir = Path(".data")
    stored_messages = store_messages(messages, data_dir)

    # Create embeddings index
    create_embeddings_index(stored_messages, data_dir)

    print("\n" + "=" * 70)
    print("✅ COMPLETE - ALL DATA IS REAL")
    print("=" * 70)
    print("\nStored actual conversation messages from:")
    print(f"  {session_dir}")
    print("\nNo AI generation or extraction was used.")


if __name__ == "__main__":
    main()
