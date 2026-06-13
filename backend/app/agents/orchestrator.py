"""Orchestrator — coordinates the 3-stage agent pipeline.

Runs the Planner, Writer, and Coder agents sequentially, yielding
SSE events at each stage for real-time frontend updates. This is
the core generation engine.

Pipeline:
  Phase 1: Planner → CurriculumOutline (structured JSON)
  Phase 2: Writer  → Streaming Markdown per section
  Phase 3: Coder   → Streaming code examples per section
"""

from __future__ import annotations

import json
import logging
import traceback
from collections.abc import AsyncGenerator

from app.agents.planner import plan_curriculum
from app.agents.writer import write_section
from app.agents.coder import generate_code_examples
from app.db import upsert_guide
from app.schemas.request import GenerateRequest
from app.schemas.response import SSEEvent

logger = logging.getLogger(__name__)


async def generate_guide(request: GenerateRequest) -> AsyncGenerator[SSEEvent, None]:
    """Run the full generation pipeline, yielding SSE events.

    Coordinates three sequential agent phases:
    1. Planner: produces a structured curriculum outline
    2. Writer: streams content for each section
    3. Coder: streams code examples for each section

    Each phase emits progress events, and content/code phases stream
    their output token-by-token.

    Args:
        request: The user's generation request (topics + style).

    Yields:
        SSEEvent instances to be streamed to the frontend.
    """
    try:
        # ── Phase 1: Plan the curriculum ──────────────────────────────
        yield SSEEvent(
            event="progress",
            data=json.dumps({
                "phase": "planning",
                "status": "active",
                "message": "Planning your curriculum...",
            }),
        )

        outline = await plan_curriculum(request)

        # Send the outline to the frontend so it can build the TOC.
        yield SSEEvent(
            event="outline",
            data=outline.model_dump_json(),
        )

        # Progressively save the guide to DB (Initial Outline Phase)
        sections_content = []
        sections_code = []
        guide_id = upsert_guide(
            request_data=request.model_dump(),
            outline=outline.model_dump(),
            sections_content=sections_content,
            sections_code=sections_code,
            guide_id=None,
        )

        yield SSEEvent(
            event="progress",
            data=json.dumps({
                "phase": "planning",
                "status": "complete",
                "message": f"Curriculum planned — {len(outline.sections)} sections",
            }),
        )

        # ── Phase 2: Write content for each section ───────────────────
        sections_content = []
        yield SSEEvent(
            event="progress",
            data=json.dumps({
                "phase": "writing",
                "status": "active",
                "message": "Writing content...",
            }),
        )

        for i, section in enumerate(outline.sections):
            # Signal which section we're writing.
            yield SSEEvent(
                event="section_start",
                data=json.dumps({
                    "index": i,
                    "title": section.title,
                    "topic": section.topic,
                    "type": "content",
                }),
            )

            # Stream the writer's output.
            section_content = []
            async for token in write_section(section, request.style):
                section_content.append(token)
                yield SSEEvent(event="content", data=token)
            
            sections_content.append("".join(section_content))
            
            # Progressively update DB
            upsert_guide(
                request_data=request.model_dump(),
                outline=outline.model_dump(),
                sections_content=sections_content,
                sections_code=sections_code,
                guide_id=guide_id,
            )

            yield SSEEvent(
                event="section_end",
                data=json.dumps({"index": i, "type": "content"}),
            )

        yield SSEEvent(
            event="progress",
            data=json.dumps({
                "phase": "writing",
                "status": "complete",
                "message": "Content written",
            }),
        )

        # ── Phase 3: Generate code examples for each section ──────────
        sections_code = []
        yield SSEEvent(
            event="progress",
            data=json.dumps({
                "phase": "coding",
                "status": "active",
                "message": "Generating code examples...",
            }),
        )

        for i, section in enumerate(outline.sections):
            yield SSEEvent(
                event="section_start",
                data=json.dumps({
                    "index": i,
                    "title": section.title,
                    "topic": section.topic,
                    "type": "code",
                }),
            )

            section_code = []
            async for token in generate_code_examples(section):
                section_code.append(token)
                yield SSEEvent(event="code", data=token)
            
            sections_code.append("".join(section_code))
            
            # Progressively update DB
            upsert_guide(
                request_data=request.model_dump(),
                outline=outline.model_dump(),
                sections_content=sections_content,
                sections_code=sections_code,
                guide_id=guide_id,
            )

            yield SSEEvent(
                event="section_end",
                data=json.dumps({"index": i, "type": "code"}),
            )

        yield SSEEvent(
            event="progress",
            data=json.dumps({
                "phase": "coding",
                "status": "complete",
                "message": "Code examples ready",
            }),
        )

        # ── Done ──────────────────────────────────────────────────────
        yield SSEEvent(
            event="done",
            data=json.dumps({
                "message": "Guide complete!",
                "guide_id": guide_id,
            }),
        )

    except Exception as e:
        logger.exception("Pipeline error: %s", e)
        yield SSEEvent(
            event="error",
            data=json.dumps({
                "message": f"Generation failed: {str(e)}",
                "detail": traceback.format_exc(),
            }),
        )
