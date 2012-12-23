import os
import webbrowser
import subprocess
import config
import shutil
from time import sleep

# this is a first run kinda thing.
# if the BASE_DIR does not exist, let's build it, copy the base site templates and then build out a static db.
if os.path.exists(config.BASE_DIR) == False:
	os.mkdir(config.BASE_DIR)
	shutil.copytree(os.path.realpath("templates/site"),os.path.join(config.BASE_DIR,'templates/site'))
	subprocess.call(["python","models.py"],shell=True)

server_proc = subprocess.Popen(["python","server.py","9989"],shell=True)
#we have to give the server some time to boot up.
sleep(1)
webbrowser.open("http://localhost:9989/")

