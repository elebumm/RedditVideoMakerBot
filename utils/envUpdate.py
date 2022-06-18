import os
import subprocess
import tempfile
from os import path
import logging

log = logging.getLogger(__name__)


def envUpdate():
    if path.exists(".env.template"):
        envTemplate = subprocess.check_output(
            "awk -F '=' 'NF {print $1}' .env.template | grep --regexp=^[a-zA-Z]",  # noqa
            shell=True,
        )
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