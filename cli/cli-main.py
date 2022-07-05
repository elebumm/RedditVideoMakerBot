#!/usr/bin/env python
import click
from ...RedditVideoMakerBot.main import process, VERSION

# MAIN Group:
# A group is created here called "main", which will have subcommands.
@click.group()
def main():
  # Since this command will execute nothing, we'll just pass.
  pass

# Command 1:
# We are using a decorator here, which is a "command" decorator, which turns your function into a command.
# Note that the decorator has an argument called "help", this will describe the command when we use "--help" flag
@click.command(help="Create your reddit video.")
def create():
    # By making taking the help of "main.py", we import a function called "process" which does the same if we do "python main.py"
    process()

# Command 2:
# We are using a decorator here, which is a "command" decorator, which turns your function into a command.
@click.command(help="Bot's version")
def version():
    print(VERSION)

# Helper 1:
# This function takes the group, command and the name. After that it adds a command into that group
def command_adder(group: click.Group, cmd: click.Command, name: str):
  # Adding command
  group.add_command(cmd, name)


# MAIN
if __name__ == "__main__":
  # Helper Called 1
  command_adder(main, create, "create")
  # Helper Called 2
  command_adder(main, version, "version")
  # Group Called
  main()