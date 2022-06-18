import os
import subprocess
import tempfile
import logging

from os import path
from sys import platform

log = logging.getLogger(__name__)

def envUpdate():
    if path.exists(".env.template"):
        if platform == "win32" or platform == "cygwin":
            #envTemplate = subprocess.run(
            #    [r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
            #    r'.\envUpdateWin.ps1'],
            #    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            #    shell=True
            #)
            print("Updating is not yet supported on Windows.")
            return
        elif platform == "darwin" or platform == "linux":
            envTemplate = subprocess.check_output(
                "awk -F '=' 'NF {print $1}' .env.template | grep --regexp=^[a-zA-Z]",
                shell=True,
            )
            return
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
            isMissingEnvs = True
            missing.append(env)

    if isMissingEnvs:
        log.error(
            f"[ERROR] The following environment variables are missing: {missing}.)"
        )
        exit(-1)