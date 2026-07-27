from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Iterable


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp is not timezone-aware: {value}")
    return parsed


def topological_order(node_ids: Iterable[str], edges: Iterable[tuple[str, str]]) -> tuple[str, ...]:
    nodes = set(node_ids)
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {node: 0 for node in nodes}

    for source, target in edges:
        if source not in nodes or target not in nodes:
            raise ValueError(f"edge references unknown node: {(source, target)}")
        adjacency[source].append(target)
        indegree[target] += 1

    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    ordered: list[str] = []
    while queue:
        node = queue.popleft()
        ordered.append(node)
        for target in sorted(adjacency[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)

    if len(ordered) != len(nodes):
        raise ValueError("graph contains a cycle")
    return tuple(ordered)


def ancestors(target: str, edges: Iterable[tuple[str, str]]) -> set[str]:
    reverse: dict[str, list[str]] = defaultdict(list)
    for source, destination in edges:
        reverse[destination].append(source)
    visited: set[str] = set()
    stack = list(reverse[target])
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        stack.extend(reverse[node])
    return visited


def validate_provenance_graph(
    nodes: dict[str, dict[str, Any]],
    edges: list[tuple[str, str]],
) -> dict[str, Any]:
    order = topological_order(nodes, edges)
    errors: list[str] = []

    owner_nodes = {
        node_id
        for node_id, node in nodes.items()
        if node.get("authority_role") == "OWNER"
    }
    conclusion_nodes = {
        node_id
        for node_id, node in nodes.items()
        if node.get("node_type") in {"RESULT", "CONCLUSION", "RECOMMENDATION"}
    }

    for node_id, node in nodes.items():
        if not node.get("node_type"):
            errors.append(f"{node_id}: missing node_type")
        if node.get("node_type") in {"FEATURE", "EVENT", "TEST", "RESULT"} and not node.get("method_id"):
            errors.append(f"{node_id}: missing method_id")

    for conclusion in conclusion_nodes:
        upstream = ancestors(conclusion, edges)
        if not upstream.intersection(owner_nodes):
            errors.append(f"{conclusion}: no path to OWNER data")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "topological_order": list(order),
        "owner_nodes": sorted(owner_nodes),
        "conclusion_nodes": sorted(conclusion_nodes),
    }


def latest_upstream_knowledge(
    nodes: dict[str, dict[str, Any]],
    edges: list[tuple[str, str]],
) -> dict[str, str | None]:
    order = topological_order(nodes, edges)
    parents: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        parents[target].append(source)

    latest: dict[str, datetime | None] = {}
    for node_id in order:
        own_value = nodes[node_id].get("knowledge_at_utc")
        candidates: list[datetime] = []
        if own_value:
            candidates.append(_parse_utc(str(own_value)))
        for parent in parents[node_id]:
            parent_value = latest[parent]
            if parent_value is not None:
                candidates.append(parent_value)
        latest[node_id] = max(candidates) if candidates else None

    return {
        node_id: value.isoformat().replace("+00:00", "Z") if value is not None else None
        for node_id, value in latest.items()
    }


def temporal_dependency_violations(
    nodes: dict[str, dict[str, Any]],
    edges: list[tuple[str, str]],
) -> list[dict[str, str]]:
    latest = latest_upstream_knowledge(nodes, edges)
    violations: list[dict[str, str]] = []
    for node_id, node in nodes.items():
        decision_at = node.get("decision_at_utc")
        upstream_at = latest[node_id]
        if not decision_at or not upstream_at:
            continue
        if _parse_utc(str(upstream_at)) > _parse_utc(str(decision_at)):
            violations.append(
                {
                    "node_id": node_id,
                    "latest_upstream_knowledge_at_utc": str(upstream_at),
                    "decision_at_utc": str(decision_at),
                    "reason": "UPSTREAM_INFORMATION_AVAILABLE_AFTER_DECISION",
                }
            )
    return violations
