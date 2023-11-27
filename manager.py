import os
import subprocess
import yaml
import json

selenium_env = {}

# Get all environment variables
env_vars = os.environ['ALLSECRETS']

def get_all_keys(data, prefix="", keys_list=None):
    if keys_list is None:
        keys_list = []

    if isinstance(data, dict):
        for key, value in data.items():
            get_all_keys(value, prefix + key + '.', keys_list)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            get_all_keys(item, prefix + str(i) + '.', keys_list)
    else:
        keys_list.append(prefix[:-1])  # Add the key without the trailing dot to the list

    return keys_list

print("PARSED JSON:")
parsed_data = json.loads(env_vars)
jsonkeys = get_all_keys(parsed_data)
print(jsonkeys)

for jsonkey in jsonkeys:
    dict_key = "ISP_" + jsonkey
    dict_value = "${{ secrets." + jsonkey + "}}"
    selenium_env[dict_key]=dict_value

yaml_content = {
    "name": "Run Selenium On GitHub Action",
    "env": selenium_env,
    "on": {
        "workflow_dispatch": {},
        "schedule": [
            {"cron": "*/15 * * * *"}
        ]
    },
    "jobs": {
        "scrape": {
            "runs-on": "ubuntu-latest",
            "timeout-minutes": 15,
            "steps": [
                {"name": "Checking out repo", "uses": "actions/checkout@v3"},
                {"name": "Setting up Python", "uses": "actions/setup-python@v4", "with": {"python-version": "3.9"}},
                {"name": "Installing package list", "run": "apt list --installed"},
                {"name": "Removing previous chrome instances on runner", "run": "sudo apt purge google-chrome-stable"},
                {"name": "Installing all necessary packages", "run": "pip install requests chromedriver-autoinstaller selenium pyvirtualdisplay ics pyshorteners datetime"},
                {"name": "Install xvfb", "run": "sudo apt-get install xvfb"},
                {"name": "Running the Python script", "run": "python manager.py"},
                {
                    "name": "Commit and Push The Results From Python Selenium Action",
                    "run": (
                        "git config --global user.name 'github-actions[bot]'\n"
                        "git config --global user.email '41898282+github-actions[bot]@users.noreply.github.com'\n"
                        "git add -A\n"
                        "git commit -m 'GitHub Actions Results added'\n"
                        "git push"
                    ),
                },
            ],
        },
    },
}

with open(".github/workflows/workflow.yaml", "a") as yaml_file:
    yaml.dump(yaml_content, yaml_file, default_flow_style=False)

# Variables to add to env
# PYTHON_NAME: ${{ secrets.GITHUB_REPO_NAME }}

