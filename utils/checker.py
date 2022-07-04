#!/usr/bin/env python
import os
from rich.console import Console
from rich.table import Table
from rich import box
import re
import dotenv
from utils.console import handle_input

console = Console()


def check_env() -> bool:
    """Checks to see what's been put in .env

    Returns:
        bool: Whether or not everything was put in properly
    """
    if not os.path.exists(".env.template"):
        console.print("[red]Couldn't find .env.template. Unable to check variables.")
        return True
    if not os.path.exists(".env"):
        console.print("[red]Couldn't find the .env file, creating one now.")
        with open(".env", "x", encoding="utf-8") as file:
            file.write("")
    success = True
    with open(".env.template", "r", encoding="utf-8") as template:
        # req_envs = [env.split("=")[0] for env in template.readlines() if "=" in env]
        matching = {}
        explanations = {}
        bounds = {}
        types = {}
        oob_errors = {}
        examples = {}
        req_envs = []
        var_optional = False
        for line in template.readlines():
            if line.startswith("#") is not True and "=" in line and var_optional is not True:
                req_envs.append(line.split("=")[0])
                if "#" in line:
                    examples[line.split("=")[0]] = "#".join(line.split("#")[1:]).strip()
            elif "#OPTIONAL" in line:
                var_optional = True
            elif line.startswith("#MATCH_REGEX "):
                matching[req_envs[-1]] = line.removeprefix("#MATCH_REGEX ")[:-1]
                var_optional = False
            elif line.startswith("#OOB_ERROR "):
                oob_errors[req_envs[-1]] = line.removeprefix("#OOB_ERROR ")[:-1]
                var_optional = False
            elif line.startswith("#RANGE "):
                bounds[req_envs[-1]] = tuple(
                    map(
                        lambda x: float(x) if x != "None" else None,
                        line.removeprefix("#RANGE ")[:-1].split(":"),
                    )
                )
                var_optional = False
            elif line.startswith("#MATCH_TYPE "):
                types[req_envs[-1]] = eval(line.removeprefix("#MATCH_TYPE ")[:-1].split()[0])
                var_optional = False
            elif line.startswith("#EXPLANATION "):
                explanations[req_envs[-1]] = line.removeprefix("#EXPLANATION ")[:-1]
                var_optional = False
            else:
                var_optional = False
    missing = set()
    incorrect = set()
    dotenv.load_dotenv()
    for env in req_envs:
        value = os.getenv(env)
        if value is None:
            missing.add(env)
            continue
        if env in matching.keys():
            re.match(matching[env], value) is None and incorrect.add(env)
        if env in bounds.keys() and env not in types.keys():
            len(value) >= bounds[env][0] or (
                len(bounds[env]) > 1 and bounds[env][1] >= len(value)
            ) or incorrect.add(env)
            continue
        if env in types.keys():
            try:
                temp = types[env](value)
                if env in bounds.keys():
                    (bounds[env][0] <= temp or incorrect.add(env)) and len(bounds[env]) > 1 and (
                        bounds[env][1] >= temp or incorrect.add(env)
                    )
            except ValueError:
                incorrect.add(env)

    if len(missing):
        table = Table(
            title="Missing variables",
            highlight=True,
            show_lines=True,
            box=box.ROUNDED,
            border_style="#414868",
            header_style="#C0CAF5 bold",
            title_justify="left",
            title_style="#C0CAF5 bold",
        )
        table.add_column("Variable", justify="left", style="#7AA2F7 bold", no_wrap=True)
        table.add_column("Explanation", justify="left", style="#BB9AF7", no_wrap=False)
        table.add_column("Example", justify="center", style="#F7768E", no_wrap=True)
        table.add_column("Min", justify="right", style="#F7768E", no_wrap=True)
        table.add_column("Max", justify="left", style="#F7768E", no_wrap=True)
        for env in missing:
            table.add_row(
                env,
                explanations[env] if env in explanations.keys() else "No explanation given",
                examples[env] if env in examples.keys() else "",
                str(bounds[env][0]) if env in bounds.keys() and bounds[env][1] is not None else "",
                str(bounds[env][1])
                if env in bounds.keys() and len(bounds[env]) > 1 and bounds[env][1] is not None
                else "",
            )
        console.print(table)
        success = False
    if len(incorrect):
        table = Table(
            title="Incorrect variables",
            highlight=True,
            show_lines=True,
            box=box.ROUNDED,
            border_style="#414868",
            header_style="#C0CAF5 bold",
            title_justify="left",
            title_style="#C0CAF5 bold",
        )
        table.add_column("Variable", justify="left", style="#7AA2F7 bold", no_wrap=True)
        table.add_column("Current value", justify="left", style="#F7768E", no_wrap=False)
        table.add_column("Explanation", justify="left", style="#BB9AF7", no_wrap=False)
        table.add_column("Example", justify="center", style="#F7768E", no_wrap=True)
        table.add_column("Min", justify="right", style="#F7768E", no_wrap=True)
        table.add_column("Max", justify="left", style="#F7768E", no_wrap=True)
        for env in incorrect:
            table.add_row(
                env,
                os.getenv(env),
                explanations[env] if env in explanations.keys() else "No explanation given",
                str(types[env].__name__) if env in types.keys() else "str",
                str(bounds[env][0]) if env in bounds.keys() else "None",
                str(bounds[env][1]) if env in bounds.keys() and len(bounds[env]) > 1 else "None",
            )
            missing.add(env)
        console.print(table)
        success = False
    if success is True:
        return True
    console.print(
        "[green]Do you want to automatically overwrite incorrect variables and add the missing variables? (y/n)"
    )
    if not input().casefold().startswith("y"):
        console.print("[red]Aborting: Unresolved missing variables")
        return False
    if len(incorrect):
        with open(".env", "r+", encoding="utf-8") as env_file:
            lines = []
            for line in env_file.readlines():
                line.split("=")[0].strip() not in incorrect and lines.append(line)
            env_file.seek(0)
            env_file.write("\n".join(lines))
            env_file.truncate()
        console.print("[green]Successfully removed incorrectly set variables from .env")
    with open(".env", "a", encoding="utf-8") as env_file:
        for env in missing:
            env_file.write(
                env
                + "="
                + ('"' if env not in types.keys() else "")
                + str(
                    handle_input(
                        "[#F7768E bold]" + env + "[#C0CAF5 bold]=",
                        types[env] if env in types.keys() else False,
                        matching[env] if env in matching.keys() else ".*",
                        explanations[env]
                        if env in explanations.keys()
                        else "Incorrect input. Try again.",
                        bounds[env][0] if env in bounds.keys() else None,
                        bounds[env][1] if env in bounds.keys() and len(bounds[env]) > 1 else None,
                        oob_errors[env] if env in oob_errors.keys() else "Input too long/short.",
                        extra_info="[#C0CAF5 bold]⮶ "
                        + (explanations[env] if env in explanations.keys() else "No info available"),
                    )
                )
                + ('"' if env not in types.keys() else "")
                + "\n"
            )
    return True


if __name__ == "__main__":
    check_env()
