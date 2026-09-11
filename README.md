# LangGraph-style news agent

Upstream study of [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph), rewritten as a small stateful graph for **Column-style news research**.

This is not a fork of LangGraph. It is a four-node graph I own: planner → retrieval → policy → draft. The policy node is the change — it refuses to invent a headline that is not grounded in retrieved titles.

## Architecture

```
user query
    → planner (intent + sub-questions)
    → retrieval (local news index)
    → policy (grounding + injection scan)
    → draft (answer + citations)
    → state checkpoint
```

## Run

```bash
python -m src.graph "What is happening with EV batteries in Europe?"
```

No API key required — retrieval is a local index; the LLM is a stub you can swap.

## What I changed vs the tutorial graph

- Policy is a first-class node, not a regex on the system prompt.
- State carries `citations: list[str]` so a draft cannot ship without sources.
- Checkpoint is JSON on disk so a dropped run resumes.

Author: Samesun Singh ([Sam9875](https://github.com/Sam9875))
