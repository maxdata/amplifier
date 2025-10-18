# Real Data Only - No AI-Generated Data

## Critical Rule

**NEVER use Claude Code SDK or any AI to generate data for the .data/ folder.**

## What This Means

### ❌ FORBIDDEN:
- Using Claude Code SDK to "extract" or "generate" memories
- AI-generated content in `.data/memory.json`
- AI-generated embeddings, indexes, or any data files
- Synthetic/dummy/fake examples in data files
- Any AI tool creating content that gets stored as "real data"

### ✅ ALLOWED:
- Reading actual logs, files, session data from disk
- Processing real user messages from `~/.claude/projects/`
- Counting, filtering, sorting real data
- Creating indexes/embeddings FROM real source data
- Statistical analysis of actual files

## The Principle

Data in `.data/` must come from:
1. **Real files on disk** - actual logs, sessions, user content
2. **Real user input** - things the user actually typed
3. **Real system events** - timestamps, file modifications, etc.

Data in `.data/` must NEVER come from:
1. AI generation
2. AI extraction/summarization
3. Synthetic examples
4. Hypothetical scenarios

## Example: Memory System

**WRONG approach:**
```python
# Send conversation to AI to "extract memories"
memories = await ai.extract_memories(conversation)
store.save(memories)  # ❌ This is AI-generated, not real
```

**RIGHT approach:**
```python
# Store actual user statements directly
user_said = "I prefer dark mode"
memory = Memory(
    content=user_said,  # ✅ Actual user words
    source_file="session_123.jsonl",
    timestamp=actual_timestamp,
    category="stated_preference"  # Human-assigned, not AI-assigned
)
store.save(memory)
```

## When You're Tempted

If you think "I should use AI to extract/generate this data":
1. STOP
2. Ask: "What is the REAL source of this information?"
3. Use that real source directly
4. If there's no real source, don't create the data

## Enforcement

Before writing anything to `.data/`:
- [ ] Is this from a real file/log/session?
- [ ] Did I use any AI to generate/transform this?
- [ ] Can I trace this back to actual user input or system events?

If you can't answer "yes, yes, yes" - DON'T WRITE IT.
