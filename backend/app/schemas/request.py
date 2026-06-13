"""Request schemas for the generation API."""

from __future__ import annotations

from typing import Literal

import pydantic


# All 23 DSA topics as an enum-like set for validation.
VALID_TOPICS = frozenset(
    [
        "arrays",
        "strings",
        "hash_tables",
        "linked_lists",
        "stacks",
        "queues",
        "trees",
        "heaps",
        "graphs",
        "tries",
        "union_find",
        "dfs",
        "bfs",
        "binary_search",
        "two_pointers",
        "sliding_window",
        "backtracking",
        "dynamic_programming",
        "greedy",
        "topological_sort",
        "prefix_sum",
        "bit_manipulation",
        "divide_and_conquer",
    ]
)

# Human-readable labels for each topic.
TOPIC_LABELS: dict[str, str] = {
    "arrays": "Arrays",
    "strings": "Strings",
    "hash_tables": "Hash Tables (Maps / Sets)",
    "linked_lists": "Linked Lists",
    "stacks": "Stacks",
    "queues": "Queues",
    "trees": "Trees (Binary Trees, BST)",
    "heaps": "Heaps (Priority Queues)",
    "graphs": "Graphs",
    "tries": "Tries",
    "union_find": "Disjoint Set (Union-Find)",
    "dfs": "Depth-First Search (DFS)",
    "bfs": "Breadth-First Search (BFS)",
    "binary_search": "Binary Search",
    "two_pointers": "Two Pointers",
    "sliding_window": "Sliding Window",
    "backtracking": "Backtracking",
    "dynamic_programming": "Dynamic Programming",
    "greedy": "Greedy Algorithms",
    "topological_sort": "Topological Sort",
    "prefix_sum": "Prefix Sum",
    "bit_manipulation": "Bit Manipulation",
    "divide_and_conquer": "Divide and Conquer",
}

LearningStyle = Literal["interview_prep", "academic", "visual", "speed_run"]


class GenerateRequest(pydantic.BaseModel):
    """Incoming request to generate a DSA learning guide.

    Attributes:
        topics: List of topic identifiers (must be from VALID_TOPICS).
        style: The learning style to adapt the guide for.
    """

    topics: list[str] = pydantic.Field(
        ..., min_length=1, max_length=23, description="DSA topic identifiers"
    )
    style: LearningStyle = pydantic.Field(
        ..., description="Learning style for the generated guide"
    )

    @pydantic.field_validator("topics")
    @classmethod
    def validate_topics(cls, v: list[str]) -> list[str]:
        invalid = [t for t in v if t not in VALID_TOPICS]
        if invalid:
            raise ValueError(f"Invalid topics: {invalid}")
        # Deduplicate while preserving order.
        seen: set[str] = set()
        deduped: list[str] = []
        for t in v:
            if t not in seen:
                seen.add(t)
                deduped.append(t)
        return deduped
