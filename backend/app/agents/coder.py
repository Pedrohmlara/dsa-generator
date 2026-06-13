"""Coder Agent — generates code examples with streaming output.

Streams annotated Python code examples for each section of the
curriculum. Uses a custom validation tool to check syntax.
This is Phase 3 of the generation pipeline.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from google.antigravity import Agent, LocalAgentConfig, GeminiConfig
from google.antigravity.hooks import policy

from app.config import settings
from app.agents.prompts import CODER_SYSTEM_PROMPT, build_coder_prompt
from app.schemas.response import Section
from app.tools.validators import validate_python_code

logger = logging.getLogger(__name__)


async def generate_code_examples(
    section: Section,
) -> AsyncGenerator[str, None]:
    """Stream code examples for a single curriculum section.

    Creates a fresh Coder agent for each section with the
    validate_python_code custom tool available. Streams tokens
    as they arrive.

    Args:
        section: The curriculum section to generate code for.

    Yields:
        String tokens of Markdown content (code blocks + explanations).
    """
    config = LocalAgentConfig(
        system_instructions=CODER_SYSTEM_PROMPT,
        model=settings.model_name,
        tools=[validate_python_code],
        policies=[policy.allow_all()],
    )

    prompt = build_coder_prompt(
        section_title=section.title,
        topic=section.topic,
        subtopics=section.subtopics,
    )

    logger.info("Coder agent: generating code for '%s'", section.title)

    async with Agent(config) as coder:
        response = await coder.chat(prompt)
        async for token in response:
            yield token

    logger.info("Coder agent: completed code for '%s'", section.title)
