#!/usr/bin/env python
import toml
from os.path import exists
from re import match
from typing import Optional, Union, TypeVar, Callable

from utils.console import handle_input, console

function = TypeVar("function", bound=Callable[..., object])

config: Optional[dict] = None
config_name: str = "config.toml"
config_template_name: str = "utils/.config.template.toml"


def crawl(
        obj: dict,
        func: function = lambda x, y: print(x, y),
        path: Optional[list] = None,
) -> None:
    """
    Crawls on values of the dict and executes func if found dict w/ settings

    Args:
        obj: Dict to be crawled on
        func: Function to be executed with settings
        path: List with keys of nested dict
    """
    if not path:
        path = []

    for key, value in obj.items():
        if type(value) is dict and any([type(v) is dict for v in value.values()]):
            crawl(value, func, path + [key])
            continue
        func(path + [key], value)


def check(
        value: any,
        checks: dict,
        name: str,
) -> any:
    """
    Checks values and asks user for input if value is incorrect

    Args:
        value: Values to check
        checks: List of checks as a dict
        name: Name of the value to be checked

    Returns:
        Correct value
    """
    correct = True if value != {} else False

    if correct and "type" in checks:
        try:
            value = eval(checks["type"])(value)
        except Exception:  # noqa (Exception is fine, it's not too broad)
            correct = False

    if (
        correct and "options" in checks and value not in checks["options"]
    ):  # FAILSTATE Value is not one of the options
        correct = False
    if (
        correct
        and "regex" in checks
        and (
            (isinstance(value, str) and match(checks["regex"], value) is None)
            or not isinstance(value, str)
        )
    ):  # FAILSTATE Value doesn't match regex, or has regex but is not a string.
        correct = False

    if (
        correct
        and not hasattr(value, "__iter__")
        and (
            ("nmin" in checks and checks["nmin"] is not None and value < checks["nmin"])
            or ("nmax" in checks and checks["nmax"] is not None and value > checks["nmax"])
        )
    ):
        correct = False
    if (
        correct
        and hasattr(value, "__iter__")
        and (
            ("nmin" in checks and checks["nmin"] is not None and len(value) < checks["nmin"])
            or ("nmax" in checks and checks["nmax"] is not None and len(value) > checks["nmax"])
        )
    ):
        correct = False
    
    if not correct:
        default_values = {
            "explanation": "",
            "var_type": "False",
            "default": NotImplemented,
            "regex": "",
            "input_error": "Incorrect input",
            "nmin": None,  # noqa
            "nmax": None,  # noqa
            "oob_error": "Input out of bounds(Value too high/low/long/short)",
            "options": None,
            "optional": False,
        }

        [checks.update({key: value}) for key, value in default_values.items() if checks.get(key, 'Non') == 'Non']

        value = handle_input(name=name, **checks)
    return value


def nested_get(
        obj: dict,
        keys: list,
) -> any:
    """
    Gets value from nested dict by list with path

    Args:
        obj: Nested dict
        keys: List with path
    Return:
        Value of last key
    """
    for key in keys:
        obj = obj.get(key, {})
    return obj


def nested_set(
        obj: dict,
        keys: list,
        value: any,
) -> None:
    """
    Sets last key in the nested dict by the path

    Args:
        obj: Nested dict
        keys: List with path
        value: Value to set
    """
    for key in keys[:-1]:
        obj = obj.setdefault(key, {})
    obj[keys[-1]] = value


def check_vars(
        path: list,
        checks: dict,
) -> None:
    """
    Checks if there is the value in the dict and it's correct

    Args:
        path: List with path
        checks: Dict with all checks
    """
    global config
    if checks is None:
        checks = dict()

    value = check(
        nested_get(config, path),
        checks,
        name=path[-1],
    )
    nested_set(config, path, value)


def check_config_wrapper(
        func: function,
) -> function:
    """
    Exception wrapper for check_config function
    """

    def wrapper(*args, **kwargs):
        if args:
            kwargs["name"] = args[0]
            if args.__len__() > 1:
                kwargs["template_name"] = args[-1]
        if not kwargs or not all(arg is not None for arg in kwargs.values()):
            kwargs["name"] = config_name
            kwargs["template_name"] = config_template_name

        try:
            return func(*args, **kwargs)
        except toml.TomlDecodeError:
            if console.input(f"[blue]Couldn't read {kwargs['name']}.\nOverwrite it?(y/n)").startswith("y"):
                try:
                    with open(kwargs["name"], "w") as f:
                        f.write("")
                    return func(*args, **kwargs)
                except Exception:  # noqa (Exception is fine, it's not too broad)
                    console.print(
                        f"[red bold]Failed to overwrite {kwargs['name']}. Giving up.\n"
                        f"Suggestion: check {kwargs['name']} permissions for the user."
                    )
                    return False
            console.print("Unable to read config, and not allowed to overwrite it. Giving up.")
            return False
        except Exception as error:
            console.print(f"[red bold]Encountered error when trying to to load {kwargs['template_name']}: {error}")
            return False

    return wrapper


@check_config_wrapper
def check_config(
        name: Optional[str] = None,
        template_name: Optional[str] = None,
) -> Union[dict, bool]:
    """
    Checks config and returns corrected version

    Args:
        name: Config name
        template_name: Template name
    Return:
        Corrected config file as a dict
    """
    if not name:
        name = config_name
    if not template_name:
        template_name = config_template_name

    global config

    if not exists(name):
        console.print(f"[blue]Couldn't find {name}\nCreating it now.")
        try:
            with open(name, "w+") as f:
                f.write("")
            config = dict()
        except Exception:  # noqa (Exception is fine, it's not too broad)
            console.print(
                f"[red bold]Failed to write to {name}.Giving up.\n"
                f"Suggestion: check the folder's permissions for the user."
            )
            return False
    else:
        config = toml.load(config_name)

    template = toml.load(template_name)
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
    with open(config_name, "w") as f:
        toml.dump(config, f)
    return config


if __name__ == "__main__":
    print(check_config())
    # template = toml.load(config_template_name)
    # crawl(template)
