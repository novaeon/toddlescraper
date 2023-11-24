import os
import subprocess

# Get all environment variables
env_vars = os.environ

# For each environment variable
for name, value in env_vars.items():
    print("GETTING CALENDAR FOR " + name + " PASSWORD IS " + value)
    subprocess.run(["python", "scraper.py", name, value])
