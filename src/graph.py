"""Stateful four-node agent. Planner → retrieve → policy → draft."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

NEWS = [
    {"title": "EU reviews EV battery recycling targets", "body": "New draft raises recovery rates for lithium and nickel."},
    {"title": "Stellantis expands Turin service analytics", "body": "Warranty logs feed a breakdown-risk model in production."},
    {"title": "Column tests cold-start ranking v4", "body": "Two-tower retrieval plus a popularity prior for brand-new stories."},
]


@dataclass
class State:
    query: str
    plan: list[str] = field(default_factory=list)
    hits: list[dict] = field(default_factory=list)
    policy_ok: bool = False
    policy_reason: str = ""
    draft: str = ""
    citations: list[str] = field(default_factory=list)


def planner(state: State) -> State:
    state.plan = [
        f"Find news overlapping: {state.query}",
        "Collect titles that can be cited",
        "Refuse to invent a headline",
    ]
    return state


def retrieve(state: State) -> State:
    q = state.query.lower().split()
    scored = []
    for doc in NEWS:
        blob = (doc["title"] + " " + doc["body"]).lower()
        score = sum(1 for t in q if t in blob)
        scored.append((score, doc))
    scored.sort(key=lambda x: -x[0])
    state.hits = [d for s, d in scored if s > 0][:3] or [scored[0][1]]
    return state


def policy(state: State) -> State:
    if not state.hits:
        state.policy_ok = False
        state.policy_reason = "no grounded hits"
        return state
    injection = any("ignore previous" in (h["body"] + h["title"]).lower() for h in state.hits)
    state.policy_ok = not injection
    state.policy_reason = "injection" if injection else "grounded"
    state.citations = [h["title"] for h in state.hits]
    return state


def draft(state: State) -> State:
    if not state.policy_ok:
        state.draft = f"Blocked by policy ({state.policy_reason})."
        return state
    bullets = "; ".join(h["title"] for h in state.hits)
    state.draft = f"Based on {len(state.hits)} sources: {bullets}."
    return state


def run(query: str, checkpoint: Path | None = None) -> State:
    state = State(query=query)
    for node in (planner, retrieve, policy, draft):
        state = node(state)
        if checkpoint:
            checkpoint.write_text(json.dumps(asdict(state), indent=2))
    return state


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "EV batteries Europe"
    out = run(q, Path("checkpoint.json"))
    print(out.draft)
    print("citations:", out.citations)
