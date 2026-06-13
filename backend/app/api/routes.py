"""API routes for the DSA guide generator.

Exposes:
  POST /api/generate — Streams a DSA learning guide via SSE.
  GET  /api/health   — Health check endpoint.
  GET  /api/topics   — Returns available topics and labels.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.orchestrator import generate_guide
from app.db import get_guide, list_guides
from app.schemas.request import GenerateRequest, TOPIC_LABELS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/topics")
async def get_topics():
    """Return the list of available DSA topics with labels.

    Returns a structured list the frontend can use to render the
    topic selector without hardcoding topic data.
    """
    # Group topics by category for the frontend.
    data_structures = [
        "arrays", "strings", "hash_tables", "linked_lists",
        "stacks", "queues", "trees", "heaps", "graphs", "tries", "union_find",
    ]
    algorithms = [
        "dfs", "bfs", "binary_search", "two_pointers", "sliding_window",
        "backtracking", "dynamic_programming", "greedy", "topological_sort",
        "prefix_sum", "bit_manipulation", "divide_and_conquer",
    ]

    return {
        "categories": [
            {
                "name": "Data Structures",
                "topics": [
                    {"id": t, "label": TOPIC_LABELS[t]} for t in data_structures
                ],
            },
            {
                "name": "Algorithms & Techniques",
                "topics": [
                    {"id": t, "label": TOPIC_LABELS[t]} for t in algorithms
                ],
            },
        ],
        "styles": [
            {"id": "interview_prep", "label": "Interview Prep", "icon": "🎯", "description": "Patterns, complexity analysis, and common interview variations"},
            {"id": "academic", "label": "Academic Deep-Dive", "icon": "📚", "description": "Formal definitions, proofs, and mathematical analysis"},
            {"id": "visual", "label": "Visual / Intuitive", "icon": "🧠", "description": "Step-by-step walkthroughs, diagrams, and analogies"},
            {"id": "speed_run", "label": "Speed Run", "icon": "⚡", "description": "Concise cheat-sheet style, just the essentials"},
        ],
    }


@router.post("/generate")
async def generate(request: GenerateRequest):
    """Stream a DSA learning guide via Server-Sent Events.

    The response is a text/event-stream that emits events as the
    multi-agent pipeline progresses through planning, writing,
    and code generation phases.

    Args:
        request: The generation request with topics and style.

    Returns:
        A StreamingResponse with SSE content.
    """
    logger.info(
        "Generate request: %d topics, style=%s",
        len(request.topics),
        request.style,
    )

    async def event_stream():
        async for event in generate_guide(request):
            yield event.encode()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/guides")
async def get_all_guides():
    """Retrieve metadata for all generated guides."""
    guides = list_guides()
    return {"guides": guides}


@router.get("/guides/{guide_id}")
async def get_single_guide(guide_id: str):
    """Retrieve a single generated guide by ID."""
    guide = get_guide(guide_id)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide

