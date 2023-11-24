import os
import subprocess

# Get all environment variables
env_vars = os.environ

# For each environment variable
for name, value in env_vars.items():
    # Call the second Python script with the name and value as arguments
    subprocess.run(["python", "scraper.py", name, value])
    print("getting calendar for " + name)
