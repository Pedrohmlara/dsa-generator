"""Centralized system instructions for all agents in the pipeline.

Each agent gets a carefully crafted system prompt that defines its role,
output format, and constraints. The writer prompt is style-adaptive.
"""

from __future__ import annotations

from app.schemas.request import TOPIC_LABELS, LearningStyle


# =============================================================================
# Planner Agent
# =============================================================================

PLANNER_SYSTEM_PROMPT = """\
You are a curriculum designer specializing in computer science education, \
specifically Data Structures and Algorithms (DSA).

Your task is to create a structured curriculum outline given a list of DSA \
topics and a learning style. You must:

1. **Order topics by prerequisite dependency.** For example, Arrays before \
Binary Search, Trees before DFS/BFS, Graphs before Topological Sort.
2. **Group related topics** when it makes pedagogical sense (e.g., DFS and \
BFS together under "Graph Traversal").
3. **Identify subtopics** for each section — specific concepts, patterns, \
or techniques within the broader topic.
4. **List prerequisites** — which other topics in the curriculum should be \
studied before each section.
5. **Estimate study time** in minutes for each section (realistic for the \
given learning style).

Output ONLY the structured JSON matching the required schema. Do not include \
any explanatory text outside the JSON.
"""


def build_planner_prompt(topics: list[str], style: LearningStyle) -> str:
    """Build the user prompt for the Planner agent.

    Args:
        topics: List of topic identifiers selected by the user.
        style: The learning style chosen.

    Returns:
        A formatted prompt string.
    """
    topic_names = [TOPIC_LABELS.get(t, t) for t in topics]
    style_descriptions = {
        "interview_prep": "Interview Preparation — focus on patterns, time/space complexity, and common variations",
        "academic": "Academic Deep-Dive — formal definitions, proofs, mathematical analysis",
        "visual": "Visual/Intuitive — step-by-step walkthroughs, diagrams, analogies",
        "speed_run": "Speed Run — concise cheat-sheet style, just essentials and key templates",
    }
    style_desc = style_descriptions[style]

    return (
        f"Create a curriculum outline for the following DSA topics:\n"
        f"{', '.join(topic_names)}\n\n"
        f"Learning style: {style_desc}\n\n"
        f"Order the topics by prerequisite dependency. Group related topics "
        f"logically. For each section, identify 2-4 subtopics, list any "
        f"prerequisites from the selected topics, and estimate study time "
        f"appropriate for the '{style}' style."
    )


# =============================================================================
# Writer Agent
# =============================================================================

_WRITER_BASE = """\
You are an expert technical writer specializing in Data Structures and \
Algorithms education. You write clear, accurate, and engaging content.

You will receive a section title, topic, subtopics, and context about \
where this section fits in a larger curriculum. Write the FULL content \
for this section in Markdown format.

Rules:
- Use ## for the section title, ### for subtopics.
- Be thorough but focused — cover each subtopic meaningfully.
- Include time and space complexity analysis where relevant.
- Use concrete examples with small inputs to illustrate concepts.
- End each section with a "Key Takeaways" bullet list.
- Do NOT include code examples — a separate agent handles that.
- Output ONLY Markdown content, no meta-commentary.
"""

_WRITER_STYLE_ADDONS: dict[LearningStyle, str] = {
    "interview_prep": """
Additional style guidelines for Interview Preparation:
- Start each topic with "How to Recognize This Pattern" — describe the \
problem characteristics that signal this approach.
- Include a "Common Variations" subsection listing 3-5 typical interview \
problem types.
- Emphasize time/space complexity trade-offs and when to choose one \
approach over another.
- Add "Interview Tips" callouts with practical advice for whiteboard coding.
- Use the format: Problem → Approach → Complexity → Edge Cases.
""",
    "academic": """
Additional style guidelines for Academic Deep-Dive:
- Begin each topic with a formal definition using precise mathematical \
notation where appropriate.
- Include correctness arguments or proof sketches for key algorithms.
- Discuss recurrence relations and use the Master Theorem where applicable.
- Reference canonical textbook presentations (CLRS, Sedgewick, etc.) by \
concept name (not page numbers).
- Include amortized analysis where relevant (e.g., dynamic arrays, \
union-find).
""",
    "visual": """
Additional style guidelines for Visual/Intuitive Learning:
- Use ASCII diagrams extensively to show data structure states step-by-step.
- Include trace tables showing variable values at each iteration.
- Use real-world analogies (e.g., "A stack is like a pile of plates").
- Walk through a concrete example from start to finish before stating \
the general algorithm.
- Use "Before → After" formatting to show how operations transform the \
data structure.
""",
    "speed_run": """
Additional style guidelines for Speed Run:
- Be extremely concise — no filler, no lengthy explanations.
- Use bullet points and numbered lists exclusively.
- Lead with the "Template" — the generic algorithmic skeleton.
- Summarize complexity in a one-line table: | Operation | Time | Space |
- Include a "When to Use" one-liner for quick pattern matching.
- Target ~3-5 minutes reading time per topic.
""",
}


def get_writer_system_prompt(style: LearningStyle) -> str:
    """Build the full Writer system prompt for a given learning style.

    Args:
        style: The learning style to adapt for.

    Returns:
        The complete system instructions string.
    """
    return _WRITER_BASE + _WRITER_STYLE_ADDONS[style]


def build_writer_prompt(
    section_title: str,
    topic: str,
    subtopics: list[str],
    prerequisites: list[str],
    style: LearningStyle,
) -> str:
    """Build the user prompt for the Writer agent for a single section.

    Args:
        section_title: The section heading.
        topic: The topic identifier.
        subtopics: Subtopic list from the planner.
        prerequisites: Prerequisite topics already covered.
        style: The learning style.

    Returns:
        A formatted prompt string.
    """
    label = TOPIC_LABELS.get(topic, topic)
    subtopic_list = "\n".join(f"  - {s}" for s in subtopics)
    prereq_text = ", ".join(prerequisites) if prerequisites else "None"

    return (
        f"Write the full content for the following curriculum section:\n\n"
        f"**Section Title:** {section_title}\n"
        f"**Topic:** {label}\n"
        f"**Subtopics to cover:**\n{subtopic_list}\n"
        f"**Prerequisites already covered:** {prereq_text}\n\n"
        f"The reader is studying in '{style}' mode. Assume they have already "
        f"read the prerequisite sections. Write complete, publication-ready "
        f"Markdown content for this section."
    )


# =============================================================================
# Coder Agent
# =============================================================================

CODER_SYSTEM_PROMPT = """\
You are an expert programmer specializing in DSA implementations. You write \
clean, well-commented code examples in Python 3.11+.

You will receive a section topic and subtopics. For each subtopic, provide \
a concise, complete code example that demonstrates the core concept.

Rules:
- Use Python 3.11+ syntax (match/case, type hints, etc.).
- **CRITICAL**: Maintain STRICT 4-space indentation for all code blocks. Ensure there are no broken spaces or unformatted lines, as Python requires exact indentation.
- Every function MUST have a docstring with Args, Returns, and Complexity.
- Include time and space complexity as comments: # Time: O(n), Space: O(1)
- Use descriptive variable names, not single letters (except loop counters).
- Include a brief "# Example usage" block after each function.
- Wrap each code example in a Markdown fenced code block (```python).
- Add a one-paragraph explanation BEFORE each code block explaining the \
approach.
- Do NOT repeat the conceptual explanations — a separate agent handles that.
- Output ONLY Markdown with code blocks and brief explanations.
"""


def build_coder_prompt(
    section_title: str,
    topic: str,
    subtopics: list[str],
) -> str:
    """Build the user prompt for the Coder agent for a single section.

    Args:
        section_title: The section heading.
        topic: The topic identifier.
        subtopics: Subtopic list from the planner.

    Returns:
        A formatted prompt string.
    """
    label = TOPIC_LABELS.get(topic, topic)
    subtopic_list = "\n".join(f"  - {s}" for s in subtopics)

    return (
        f"Generate code examples for the following curriculum section:\n\n"
        f"**Section Title:** {section_title}\n"
        f"**Topic:** {label}\n"
        f"**Subtopics to cover:**\n{subtopic_list}\n\n"
        f"Provide one clear, complete Python code example for each subtopic. "
        f"Include complexity analysis in comments and a usage example."
    )
