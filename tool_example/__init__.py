"""Tool example package entry point.

Provides a ``main`` function used by the console script defined in
``pyproject.toml``. The command prints a line of text – either the supplied
command‑line arguments joined together or a default message.
"""

import sys

def main() -> None:
    """Entry point for ``my-command``.

    If arguments are provided they are printed; otherwise a default string is
    output. This satisfies the requirement of printing one line of any text.
    """
    if len(sys.argv) > 1:
        print(" ".join(sys.argv[1:]))
    else:
        print("tool-example output")
