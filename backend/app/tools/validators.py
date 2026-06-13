"""Custom tools for the Coder agent.

Provides a code validation tool that the Coder agent can call to verify
that generated code snippets are syntactically correct before including
them in the guide.
"""

from __future__ import annotations

import ast
import traceback


async def validate_python_code(code: str) -> str:
    """Validate that a Python code snippet is syntactically correct.

    Attempts to parse the code using Python's AST module. Returns a
    success message or a detailed error description.

    Args:
        code: The Python source code to validate.

    Returns:
        A string indicating whether the code is valid or describing the error.
    """
    try:
        ast.parse(code)
        return "✅ Code is syntactically valid."
    except SyntaxError as e:
        return (
            f"❌ Syntax error at line {e.lineno}, column {e.offset}: {e.msg}\n"
            f"Please fix the code and try again."
        )
    except Exception as e:
        return f"❌ Unexpected error during validation: {traceback.format_exc()}"
