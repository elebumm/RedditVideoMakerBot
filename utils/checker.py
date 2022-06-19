import os
import subprocess
import tempfile
from os import path
from sys import platform

ACCEPTABLE_TO_BE_LEFT_BLANK = ["RANDOM_THREAD", "TIMES_TO_RUN"]


def envUpdate():
    if path.exists(".env.template"):  # if .env.template exists and .env does not exist
        if platform == "win32" or platform == "cygwin":
            runPS("utils/scripts/FileGrabber.ps1")
            with open(".\\video_creation\\data\\envvars.txt", "rb") as f:
                envTemplate = f.read()
        elif platform == "darwin" or platform == "linux":
            envTemplate = subprocess.check_output(
                "awk -F '=' 'NF {print $1}' .env.template | grep --regexp=^[a-zA-Z]",
                shell=True,
            )
        else:
            raise OSError("Unsupported platform")
    elif path.exists(".env"):
        if platform == "win32" or platform == "cygwin":
            runPS("utils/scripts/FileGrabberenv.ps1")
            with open(".\\video_creation\\data\\envvars.txt", "rb") as f:
                envTemplate = f.read()
        elif platform == "darwin" or platform == "linux":
            envTemplate = subprocess.check_output(
                "awk -F '=' 'NF {print $1}' .env | grep --regexp=^[a-zA-Z]",
                shell=True,
            )
        else:
            raise OSError("Unsupported platform")
    else:
        raise FileNotFoundError("No .env or .env.template file found")
    tempEnv = tempfile.TemporaryFile()
    tempEnv.write(envTemplate)
    tempEnv.seek(0)
    envVars = tempEnv.readlines()

    missing = []
    isMissingEnvs = False
    for env in envVars:
        try:
            env = env.decode("utf-8").strip()
        except AttributeError:
            env = env.strip()

        if env not in os.environ:
            if str(env) in ACCEPTABLE_TO_BE_LEFT_BLANK:
                continue
            isMissingEnvs = True
            missing.append(env)

    if isMissingEnvs:
        printstr = ""
        [printstr + str(var) for var in missing]
        print(
            f"The following environment variables are missing: {printstr}. Please add them to the .env file."
        )
        exit(-1)


def runPS(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed
