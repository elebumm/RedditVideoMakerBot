import re
from typing import Tuple, Dict
from pathlib import Path
import toml
from rich.console import Console

from utils.console import handle_input

console = Console()
config = dict  # autocomplete


def crawl(obj: dict, func=lambda x, y: print(x, y, end="\n"), path=None):
    if path is None:  # path Default argument value is mutable
        path = []
    for key in obj.keys():
        if type(obj[key]) is dict:
            crawl(obj[key], func, path + [key])
            continue
        func(path + [key], obj[key])


def check(value, checks, name):
    def get_check_value(key, default_result):
        return checks[key] if key in checks else default_result

    incorrect = False
    if value == {}:
        incorrect = True
    if not incorrect and "type" in checks:
        try:
            value = eval(checks["type"])(value)
        except:
            incorrect = True

    if (
        not incorrect and "options" in checks and value not in checks["options"]
    ):  # FAILSTATE Value is not one of the options
        incorrect = True
    if (
        not incorrect
        and "regex" in checks
        and (
            (isinstance(value, str) and re.match(checks["regex"], value) is None)
            or not isinstance(value, str)
        )
    ):  # FAILSTATE Value doesn't match regex, or has regex but is not a string.
        incorrect = True

    if (
        not incorrect
        and not hasattr(value, "__iter__")
        and (
            ("nmin" in checks and checks["nmin"] is not None and value < checks["nmin"])
            or ("nmax" in checks and checks["nmax"] is not None and value > checks["nmax"])
        )
    ):
        incorrect = True
    if (
        not incorrect
        and hasattr(value, "__iter__")
        and (
            ("nmin" in checks and checks["nmin"] is not None and len(value) < checks["nmin"])
            or ("nmax" in checks and checks["nmax"] is not None and len(value) > checks["nmax"])
        )
    ):
        incorrect = True

    if incorrect:
        value = handle_input(
            message=(
                (("[blue]Example: " + str(checks["example"]) + "\n") if "example" in checks else "")
                + "[red]"
                + ("Non-optional ", "Optional ")["optional" in checks and checks["optional"] is True]
            )
            + "[#C0CAF5 bold]"
            + str(name)
            + "[#F7768E bold]=",
            extra_info=get_check_value("explanation", ""),
            check_type=eval(get_check_value("type", "False")),
            default=get_check_value("default", NotImplemented),
            match=get_check_value("regex", ""),
            err_message=get_check_value("input_error", "Incorrect input"),
            nmin=get_check_value("nmin", None),
            nmax=get_check_value("nmax", None),
            oob_error=get_check_value(
                "oob_error", "Input out of bounds(Value too high/low/long/short)"
            ),
            options=get_check_value("options", None),
            optional=get_check_value("optional", False),
        )
    return value


def crawl_and_check(obj: dict, path: list, checks: dict = {}, name=""):
    if len(path) == 0:
        return check(obj, checks, name)
    if path[0] not in obj.keys():
        obj[path[0]] = {}
    obj[path[0]] = crawl_and_check(obj[path[0]], path[1:], checks, path[0])
    return obj


def check_vars(path, checks):
    global config
    crawl_and_check(config, path, checks)


def check_toml(template_file, config_file) -> Tuple[bool, Dict]:
    global config
    config = None
    try:
        template = toml.load(template_file)
    except Exception as error:
        console.print(f"[red bold]Encountered error when trying to to load {template_file}: {error}")
        return False
    try:
        config = toml.load(config_file)
    except toml.TomlDecodeError:
        console.print(
            f"""[blue]Couldn't read {config_file}.
Overwrite it?(y/n)"""
        )
        if not input().startswith("y"):
            print("Unable to read config, and not allowed to overwrite it. Giving up.")
            return False
        else:
            try:
                with open(config_file, "w") as f:
                    f.write("")
            except:
                console.print(
                    f"[red bold]Failed to overwrite {config_file}. Giving up.\nSuggestion: check {config_file} permissions for the user."
                )
                return False
    except FileNotFoundError:
        console.print(
            f"""[blue]Couldn't find {config_file}
Creating it now."""
        )
        try:
            with open(config_file, "x") as f:
                f.write("")
            config = {}
        except:
            console.print(
                f"[red bold]Failed to write to {config_file}. Giving up.\nSuggestion: check the folder's permissions for the user."
            )
            return False

    console.print(
        """\
[blue bold]###############################
#                             #
# Checking TOML configuration #
#                             #
###############################
If you see any prompts, that means that you have unset/incorrectly set variables, please input the correct values.\
"""
    )
    crawl(template, check_vars)
    with open(config_file, "w") as f:
        toml.dump(config, f)
    return config


if __name__ == "__main__":
    directory = Path().absolute()
    check_toml(f"{directory}/utils/.config.template.toml", "config.toml")
