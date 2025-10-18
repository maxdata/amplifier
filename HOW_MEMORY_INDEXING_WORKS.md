# How Memory Indexing and Querying Works

**IMPORTANT**: This system uses ONLY real data - no AI generation.

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. READ REAL MESSAGES FROM SESSION FILES                       │
│                                                                 │
│ Source: ~/.claude/projects/-Users-max-Documents-GitHub-amplifier/
│                                                                 │
│ File: 64282b9c-6fd7-4841-809f-48a7bff22567.jsonl               │
│ {                                                               │
│   "message": {                                                  │
│     "role": "user",                                             │
│     "content": "you are kiding. yo still use fake data"        │
│   },                                                            │
│   "timestamp": "2025-10-18T16:26:47.504Z"                      │
│ }                                                               │
│                                                                 │
│ ✅ Real file on disk - NOT AI generated                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. STORE RAW MESSAGES (store_real_messages.py)                 │
│                                                                 │
│ File: .data/memory.json                                        │
│ {                                                               │
│   "messages": [                                                 │
│     {                                                           │
│       "id": "user_2025-10-18T16:26:47.504Z",                   │
│       "content": "you are kiding. yo still use fake data",     │
│       "role": "user",                                           │
│       "timestamp": "2025-10-18T16:26:47.504Z",                 │
│       "source": "real_session_message"                         │
│     }                                                           │
│   ]                                                             │
│ }                                                               │
│                                                                 │
│ ✅ Actual message text - NOT AI extracted/summarized           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. CREATE EMBEDDINGS INDEX                                     │
│                                                                 │
│ Using: sentence-transformers (all-MiniLM-L6-v2)                │
│                                                                 │
│ Text: "you are kiding. yo still use fake data"                 │
│   ↓                                                             │
│ model.encode(text)                                              │
│   ↓                                                             │
│ Vector: [0.042, -0.073, 0.128, ... 384 dimensions]            │
│                                                                 │
│ File: .data/embeddings.json                                    │
│ {                                                               │
│   "user_2025-10-18T16:26:47.504Z": [                          │
│     0.042, -0.073, 0.128, -0.051, ...                         │
│   ]                                                             │
│ }                                                               │
│                                                                 │
│ ✅ Vector created FROM real text - NOT AI generated            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. QUERY WITH SEMANTIC SEARCH (search_real_messages.py)        │
│                                                                 │
│ User Query: "fake data dummy data"                             │
│   ↓                                                             │
│ model.encode(query)                                             │
│   ↓                                                             │
│ Query Vector: [0.039, -0.068, 0.115, ...]                     │
│   ↓                                                             │
│ Compare with ALL stored vectors using cosine similarity:       │
│                                                                 │
│   similarity = dot(query_vec, msg_vec) /                       │
│                (norm(query_vec) * norm(msg_vec))               │
│                                                                 │
│ Results (sorted by similarity):                                │
│   1. Score: 0.760 - "you are kiding. yo still use fake data"  │
│   2. Score: 0.618 - "it seem you still use dummy data..."     │
│   3. Score: 0.615 - "remove all code and documents..."        │
│                                                                 │
│ ✅ Finds ACTUAL user messages - NOT AI summaries               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Input: Real Session Files
- **Source**: `~/.claude/projects/-Users-max-Documents-GitHub-amplifier/*.jsonl`
- **Format**: One message per file, JSON Lines format
- **Content**: Actual conversation between user and assistant
- **NO AI involved**: Direct file reads

### 2. Storage: memory.json
- **Contains**: Raw message text exactly as written
- **Structure**:
  ```json
  {
    "id": "role_timestamp",
    "content": "actual message text",
    "role": "user|assistant",
    "timestamp": "ISO 8601 timestamp",
    "source": "real_session_message"
  }
  ```
- **NO AI involved**: Direct storage of text from files

### 3. Index: embeddings.json
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Process**: Convert text → 384-dimensional vector
- **Purpose**: Enable semantic similarity search
- **Structure**:
  ```json
  {
    "message_id": [0.042, -0.073, ..., 384 numbers]
  }
  ```
- **Note**: Embeddings created FROM real text, not AI-generated

### 4. Search: Cosine Similarity
- **Input**: User query string
- **Process**:
  1. Convert query to vector (same model)
  2. Calculate cosine similarity with ALL message vectors
  3. Sort by similarity score (0.0 to 1.0)
  4. Return top N matches
- **Output**: ACTUAL messages from real conversations

## What's Different from AI Extraction?

### ❌ OLD Way (AI Extraction):
```python
# Send conversation to AI
memories = await claude.extract_memories(conversation)
# Result: AI-generated summaries like:
# "User prefers minimal complexity with modular design"
# This is SYNTHETIC content created by AI
```

### ✅ NEW Way (Real Data):
```python
# Read actual messages from disk
messages = load_from_session_files()
# Result: Exact text user/assistant actually wrote:
# "you are kiding. yo still use fake data"
# This is AUTHENTIC content from real conversations
```

## Example: Complete Search Flow

1. **User asks**: "Show me when I complained about fake data"

2. **System converts query to vector**:
   ```python
   query_vec = model.encode("fake data dummy data")
   # → [0.039, -0.068, 0.115, ...]
   ```

3. **System compares with all stored messages**:
   ```python
   for msg in messages:
       msg_vec = embeddings[msg.id]
       similarity = cosine_similarity(query_vec, msg_vec)
   ```

4. **System finds best matches**:
   ```
   0.760: "you are kiding. yo still use fake data"
   0.618: "it seem you still use dummy data not real data"
   ```

5. **Returns ACTUAL messages** - not AI summaries

## Data Authenticity Guarantees

Every message in the system can be traced to:
1. ✅ Actual `.jsonl` file in `~/.claude/projects/`
2. ✅ Real timestamp when message was sent
3. ✅ Exact text that was written (including typos)
4. ✅ Original session ID and role (user/assistant)

**No AI generation anywhere in the pipeline.**

## Running the System

```bash
# Store real messages and create index
python store_real_messages.py

# Search through real messages
python search_real_messages.py
```

## Files Created

1. `.data/memory.json` - 70 real messages from actual conversations
2. `.data/embeddings.json` - 69 vector embeddings (384D each)

Both files contain ONLY data derived from real session files.
