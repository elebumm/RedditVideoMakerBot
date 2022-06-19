#!/usr/bin/env python
import os
from rich.console import Console
import re
import dotenv
from utils.console import handle_input

console = Console()

success = True


def check_env() -> bool:
    if not os.path.exists(".env.template"):
        console.print("[red]Couldn't find .env.template. Unable to check variables.")
        return False
    with open(".env.template", "r") as template:
        # req_envs = [env.split("=")[0] for env in template.readlines() if "=" in env]
        matching = {}
        explanations = {}
        req_envs = []
        var_optional = False
        for line in template.readlines():
            if "=" in line and var_optional is not True:
                req_envs.append(line.split("=")[0])
            elif "#OPTIONAL" in line:
                var_optional = True
            elif line.startswith("#MATCH_REGEX "):
                matching[req_envs[-1]] = line.removeprefix("#MATCH_REGEX ")[:-1]
                var_optional = False
            elif line.startswith("#EXPLANATION "):
                explanations[req_envs[-1]] = line.removeprefix("#EXPLANATION ")[:-1]
                var_optional = False
            else:
                var_optional = False
    missing = []
    incorrect = []
    dotenv.load_dotenv()
    for env in req_envs:
        value = os.getenv(env)
        if value is None:
            missing.append(env)
            continue
        if env in matching.keys():
            env, re.match(matching[env], value) is None and incorrect.append(env)
    if len(missing):
        for i in range(len(missing)):
            try:
                missing[i] = missing[i] + ": " + explanations[missing[i]]
            except KeyError:
                pass
        console.print(
            f"[red]{'These variables are'*(len(missing) > 1) or 'This variable is'} non-optional and missing: \n\n"
            + "\n\n".join(missing)
        )
        success = False
    if len(incorrect):
        console.print(
            f"[red]{'These variables are'*(len(incorrect) > 1) or 'This variable is'} set incorrectly: "
            + "\n".join(incorrect)
        )
        success = False
    # if success is True:
    # return True
    # console.print("[green]Do you want to enter the missing variables by hand(y/n)")
    # if not input().casefold().startswith("y"):
    # console.print("[red]Aborting: Unresolved missing variables")
    # return success
    # with open(".env", "a") as env_file:
    # for env in missing:
    # pass
    return success


if __name__ == "__main__":
    check_env()
