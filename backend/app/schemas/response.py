"""Response schemas and structured output models for the agent pipeline."""

from __future__ import annotations

import pydantic


class Section(pydantic.BaseModel):
    """A single section in the curriculum outline.

    Attributes:
        topic: The topic identifier (e.g., "binary_search").
        title: Human-readable section title.
        subtopics: Specific sub-areas to cover within this topic.
        prerequisites: Topics that should be learned before this one.
        estimated_minutes: Estimated study time in minutes.
    """

    topic: str
    title: str
    subtopics: list[str]
    prerequisites: list[str] = pydantic.Field(default_factory=list)
    estimated_minutes: int = 15


class CurriculumOutline(pydantic.BaseModel):
    """Structured output from the Planner agent.

    Represents a complete, ordered curriculum with sections arranged
    by prerequisite dependency.

    Attributes:
        title: Overall guide title.
        description: Brief description of what this guide covers.
        sections: Ordered list of sections to study.
        total_estimated_minutes: Total estimated study time.
    """

    title: str
    description: str
    sections: list[Section]
    total_estimated_minutes: int


class SSEEvent(pydantic.BaseModel):
    """A Server-Sent Event to stream to the frontend.

    Attributes:
        event: Event type (progress, content, done, error).
        data: Event payload.
    """

    event: str
    data: str

    def encode(self) -> str:
        """Encode as SSE wire format."""
        # SSE spec: multi-line data needs each line prefixed with "data: "
        lines = self.data.split("\n")
        data_lines = "\n".join(f"data: {line}" for line in lines)
        return f"event: {self.event}\n{data_lines}\n\n"
