import os
import subprocess
import tempfile
from os import path
from sys import platform
from utils.console import print_markdown, print_step, print_substep

ACCEPTABLE_TO_BE_LEFT_BLANK = ["RANDOM_THREAD", "TIMES_TO_RUN"]

def checkforEnv():
	if path.exists(".env") == True:
		return
	else:
		print_markdown("[ERROR] Could not find .env. \n If this is an error, please report it [on GitHub](https://github.com/elebumm/RedditVideoMakerBot/issues).")
		exit()

def envUpdate():

	if path.exists(".env.template"):
		if platform == "win32" or platform == "cygwin":
			runPS("utils/scripts/envValidator.ps1")
			with open(".\\video_creation\\data\\envvars.txt", "rb") as f:
				envTemplate = f.read()
		elif platform == "darwin" or platform == "linux":
			envTemplate = subprocess.check_output(
				"awk -F '=' 'NF {print $1}' .env.template | grep --regexp=^[a-zA-Z]",
				shell=True,
			)
		else:
			raise OSError("[WARN] Could not validate your .env file due to an unsupported platform.")
	else:
		raise FileNotFoundError("[ERROR] Could not find .env.template.")
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
