#!/usr/bin/env python3
from rich.console import Console
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from typing import Optional, Union
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


def print_table(items):
    """Prints items in a table."""

    console.print(Columns([Panel(f"[yellow]{item}", expand=True) for item in items]))


def print_substep(text, style=""):
    """Prints a rich info message without the panelling."""
    console.print(text, style=style)


def handle_input(
        *,
        var_type: Union[str, bool] = False,
        regex: str = "",
        input_error: str = "",
        nmin: Optional[int] = None,  # noqa
        nmax: Optional[int] = None,  # noqa
        oob_error: str = "",
        explanation: str = "",
        options: list = None,
        default: Optional[str] = NotImplemented,
        optional: bool = False,
        example: Optional[str] = None,
        name: str = "",
        message: Optional[Union[str, float]] = None,
):
    if not message:
        message = (
                (("[blue]Example: " + str(example) + "\n") if example else "")
                + "[red]"
                + ("Non-optional ", "Optional ")[optional]
                + "[#C0CAF5 bold]"
                + str(name)
                + "[#F7768E bold]="
        )
    var_type: any = eval(var_type) if var_type else var_type

    if optional:
        console.print(message + "\n[green]This is an optional value. Do you want to skip it? (y/n)")
        if input().casefold().startswith("y"):
            return default if default is not NotImplemented else ""
    if default is not NotImplemented:
        console.print(
            "[green]"
            + message
            + '\n[blue bold]The default value is "'
            + str(default)
            + '"\nDo you want to use it?(y/n)'
        )
        if input().casefold().startswith("y"):
            return default
    if options is None:
        regex = re.compile(regex)
        console.print("[green bold]" + explanation, no_wrap=True)
        while True:
            console.print(message, end="")
            user_input = input("").strip()
            if var_type is not False:
                try:
                    user_input = var_type(user_input)
                    if (nmin is not None and user_input < nmin) or (
                            nmax is not None and user_input > nmax
                    ):
                        # FAILSTATE Input out of bounds
                        console.print("[red]" + oob_error)
                        continue
                    break  # Successful type conversion and number in bounds
                except ValueError:
                    # Type conversion failed
                    console.print("[red]" + input_error)
                    continue
            elif regex != "" and re.match(regex, user_input) is None:
                console.print("[red]" + input_error + "\nAre you absolutely sure it's correct?(y/n)")
                if input().casefold().startswith("y"):
                    break
                continue
            else:
                # FAILSTATE Input STRING out of bounds
                if (nmin is not None and len(user_input) < nmin) or (
                        nmax is not None and len(user_input) > nmax
                ):
                    console.print("[red bold]" + oob_error)
                    continue
                break  # SUCCESS Input STRING in bounds
        return user_input
    console.print(explanation, no_wrap=True)
    while True:
        console.print(message, end="")
        user_input = input("").strip()
        if var_type is not False:
            try:
                isinstance(eval(user_input), var_type)
                return var_type(user_input)
            except Exception:  # noqa (Exception is fine, it's not too broad)
                console.print(
                    "[red bold]"
                    + input_error
                    + "\nValid options are: "
                    + ", ".join(map(str, options))
                    + "."
                )
                continue
        if user_input in options:
            return user_input
        console.print(
            "[red bold]" + input_error + "\nValid options are: " + ", ".join(map(str, options)) + "."
        )
