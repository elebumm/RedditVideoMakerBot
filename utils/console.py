#!/usr/bin/env python3
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
import re

console = Console()


def print_markdown(text):
    """Prints a rich info message. Support Markdown syntax."""

    md = Padding(Markdown(text), 2)
    console.print(md)


def print_step(text):
    """Prints a rich info message."""

    panel = Panel(Text(text, justify="left"))
    console.print(panel)


def print_substep(text, style=""):
    """Prints a rich info message without the panelling."""
    console.print(text, style=style)


def handle_input(
    message: str = "",
    check_type=False,
    match: str = "",
    err_message: str = "",
    nmin=None,
    nmax=None,
    oob_error="",
):
    match = re.compile(match + "$")
    while True:
        user_input = input(message + "\n> ").strip()
        if re.match(match, user_input) is not None:
            if check_type is not False:
                try:
                    user_input = check_type(user_input)
                    if nmin is not None and user_input < nmin:
                        console.print("[red]" + oob_error)  # Input too low failstate
                        continue
                    if nmax is not None and user_input > nmax:
                        console.print("[red]" + oob_error)  # Input too high
                        continue
                    break  # Successful type conversion and number in bounds
                except ValueError:
                    console.print("[red]" + err_message)  # Type conversion failed
                    continue
            if nmin is not None and len(user_input) < nmin:  # Check if string is long enough
                console.print("[red]" + oob_error)
                continue
            if nmax is not None and len(user_input) > nmax:  # Check if string is not too long
                console.print("[red]" + oob_error)
                continue
            break
        console.print("[red]" + err_message)

    return user_input
