"""Writer Agent — generates section content with streaming output.

Streams Markdown content token-by-token for each section of the
curriculum. Adapts writing style based on the user's learning
preference. This is Phase 2 of the generation pipeline.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from google.antigravity import Agent, LocalAgentConfig, GeminiConfig
from google.antigravity.hooks import policy

from app.config import settings
from app.agents.prompts import get_writer_system_prompt, build_writer_prompt
from app.schemas.request import LearningStyle
from app.schemas.response import Section

logger = logging.getLogger(__name__)


async def write_section(
    section: Section,
    style: LearningStyle,
) -> AsyncGenerator[str, None]:
    """Stream the content for a single curriculum section.

    Creates a fresh Writer agent for each section to keep context
    windows clean and isolated. Streams tokens as they arrive from
    the model.

    Args:
        section: The curriculum section to write content for.
        style: The learning style to adapt the writing for.

    Yields:
        String tokens of Markdown content as they stream from the model.
    """
    system_prompt = get_writer_system_prompt(style)

    config = LocalAgentConfig(
        system_instructions=system_prompt,
        model=settings.model_name,
        policies=[policy.allow_all()],
    )

    prompt = build_writer_prompt(
        section_title=section.title,
        topic=section.topic,
        subtopics=section.subtopics,
        prerequisites=section.prerequisites,
        style=style,
    )

    logger.info("Writer agent: writing section '%s'", section.title)

    async with Agent(config) as writer:
        response = await writer.chat(prompt)
        async for token in response:
            yield token

    logger.info("Writer agent: completed section '%s'", section.title)
