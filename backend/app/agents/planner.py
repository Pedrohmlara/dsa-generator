"""Planner Agent — generates a structured curriculum outline.

Uses the Antigravity SDK's structured output feature (response_schema)
to guarantee a valid CurriculumOutline JSON from the model. This is
Phase 1 of the generation pipeline.
"""

from __future__ import annotations

import json
import logging

from google.antigravity import Agent, LocalAgentConfig, GeminiConfig
from google.antigravity.hooks import policy

from app.config import settings
from app.agents.prompts import PLANNER_SYSTEM_PROMPT, build_planner_prompt
from app.schemas.request import GenerateRequest
from app.schemas.response import CurriculumOutline

logger = logging.getLogger(__name__)


async def plan_curriculum(request: GenerateRequest) -> CurriculumOutline:
    """Run the Planner agent to produce a structured curriculum outline.

    Creates an Antigravity Agent configured with the CurriculumOutline
    as the response_schema, sends the planning prompt, and parses the
    structured JSON output.

    Args:
        request: The user's generation request (topics + style).

    Returns:
        A validated CurriculumOutline instance.

    Raises:
        ValueError: If the planner fails to produce valid structured output.
    """
    config = LocalAgentConfig(
        system_instructions=PLANNER_SYSTEM_PROMPT,
        model=settings.model_name,
        response_schema=CurriculumOutline,
        policies=[policy.allow_all()],
    )

    prompt = build_planner_prompt(request.topics, request.style)
    logger.info("Planner agent: starting with %d topics", len(request.topics))

    async with Agent(config) as planner:
        response = await planner.chat(prompt)
        structured = await response.structured_output()

        if not structured:
            # Fallback: try to parse the text response as JSON.
            text = await response.text()
            logger.warning("Planner: no structured output, attempting text parse")
            try:
                structured = json.loads(text)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Planner agent failed to produce valid output: {e}"
                ) from e

    logger.info(
        "Planner agent: produced %d sections",
        len(structured.get("sections", [])),
    )

    # Validate through Pydantic.
    return CurriculumOutline.model_validate(structured)
